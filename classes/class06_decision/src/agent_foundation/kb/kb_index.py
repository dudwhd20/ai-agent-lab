from __future__ import annotations

import json
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


KB_PATH = Path("data/kb.jsonl")
INDEX_DIR = Path("data/faiss_index")


def load_kb() -> List[Document]:
    docs: List[Document] = []
    for line in KB_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        content = f"{obj['title']}\n\n{obj['text']}"
        meta = {"id": obj["id"], "title": obj["title"]}
        docs.append(Document(page_content=content, metadata=meta))
    return docs


def build_faiss() -> FAISS:
    docs = load_kb()
    embeddings = OpenAIEmbeddings()
    vs = FAISS.from_documents(docs, embeddings)
    vs.save_local(str(INDEX_DIR))
    return vs


def load_faiss() -> FAISS:
    embeddings = OpenAIEmbeddings()
    if INDEX_DIR.exists():
        return FAISS.load_local(str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True)
    return build_faiss()
