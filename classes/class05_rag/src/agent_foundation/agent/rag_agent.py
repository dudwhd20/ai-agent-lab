from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from agent_foundation.tools.search_kb import SearchKBTool


SYSTEM_PROMPT = """
너는 사내 헬프데스크 지원 에이전트다.

규칙:
1) search_kb 결과가 있으면, 반드시 해당 문서를 근거로 안내한다.
2) 근거 없는 추측은 하지 않는다.
3) KB가 없으면 1차 점검 가이드를 간단히 안내한다.

응답 형식:
- 근거(KB Hits): [...]
- 1차 점검 가이드: ...
- 조치(Action Taken): guided
- 결과(Result): ...
"""


def build_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    tool = SearchKBTool()

    prompt = PromptTemplate.from_template(
        SYSTEM_PROMPT + "\n\n사용자 요청: {input}"
    )

    return llm, tool, prompt
