from __future__ import annotations

import re
from typing import List, Dict, Set, Tuple

KB_DATA: List[Dict[str, str]] = [
    {"id": "KB-001", "title": "VPN 접속 불가 대응", "snippet": "WPA3-Enterprise 환경에서는 자격 증명/인증서/네트워크를 순서대로 점검한다."},
    {"id": "KB-010", "title": "카카오톡 알림 미수신 점검", "snippet": "OS 알림 권한, 방해금지 모드, 앱 내 알림 설정을 순서대로 확인한다."},
    {"id": "KB-011", "title": "안드로이드 배터리 최적화로 인한 알림 지연", "snippet": "배터리 최적화 예외 앱 등록 및 백그라운드 제한 해제."},
    {"id": "KB-012", "title": "iOS 집중모드/알림 요약으로 인한 알림 누락", "snippet": "집중모드/알림 요약 설정 확인 및 카카오톡 알림 허용 점검."},
]

_EN_STOPWORDS = {
    "i", "am", "is", "are", "was", "were", "be", "been", "being",
    "a", "an", "the", "to", "of", "in", "on", "at", "for", "from",
    "and", "or", "but", "do", "does", "did", "can", "could", "should", "would",
    "it", "this", "that", "these", "those", "my", "your", "his", "her", "their",
    "we", "you", "they", "me", "him", "them",
}

def _normalize_text(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^0-9a-zA-Z가-힣\s]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _tokenize(s: str) -> List[str]:
    s = _normalize_text(s)
    raw = [t for t in s.split() if t]

    tokens: List[str] = []
    for t in raw:
        if re.fullmatch(r"[a-z]+", t) and len(t) < 3:
            continue
        if re.search(r"[가-힣]", t) and len(t) < 2:
            continue
        if t in _EN_STOPWORDS:
            continue
        tokens.append(t)
    return tokens

def _to_set(tokens: List[str]) -> Set[str]:
    return set(tokens)


class SearchKBTool:
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        q_tokens = _to_set(_tokenize(query))
        if not q_tokens:
            return []

        scored: List[Tuple[int, Dict[str, str]]] = []

        for doc in KB_DATA:
            title_tokens = _to_set(_tokenize(doc["title"]))
            snippet_tokens = _to_set(_tokenize(doc["snippet"]))

            title_hits = q_tokens & title_tokens
            snippet_hits = q_tokens & snippet_tokens

            # ✅ 가중치: title 매칭은 더 중요
            score = (len(title_hits) * 2) + (len(snippet_hits) * 1)

            # ✅ 임계치: 최소 점수 2 이상만 인정
            # (title에서 1개만 맞아도 score=2라 hit 가능)
            if score >= 2:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:top_k]]
