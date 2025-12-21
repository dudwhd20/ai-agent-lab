from __future__ import annotations

import os
from tabnanny import verbose
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from agent_foundation.tools.search_kb import SearchKBTool
from agent_foundation.tools.create_ticket import CreateTicketTool
from agent_foundation.agent.callbacks import AuditCallbackHandler


SYSTEM_INSTRUCTIONS = """\
너는 사내 헬프데스크 업무를 처리하는 에이전트다.

규칙:
1) 먼저 search_kb로 근거 문서를 찾아라.
2) 문서로 해결이 가능하면: 근거 문서 id/title을 인용하고 해결 절차를 안내하라.
3) 문서가 없더라도: 1차 점검 가이드를 2~3개 안내하라.
4) 점검으로 해결이 불가/불명확하면: create_ticket을 호출해 티켓을 생성하라.
5) 최종 응답에는 반드시 아래 섹션을 포함하라.
- 근거(KB Hits): [...]
- 1차 점검 가이드:
  1) ...
  2) ...
- 조치(Action Taken): guided | ticket_created
- 결과(Result): ...
"""

def build_agent(log_path: str = "logs/sample_run.jsonl"):
    load_dotenv()

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    llm = ChatOpenAI(model=model)

    tools = [SearchKBTool(), CreateTicketTool()]
    audit = AuditCallbackHandler(log_path=log_path)

    agent = create_agent(
        llm,
        tools,
        system_prompt=SYSTEM_INSTRUCTIONS,
    )    

    # config는 지금 단계에서는 최소만
    cfg = {"callbacks": [audit]}

    return agent, cfg, SYSTEM_INSTRUCTIONS
