from __future__ import annotations

import argparse

from dotenv import load_dotenv

from agent_foundation.agent.graph import build_graph
from agent_foundation.agent.state import AgentState
from agent_foundation.agent.logger import append_jsonl, build_decision_log


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="사용자 입력")
    parser.add_argument("--session", default="local", help="세션 ID(기본: local)")
    parser.add_argument("--log", default="logs/decision.jsonl", help="로그 파일 경로(JSONL)")
    args = parser.parse_args()

    app = build_graph()

    raw = app.invoke(AgentState(user_text=args.text))

    # LangGraph 결과는 dict로 나오므로 State로 복구
    out = AgentState(**raw)

    # ---- 콘솔 관측 로그 ----
    print(f"[RAG] query={out.kb_query}")
    print(f"[RAG] hits={len(out.kb_hits)} best_score={out.best_score}")
    print(f"[Decision] confidence={out.confidence} action={out.action}")

    if out.kb_hits:
        for i, h in enumerate(out.kb_hits, start=1):
            print(f"[RAG] top{i} id={h['id']} title={h['title']} score={h['score']:.4f}")

    print(out.final_text)
    print(f"[RAG] query={out.kb_query} source={out.kb_query_source}")

    # ---- 파일(jsonl) 로그 ----
    record = build_decision_log(
        session_id=args.session,
        user_text=out.user_text,
        kb_query=out.kb_query,
        kb_hits=out.kb_hits,
        best_score=out.best_score,
        confidence=out.confidence,
        action=out.action,
        ticket=out.ticket,
    )
    append_jsonl(args.log, record)


if __name__ == "__main__":
    main()
