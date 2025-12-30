from __future__ import annotations
from typing import Any, Dict, List, Optional


def _format_hits(hits: List[Dict[str, Any]]) -> str:
    if not hits:
        return "[]"
    parts = []
    for h in hits:
        parts.append(f"- {h['id']} - {h['title']} (score={h['score']:.4f})")
    return "\n".join(parts)


def prompt_guided(user_text: str, hits: List[Dict[str, Any]]) -> str:
    return f"""\
너는 헬프데스크 에이전트다.
반드시 아래 KB 근거만 사용해서 안내하고, 모르는 건 추측하지 마라.

사용자 요청: {user_text}

근거(KB Hits):
{_format_hits(hits)}

요구 응답 형식:
- 근거(KB Hits): [...]
- 1차 점검 가이드: (3개 이내, 구체적)
- 조치(Action Taken): guided
- 결과(Result): ...
""".strip()


def prompt_ask(user_text: str, hits: List[Dict[str, Any]]) -> str:
    return f"""\
너는 헬프데스크 에이전트다.
KB가 애매하게 매칭됐다. 사용자에게 확인 질문 2개만 하고,
가능하면 KB를 참고해서 질문을 더 정확하게 만들어라.

사용자 요청: {user_text}

참고 후보(KB Hits):
{_format_hits(hits)}

요구 응답 형식:
- 근거(KB Hits): [...]
- 확인 질문: (딱 2개)
- 조치(Action Taken): asked
- 결과(Result): 추가 정보 요청
""".strip()


def prompt_ticket(user_text: str, ticket: Optional[Dict[str, Any]]) -> str:
    tid = (ticket or {}).get("ticket_id", "TCK-UNKNOWN")
    return f"""\
너는 헬프데스크 에이전트다.
KB로 해결 불가이므로 티켓 생성 결과를 안내하라.

사용자 요청: {user_text}
생성된 티켓: {tid}

요구 응답 형식:
- 근거(KB Hits): []
- 조치(Action Taken): ticket_created
- 결과(Result): 티켓 {tid} 생성 안내 + 추가로 필요한 정보 1개 요청
""".strip()
