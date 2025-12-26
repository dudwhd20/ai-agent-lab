from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    user_text: str

    issue_type: str = "unknown"
    router_score: float = 0.0
    kb_query: str = ""

    kb_hits: List[Dict[str, str]] = Field(default_factory=list)
    action: str = ""  # guided | ticket_created
    ticket: Optional[Dict[str, Any]] = None
    final_text: str = ""
