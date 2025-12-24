from __future__ import annotations


def prompt_guided(user_text: str, hits) -> str:
    return f"""너는 헬프데스크 1차 응대 담당이다.
아래 KB Hits만 근거로 답하라. 추측/일반론 금지.

출력 형식:
- 근거(KB Hits): [id - title, ...]
- 1차 점검 가이드:
  1) ...
  2) ...
  3) ...
- 조치(Action Taken): guided
- 결과(Result): 한 줄

[User]
{user_text}

[KB Hits]
{hits}
"""


def prompt_ticket_created(user_text: str, ticket: dict) -> str:
    return f"""너는 헬프데스크 1차 응대 담당이다.
KB에서 근거를 찾지 못해 티켓이 생성되었다. 아래 티켓 정보를 사용자에게 안내하라.

출력 형식:
- 근거(KB Hits): []
- 조치(Action Taken): ticket_created
- 결과(Result): 티켓 번호 포함, 한 줄

[User]
{user_text}

[Ticket]
{ticket}
"""
