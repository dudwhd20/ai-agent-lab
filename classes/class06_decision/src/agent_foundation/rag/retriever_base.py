from __future__ import annotations

from typing import Any, Dict, List, Protocol


class Retriever(Protocol):
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        ...
