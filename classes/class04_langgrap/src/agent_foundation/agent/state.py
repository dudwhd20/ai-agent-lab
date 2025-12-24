from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    user_text: str
    kb_query: str = ""
    kb_hits: List[Dict[str, str]] = Field(default_factory=list)

    action: str = ""  # guided | ticket_created
    ticket: Optional[Dict[str, Any]] = None
    final_text: str = ""
