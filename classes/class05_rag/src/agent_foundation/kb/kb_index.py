from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from .kb_data import KB_DOCS

INDEX_PATH = "./.faiss_index"


def build_or_load_index():
    embeddings = OpenAIEmbeddings()

    try:
        return FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    except Exception:
        docs = [
            Document(
                page_content=doc["content"],
                metadata={"id": doc["id"], "title": doc["title"]},
            )
            for doc in KB_DOCS
        ]
        db = FAISS.from_documents(docs, embeddings)
        db.save_local(INDEX_PATH)
        return db
