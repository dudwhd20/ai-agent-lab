from typing import Any, List, Dict, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

from agent_foundation.kb.kb_index import build_or_load_index


class SearchKBInput(BaseModel):
    query: str = Field(..., description="사용자 원문 또는 정규화된 질의")
    top_k: int = Field(3, ge=1, le=5)


class SearchKBTool(BaseTool):
    name: str = "search_kb"
    description: str = (
        "헬프데스크 티켓을 생성한다. 반환은 ticket_id, created_at, priority를 포함한다."
    )
    args_schema: Type[BaseModel] = SearchKBInput

    def _run(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        db = build_or_load_index()
        results = db.similarity_search_with_score(query, k=top_k)
        
        hits: List[Dict[str, Any]] = []
        for doc, score in results:
            hits.append(
                {
                    "id": doc.metadata.get("id"),
                    "title": doc.metadata.get("title"),
                    "score": float(score),
                    "content": doc.page_content,
                }
            )
        return hits
