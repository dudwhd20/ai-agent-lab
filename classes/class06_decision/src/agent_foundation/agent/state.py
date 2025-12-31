from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    user_text: str

    kb_query: str = ""
    kb_query_source: str = "original"  # original | normalized | fallback
    kb_hits: List[Dict[str, Any]] = Field(default_factory=list)

    best_score: Optional[float] = None
    confidence: str = "unknown"  # high | mid | low

    action: str = ""  # guided | asked | ticket_created
    ticket: Optional[Dict[str, Any]] = None

    final_text: str = ""
