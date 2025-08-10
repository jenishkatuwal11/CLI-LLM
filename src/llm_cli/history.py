from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

Message = Dict[str, Any]
DEFAULT_DIR = Path.home() / ".llm_cli"
DEFAULT_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class HistoryStore:
    path: Path = field(default=DEFAULT_DIR / "history.jsonl")

    def append(self, record: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def load_session(self, session_id: str) -> List[Message]:
        if not self.path.exists():
            return []
        out: List[Message] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get("session_id") == session_id:
                        out.extend(rec.get("messages", []))
                except json.JSONDecodeError:
                    continue
        return out
