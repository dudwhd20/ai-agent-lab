from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


TICKETS_PATH = Path("logs/tickets.jsonl")


def append_ticket(ticket: Dict[str, Any]) -> None:
    TICKETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = dict(ticket)
    record.setdefault("ts", int(time.time()))
    with TICKETS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_tickets(limit: int = 500) -> List[Dict[str, Any]]:
    if not TICKETS_PATH.exists():
        return []
    lines = TICKETS_PATH.read_text(encoding="utf-8").splitlines()
    # 최신 우선으로 일부만 로드(가볍게)
    lines = lines[-limit:]
    out: List[Dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        out.append(json.loads(line))
    return out
