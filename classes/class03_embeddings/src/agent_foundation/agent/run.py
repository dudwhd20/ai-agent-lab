from __future__ import annotations

import argparse
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from agent_foundation.agent.issue_types import IssueType
from agent_foundation.agent.prototypes import PROTOTYPES
from agent_foundation.agent.embedding_router import EmbeddingRouter
from agent_foundation.agent.kb_query_builder import build_kb_query
from agent_foundation.agent.prompts import system_prompt
from agent_foundation.tools.search_kb import SearchKBTool


def main():
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="사용자 입력")
    args = parser.parse_args()
    user_text = args.text.strip()

    # 1) Semantic routing
    router = EmbeddingRouter(PROTOTYPES, threshold=float(os.getenv("ROUTE_THRESHOLD", "0.75")))
    route = router.route(user_text)
    issue: IssueType = route.issue

    # 2) KB query 고정 생성
    kb_query = build_kb_query(issue, user_text)

    # 3) KB 검색 (코드 호출)
    kb_tool = SearchKBTool()
    hits = kb_tool._run(
        original_user_text=user_text,
        query=kb_query,
        top_k=3,
    )

    # ✅ 관측 로그
    print(f"[Router] issue_type={issue.value} score={route.score:.3f}")
    print(f"[KB] query={kb_query}")
    print(f"[KB] hits={len(hits)}")

    # 4) LLM은 최종 답변만
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    llm = ChatOpenAI(model=model)

    sys = system_prompt(issue, has_hits=bool(hits))

    payload = f"""[User]
{user_text}

[KB Query]
{kb_query}

[KB Hits]
{hits}
"""

    msg = llm.invoke(
        [
            {"role": "system", "content": sys},
            {"role": "user", "content": payload},
        ]
    )

    print(msg.content)


if __name__ == "__main__":
    main()
