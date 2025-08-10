from __future__ import annotations

import sys, uuid
from typing import List, Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

from .config import ChatOptions, ClientSettings
from .history import HistoryStore
from .router import RouterClient

app = typer.Typer(no_args_is_help=True, help="CLI for OpenAI-compatible LLM routers")
console = Console()

def _load_settings(verbose_flag: bool) -> ClientSettings:
    settings = ClientSettings()
    if verbose_flag:
        settings.verbose = True
    if settings.verbose:
        console.print(f"[dim]Base URL:[/] {settings.base_url or '(not set)'}")
        if settings.default_model:
            console.print(f"[dim]Default model:[/] {settings.default_model}")
    return settings

@app.command()
def models(verbose: bool = typer.Option(False, "--verbose", "-v")):
    settings = _load_settings(verbose)
    client = RouterClient(settings)
    try:
        items = client.list_models()
        if not items:
            console.print("[yellow]No models returned (router may not expose /models).[/]")
            raise typer.Exit(0)
        console.print("[bold]Available models:[/]")
        for m in items:
            console.print(f"- {m}")
    finally:
        client.close()

@app.command()
def chat(
    prompt: Optional[str] = typer.Argument(None, help="Single-turn prompt. Omit for interactive mode."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model ID"),
    system: Optional[str] = typer.Option(None, "--system", help="Optional system prompt"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Max tokens"),
    temperature: float = typer.Option(0.7, "--temp", help="Sampling temperature"),
    no_stream: bool = typer.Option(False, "--no-stream", help="Disable streaming"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Start a multi-turn REPL"),
    session: Optional[str] = typer.Option(None, "--session", help="Session id for saving/loading history"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
):
    settings = _load_settings(verbose)
    client = RouterClient(settings)
    store = HistoryStore()

    try:
        session_id = session or str(uuid.uuid4())
        messages: List[dict] = store.load_session(session_id)

        if interactive and prompt:
            messages.append({"role": "user", "content": prompt})
            _run_once(client, store, session_id, messages, model, system, max_tokens, temperature, not no_stream)

        if interactive or prompt is None:
            console.print(f"[dim]Interactive chat (session {session_id}). Ctrl+C to exit.[/]")
            while True:
                try:
                    user = typer.prompt("[bold cyan]You[/]")
                except (KeyboardInterrupt, EOFError):
                    console.print("\n[dim]Bye![/]")
                    break
                if not user.strip():
                    continue
                messages.append({"role": "user", "content": user})
                _run_once(client, store, session_id, messages, model, system, max_tokens, temperature, not no_stream)
        else:
            messages.append({"role": "user", "content": prompt})
            _run_once(client, store, session_id, messages, model, system, max_tokens, temperature, not no_stream)
    finally:
        client.close()

def _run_once(
    client: RouterClient,
    store: HistoryStore,
    session_id: str,
    messages: List[dict],
    model: Optional[str],
    system: Optional[str],
    max_tokens: Optional[int],
    temperature: float,
    stream: bool,
) -> None:
    opts = ChatOptions(
        model=model,
        stream=stream,
        max_tokens=max_tokens,
        temperature=temperature,
        system_prompt=system,
    )
    final_text, token_stream = client.chat(messages=messages, opts=opts)

    if stream:
        console.print("[bold magenta]Assistant[/]: ", end="")
        acc: List[str] = []
        try:
            for tok in token_stream:
                acc.append(tok)
                console.print(tok, end="", soft_wrap=True)
                sys.stdout.flush()
        except KeyboardInterrupt:
            console.print("\n[dim]-- interrupted --[/]")
        text = "".join(acc).strip()
        console.print()
    else:
        text = (final_text or "").strip()
        console.print("[bold magenta]Assistant[/]:")
        if text:
            console.print(Markdown(text))
        else:
            console.print("[yellow]Empty response[/]")

    if messages and messages[-1]["role"] == "user":
        user_msg = messages[-1]
    else:
        user_msg = {"role": "user", "content": ""}
    ai_msg = {"role": "assistant", "content": text}

    store.append({"session_id": session_id, "messages": [user_msg, ai_msg]})
    messages.append(ai_msg)
