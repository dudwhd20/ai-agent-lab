from __future__ import annotations

import re


# 아주 가벼운 한국어/영어 공통 정규화
_STOPWORDS = {
    "좀", "제발", "갑자기", "계속", "자꾸", "어떻게", "해요", "되나요", "됩니다", "안돼요", "안됨",
    "the", "a", "an", "to", "of", "and", "or", "is", "are", "am", "can", "could", "please",
    "help", "me", "i", "you", "it", "this", "that",
}

# 이슈 키워드(필요시 계속 추가)
_KEYWORDS = [
    "vpn", "dns", "카카오톡", "알림", "인증", "오류", "접속", "끊김", "지연", "로그인", "집중모드",
]


def normalize_query(user_text: str) -> str:
    """
    규칙 기반 쿼리 정규화:
    - 원문을 기본으로 하되, 너무 길면 토큰을 줄이고 핵심 키워드 위주로 축약
    - 영문은 소문자 기준
    - 최종적으로 원문과의 괴리가 크면 원문으로 롤백은 graph에서 수행
    """
    original = (user_text or "").strip()
    if not original:
        return ""

    # 문자 정리 (특수문자 최소화)
    cleaned = re.sub(r"[^\w\s가-힣\-]+", " ", original, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    lower = cleaned.lower()

    # 키워드가 포함된 경우 가산
    found_keywords = [k for k in _KEYWORDS if k.lower() in lower]

    # 단어 단위로 stopword 제거
    tokens = []
    for t in lower.split():
        if t in _STOPWORDS:
            continue
        # 너무 짧은 토큰 제거
        if len(t) <= 1:
            continue
        tokens.append(t)

    # 키워드가 있으면 키워드를 앞쪽에 배치
    # (키워드 + 나머지 토큰 일부) 형태
    merged = []
    for k in found_keywords:
        if k.lower() not in merged:
            merged.append(k.lower())

    for t in tokens:
        if t not in merged:
            merged.append(t)

    # 너무 길면 앞에서부터 8토큰만
    merged = merged[:8]

    # 결과가 너무 비면 원문 축약만
    if not merged:
        return cleaned[:80]

    return " ".join(merged)


def should_fallback_to_original(user_text: str, candidate_query: str) -> bool:
    """
    탈선 방지용 롤백 판정:
    - candidate_query가 원문과 지나치게 무관하면 원문으로 되돌림
    (간단한 포함/키워드 기반 휴리스틱)
    """
    original = (user_text or "").strip().lower()
    q = (candidate_query or "").strip().lower()

    if not q:
        return True

    # 원문이 매우 짧으면 굳이 바꾸지 않기
    if len(original) <= 12:
        return True

    # query가 원문에 포함되면 안전
    if q in original:
        return False

    # 공통 토큰이 너무 적으면 탈선 가능성
    o_tokens = set(original.split())
    q_tokens = set(q.split())
    if not q_tokens:
        return True

    overlap = len(o_tokens & q_tokens)
    ratio = overlap / max(1, len(q_tokens))

    # q 토큰의 40% 미만이 원문과 겹치면 롤백
    return ratio < 0.4
