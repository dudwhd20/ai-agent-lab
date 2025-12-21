from __future__ import annotations

from typing import List, Dict, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


class SearchKBInput(BaseModel):
    original_user_text: str = Field(..., min_length=2, max_length=500, description="사용자 입력 원문(변형 금지)")
    query: str = Field(..., min_length=2, max_length=200, description="검색 질의어")
    top_k: int = Field(3, ge=1, le=10, description="최대 반환 문서 수")


class SearchKBTool(BaseTool):
    name: str = "search_kb"
    description: str = (
        "사내 KB(FAQ/가이드) 검색. "
        "반드시 original_user_text(원문)를 함께 전달해야 하며, "
        "query는 원문에 포함된 단어로 작성한다. "
        "원문과 무관한 이슈로 query를 변조하지 않는다."
    )
    args_schema: Type[BaseModel] = SearchKBInput

    # 데모용 in-memory KB
    _KB: List[Dict[str, str]] = [
        {"id": "KB-001", "title": "VPN 접속 불가 대응", "snippet": "WPA3-Enterprise 환경에서는 ..."},
        {"id": "KB-002", "title": "사내 DNS 이슈 점검", "snippet": "nslookup으로 레코드 확인 후 ..."},
        {"id": "KB-003", "title": "IIS + WebSocket 프록시 설정", "snippet": "ARR, WebSocket Protocol 활성화 ..."},
    ]

    def _run(self, original_user_text: str, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        original = (original_user_text or "").strip().lower()
        q = (query or "").strip().lower()

        # ✅ query가 원문에 없으면 원문 기반으로 fallback (탈선 방지)
        if q and q not in original:
            q = original

        hits = [doc for doc in self._KB if q in (doc["title"] + " " + doc["snippet"]).lower()]
        return hits[:top_k]
