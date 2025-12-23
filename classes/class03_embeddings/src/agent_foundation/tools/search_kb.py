from __future__ import annotations

from typing import List, Dict, Type, ClassVar
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
    _KB: ClassVar[List[Dict[str, str]]] = [
        {"id": "KB-001", "title": "VPN 접속 불가 대응", "snippet": "WPA3-Enterprise 환경에서는 ..."},
        {"id": "KB-002", "title": "사내 DNS 이슈 점검", "snippet": "nslookup으로 레코드 확인 후 ..."},
        {"id": "KB-003", "title": "IIS + WebSocket 프록시 설정", "snippet": "ARR, WebSocket Protocol 활성화 ..."},

        {"id": "KB-010", "title": "카카오톡 알림 미수신 점검", "snippet": "OS 알림 권한, 방해금지 모드, 앱 내 알림 설정을 순서대로 확인한다."},
        {"id": "KB-011", "title": "안드로이드 배터리 최적화로 인한 알림 지연", "snippet": "배터리 최적화(절전) 예외 앱 등록 및 백그라운드 제한 해제 방법."},
        {"id": "KB-012", "title": "iOS 알림 요약/집중모드로 인한 알림 누락", "snippet": "집중모드/알림 요약 설정 확인 및 카카오톡 알림 허용 점검."},

    ]

    def _run(self, original_user_text: str, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        q = (query or "").strip().lower()

        # ✅ Class03-b: router/query_builder가 만든 query를 신뢰한다.
        # original_user_text 기반 fallback은 사용하지 않는다.

        hits = []
        tokens = [t for t in q.split() if t]

        for doc in type(self)._KB:
            hay = (doc["title"] + " " + doc["snippet"]).lower()
            score = sum(1 for t in tokens if t in hay) if tokens else (1 if q in hay else 0)
            if score > 0:
                hits.append((score, doc))

        hits.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in hits[:top_k]]
