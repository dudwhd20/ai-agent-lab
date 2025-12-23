from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import math

from langchain_openai import OpenAIEmbeddings

from agent_foundation.agent.issue_types import IssueType


@dataclass(frozen=True)
class RouteResult:
    issue: IssueType
    score: float


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class EmbeddingRouter:
    """
    Semantic routing (max-sim):
    - IssueType별 프로토타입 문장들을 모두 임베딩해 두고
    - 입력 문장과 각 프로토타입의 cosine similarity 중 "최댓값"으로 분류한다.
    - centroid 평균보다 짧은 프로토타입 세트에서 훨씬 안정적이다.
    """

    def __init__(
        self,
        prototypes: Dict[IssueType, List[str]],
        threshold: float = 0.72,
        model: str = "text-embedding-3-small",
    ):
        self.emb = OpenAIEmbeddings(model=model)
        self.threshold = threshold
        self.prototypes = prototypes

        # ✅ 각 issue의 프로토타입 벡터들을 전부 보관
        self._proto_vecs: Dict[IssueType, List[List[float]]] = {}
        for issue, texts in prototypes.items():
            if not texts:
                self._proto_vecs[issue] = []
                continue
            self._proto_vecs[issue] = self.emb.embed_documents(texts)

    def route(self, user_text: str) -> RouteResult:
        v = self.emb.embed_query(user_text)

        best_issue = IssueType.UNKNOWN
        best_score = 0.0

        for issue, vecs in self._proto_vecs.items():
            for pv in vecs:
                s = _cosine(v, pv)
                if s > best_score:
                    best_score = s
                    best_issue = issue

        if best_score < self.threshold:
            return RouteResult(issue=IssueType.UNKNOWN, score=best_score)

        return RouteResult(issue=best_issue, score=best_score)
