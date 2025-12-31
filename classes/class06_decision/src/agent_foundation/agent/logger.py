from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


def append_jsonl(path: str, record: Dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_decision_log(
    *,
    session_id: str,
    user_text: str,
    kb_query: str,
    kb_hits: list[dict[str, Any]],
    best_score: Optional[float],
    confidence: str,
    action: str,
    ticket: Optional[dict[str, Any]],
) -> Dict[str, Any]:
    # 로그 크기 제한: hit는 상위 3개만, snippet은 짧게
    slim_hits = []
    for h in (kb_hits or [])[:3]:
        slim_hits.append(
            {
                "id": h.get("id"),
                "title": h.get("title"),
                "score": h.get("score"),
            }
        )

    return {
        "ts": int(time.time()),
        "session_id": session_id,
        "user_text": user_text,
        "kb_query": kb_query,
        "hits_count": len(kb_hits or []),
        "top_hits": slim_hits,
        "best_score": best_score,
        "confidence": confidence,
        "action": action,
        "ticket_id": (ticket or {}).get("ticket_id"),
    }
