from __future__ import annotations

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from agent_foundation.tools.search_kb import SearchKBTool
from agent_foundation.tools.create_ticket import CreateTicketTool
from agent_foundation.agent.callbacks import AuditCallbackHandler


SYSTEM_INSTRUCTIONS = """\
너는 사내 헬프데스크 1차 응대 담당 에이전트다.

[업무 원칙]
1. 사용자의 문제를 바로 티켓으로 넘기지 않는다.
2. 먼저 사내 KB(search_kb)를 1회 조회한다.
3. KB 결과가 있으면, 해당 내용을 기반으로 1차 점검 가이드를 제공한다.
4. KB 결과가 없더라도, 아래 기준에 따라 반드시 1차 점검 가이드를 먼저 제공한다.
5. 1차 점검 가이드를 제공한 뒤에만 티켓 생성(create_ticket)을 고려한다.

[1차 점검 가이드 규칙]
- 점검 가이드는 2~3개 항목으로 간결하게 제시한다.
- 사용자가 바로 확인할 수 있는 항목 위주로 작성한다.
- 추측이나 모호한 표현을 사용하지 않는다.

[티켓 생성 규칙]
- 아래 조건을 모두 만족할 때만 create_ticket을 호출한다.
  1) KB 결과가 없거나, 점검 가이드로 해결되지 않을 가능성이 높을 때
  2) 사용자 문제가 시스템/계정/서버 측 이슈일 가능성이 있을 때

[Tool 입력 규칙]
- search_kb 호출 시 original_user_text에는 사용자 입력을 그대로 넣는다(변형/요약 금지).
- query에는 original_user_text에 실제로 포함된 단어만 사용한다.

[최종 응답 형식]
- 근거(KB Hits): [...]
- 1차 점검 가이드:
  1) ...
  2) ...
- 조치(Action Taken): guided | ticket_created
- 결과(Result): ...
"""

def build_agent(log_path: str = "logs/sample_run.jsonl"):
    load_dotenv()

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model_name)

    tools = [SearchKBTool(), CreateTicketTool()]
    audit = AuditCallbackHandler(log_path=log_path)

    # ✅ 핵심: positional은 (model, tools)까지만
    # ✅ system 지시는 system_prompt로
    agent = create_agent(
        llm,
        tools,
        system_prompt=SYSTEM_INSTRUCTIONS,
    )

    cfg = {"callbacks": [audit]}
    return agent, cfg
