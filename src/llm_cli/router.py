from __future__ import annotations

import json, time
from typing import Dict, Generator, Iterable, List, Optional, Tuple

import httpx
from rich.console import Console

from .config import ChatOptions, ClientSettings

console = Console()

class RouterClient:
    def __init__(self, settings: ClientSettings):
        self.settings = settings
        self.settings.ensure_valid()
        self._client = httpx.Client(
            base_url=self.settings.base_url.rstrip("/"),
            timeout=httpx.Timeout(
                connect=self.settings.connect_timeout,
                read=self.settings.read_timeout,
                write=self.settings.read_timeout,
                pool=self.settings.connect_timeout,
            ),
            headers=self._build_headers(),
        )

    def _build_headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.settings.api_key:
            h["Authorization"] = f"Bearer {self.settings.api_key}"
        if self.settings.http_referer:
            h["HTTP-Referer"] = self.settings.http_referer
        if self.settings.x_title:
            h["X-Title"] = self.settings.x_title
        return h

    def list_models(self) -> List[str]:
        try:
            resp = self._client.get("/models")
            resp.raise_for_status()
            payload = resp.json()
        except Exception as e:
            raise RuntimeError(f"Failed to list models: {e}") from e
        data = payload.get("data") or []
        models: List[str] = []
        for item in data:
            if isinstance(item, dict) and "id" in item:
                models.append(item["id"])
            elif isinstance(item, str):
                models.append(item)
        return sorted(set(models))

    def chat(self, messages: List[Dict[str, str]], opts: ChatOptions) -> Tuple[Optional[str], Iterable[str]]:
        model = opts.model or self.settings.default_model
        if not model:
            raise ValueError("No model specified. Pass --model or set LLM_DEFAULT_MODEL.")
        body: Dict = {"model": model, "messages": messages, "temperature": opts.temperature}
        if opts.max_tokens is not None:
            body["max_tokens"] = opts.max_tokens
        if opts.system_prompt:
            body["messages"] = [{"role": "system", "content": opts.system_prompt}] + messages
        for attempt in range(4):
            try:
                if opts.stream:
                    return None, self._stream_chat(body)
                else:
                    txt = self._non_stream_chat(body)
                    return txt, []
            except (httpx.HTTPError, json.JSONDecodeError) as e:
                if attempt == 3:
                    raise
                sleep = 1.5 * (2**attempt)
                console.print(f"[yellow]Transient error: {e}. Retrying in {sleep:.1f}s...[/]")
                time.sleep(sleep)
        return None, []

    def _non_stream_chat(self, body: Dict) -> str:
        resp = self._client.post("/chat/completions", json=body)
        resp.raise_for_status()
        payload = resp.json()
        try:
            return payload["choices"][0]["message"]["content"] or ""
        except Exception:
            choice = payload.get("choices", [{}])[0]
            if "text" in choice:
                return choice["text"]
            return ""

    def _stream_chat(self, body: Dict) -> Generator[str, None, None]:
        with self._client.stream("POST", "/chat/completions", json={**body, "stream": True}) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                if isinstance(line, bytes):
                    line = line.decode("utf-8", errors="ignore")
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta", {})
                    token = delta.get("content")
                    if token:
                        yield token
                except Exception:
                    try:
                        token = json.loads(data).get("choices", [{}])[0].get("text")
                        if token:
                            yield token
                    except Exception:
                        continue

    def close(self) -> None:
        self._client.close()
