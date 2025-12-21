from __future__ import annotations

import time
import uuid
from typing import Dict, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool


class CreateTicketInput(BaseModel):
    title: str = Field(..., min_length=3, max_length=120, description="티켓 제목")
    description: str = Field(..., min_length=5, max_length=4000, description="티켓 상세 내용")
    priority: str = Field("P3", description="우선순위", pattern="^(P1|P2|P3|P4)$")


class CreateTicketTool(BaseTool):
    name: str = "create_ticket"
    description: str = (
        "헬프데스크 티켓을 생성한다. 반환은 ticket_id, created_at, priority를 포함한다."
    )
    args_schema: Type[BaseModel] = CreateTicketInput

    def _run(self, title: str, description: str, priority: str = "P3") -> Dict[str, str]:
        # 데모: 실제론 ServiceNow/Jira/사내 ITSM API 호출로 교체
        ticket_id = f"TCK-{uuid.uuid4().hex[:8].upper()}"
        created_at = int(time.time())
        return {"ticket_id": ticket_id, "created_at": str(created_at), "priority": priority}
