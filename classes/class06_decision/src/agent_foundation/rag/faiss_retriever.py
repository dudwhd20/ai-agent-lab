from __future__ import annotations

from typing import Any, Dict, List, Tuple
from agent_foundation.kb.kb_index import load_faiss


class FaissRetriever:
    def __init__(self) -> None:
        self.vs = load_faiss()

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        results: List[Tuple[Any, float]] = self.vs.similarity_search_with_score(query, k=top_k)
        hits: List[Dict[str, Any]] = []
        for doc, score in results:
            hits.append(
                {
                    "id": doc.metadata.get("id"),
                    "title": doc.metadata.get("title"),
                    "score": float(score),
                    "snippet": doc.page_content[:200].replace("\n", " "),
                }
            )
        return hits
