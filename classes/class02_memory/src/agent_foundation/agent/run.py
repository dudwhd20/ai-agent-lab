from __future__ import annotations

import argparse
from typing import Any, Dict

from langchain_core.messages import AIMessage

from agent_foundation.agent.react_agent import build_agent
from agent_foundation.agent.memory_store import FileMemoryStore, SessionState


def _extract_final_content(result: Dict[str, Any]) -> str:
    """agent.invoke() 결과에서 최종 사용자 응답(마지막 AIMessage.content)을 뽑는다."""
    messages = result.get("messages", [])
    for m in reversed(messages):
        if isinstance(m, AIMessage) and m.content:
            return m.content
    return str(result)


def _extract_action_and_ticket(final_text: str) -> tuple[str, str]:
    """
    아주 단순 파서 (Class02용).
    - Action Taken 라인에서 guided/ticket_created 추출
    - 텍스트에 포함된 TCK-xxxxxxx 형태를 대충 추출
    """
    action = ""
    ticket_id = ""

    for line in final_text.splitlines():
        if "조치(Action Taken)" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                action = parts[-1].strip()

        if "TCK-" in line:
            idx = line.find("TCK-")
            # TCK- + 8자리(데모 가정). 형식 다르면 Class03에서 정교화.
            ticket_id = line[idx : idx + 12].strip()

    return action, ticket_id


def _render_repeat_response(state: SessionState, user_text: str) -> str:
    """
    반복 요청 감지 시 LLM 호출을 스킵하고 고정 템플릿으로 응답한다.
    (Class02 목표: Memory가 실제로 행동을 바꾸는 걸 눈으로 확인)
    """
    last_ticket = state.last_ticket_id or "없음"

    return f"""이미 같은 요청을 이전에 처리한 이력이 있어요.

- 이전 요청: {state.last_user_text}
- 이전 조치: {state.last_action}
- 이전 티켓: {last_ticket}

추가 확인만 몇 가지만 부탁드릴게요(답 주시면 다음 액션을 정리해서 이어갈게요).
1) 기기/OS: (예: Android / iPhone / Windows)
2) 알림이 '아예' 안 오는지, '가끔'만 누락되는지
3) 특정 시간대/네트워크(Wi-Fi/데이터/회사망)에서만 재현되는지

- 근거(KB Hits): []
- 1차 점검 가이드: (이전 안내 참고)
- 조치(Action Taken): guided
- 결과(Result): 반복 요청으로 판단되어 추가 확인 질문으로 전환"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="사용자 입력")
    parser.add_argument("--session", default="local", help="세션 ID(기본: local)")
    args = parser.parse_args()

    user_text = args.text
    session_id = args.session

    store = FileMemoryStore()
    state = store.load(session_id)

    # ----------------------------
    # ✅ Class02 핵심: 반복 요청이면 LLM 호출 자체를 스킵
    # ----------------------------
    if FileMemoryStore.is_same_issue(state.last_user_text, user_text) and state.last_action == "guided":
        out = _render_repeat_response(state, user_text)
        print(out)

        # 상태 유지/갱신(필요 최소)
        store.save(
            SessionState(
                session_id=session_id,
                last_user_text=user_text,
                last_action="guided",
                last_ticket_id=state.last_ticket_id,
            )
        )
        return

    # ----------------------------
    # LLM 호출 경로
    # ----------------------------
    agent, cfg, system = build_agent()

    # (선택) 반복이지만 guided가 아닌 경우(예: ticket_created)는 힌트만 주입
    memory_hint = ""
    if FileMemoryStore.is_same_issue(state.last_user_text, user_text) and state.last_action:
        memory_hint = f"""
[Memory Hint]
- 같은 요청을 이전에 처리한 이력이 있음
- 마지막 사용자 요청: {state.last_user_text}
- 마지막 조치: {state.last_action}
- 마지막 티켓: {state.last_ticket_id or "없음"}

요청이 반복된 경우:
- 이미 안내한 점검을 길게 반복하지 말고,
- 사용자에게 '이전에 처리 이력'을 짧게 언급하고,
- 추가로 필요한 확인 질문(기기/OS/증상/시간대 등) 1~2개만 하라.
""".strip()

    final_input = "\n\n".join([system, memory_hint, f"사용자 요청: {user_text}"]).strip()
    result = agent.invoke({"input": final_input}, config=cfg)

    final_text = _extract_final_content(result)
    print(final_text)

    # 실행 결과를 Memory에 저장
    action, ticket_id = _extract_action_and_ticket(final_text)
    store.save(
        SessionState(
            session_id=session_id,
            last_user_text=user_text,
            last_action=action,
            last_ticket_id=ticket_id,
        )
    )


if __name__ == "__main__":
    main()
