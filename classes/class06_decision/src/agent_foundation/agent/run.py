from __future__ import annotations

import argparse

from dotenv import load_dotenv
from agent_foundation.agent.graph import build_graph
from agent_foundation.agent.state import AgentState


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="사용자 입력")
    args = parser.parse_args()

    app = build_graph()
    raw = app.invoke(AgentState(user_text=args.text))

    # ✅ dict → AgentState로 복구
    out = AgentState(**raw)

    # ✅ 관측 로그
    print(f"[RAG] query={out.kb_query}")
    print(f"[RAG] hits={len(out.kb_hits)} best_score={out.best_score}")
    print(f"[Decision] confidence={out.confidence} action={out.action}")

    if out.kb_hits:
        for i, h in enumerate(out.kb_hits, start=1):
            print(f"[RAG] top{i} id={h['id']} title={h['title']} score={h['score']:.4f}")

    print(out.final_text)


if __name__ == "__main__":
    main()
