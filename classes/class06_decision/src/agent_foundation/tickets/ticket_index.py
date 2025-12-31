from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from agent_foundation.tickets.ticket_store import load_tickets


INDEX_DIR = Path("logs/ticket_faiss")


def _to_docs(tickets: List[Dict[str, Any]]) -> List[Document]:
    docs: List[Document] = []
    for t in tickets:
        # 검색 대상 텍스트: title + description
        content = f"{t.get('title','')}\n\n{t.get('description','')}".strip()
        meta = {
            "ticket_id": t.get("ticket_id"),
            "priority": t.get("priority"),
            "created_at": t.get("created_at"),
            "title": t.get("title"),
        }
        docs.append(Document(page_content=content, metadata=meta))
    return docs


def build_ticket_index() -> Optional[FAISS]:
    tickets = load_tickets()
    if not tickets:
        return None
    docs = _to_docs(tickets)
    embeddings = OpenAIEmbeddings()
    vs = FAISS.from_documents(docs, embeddings)
    vs.save_local(str(INDEX_DIR))
    return vs


def load_ticket_index() -> Optional[FAISS]:
    embeddings = OpenAIEmbeddings()
    if INDEX_DIR.exists():
        return FAISS.load_local(str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True)
    return build_ticket_index()


def find_similar_ticket(
    query: str,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    vs = load_ticket_index()
    if vs is None:
        return []
    results = vs.similarity_search_with_score(query, k=top_k)

    hits: List[Dict[str, Any]] = []
    for doc, score in results:
        hits.append(
            {
                "ticket_id": doc.metadata.get("ticket_id"),
                "title": doc.metadata.get("title"),
                "score": float(score),  # distance(낮을수록 유사)
            }
        )
    return hits


def rebuild_ticket_index() -> None:
    # 티켓 저장 후 인덱스를 재생성(간단 버전)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    build_ticket_index()
