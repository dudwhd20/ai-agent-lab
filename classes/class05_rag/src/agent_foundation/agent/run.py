import argparse

from dotenv import load_dotenv
from agent_foundation.agent.rag_agent import build_agent


def main():
    load_dotenv() 
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    args = parser.parse_args()

    llm, kb_tool, prompt = build_agent()

    hits = kb_tool.run({"query": args.text, "top_k": 3})

    # ✅ 관측 로그
    print(f"[RAG] query={args.text}")
    print(f"[RAG] hits={len(hits)}")
    for i, h in enumerate(hits, start=1):
        print(f"[RAG] top{i} id={h['id']} title={h['title']} score={h['score']:.4f}")

    if hits:
        kb_text = "\n".join(
            [f"- {h['id']} {h['title']} (score={h['score']:.4f}): {h['content']}" for h in hits]
        )
    else:
        kb_text = "없음"

    final_prompt = prompt.format(input=args.text) + f"\n\nKB 검색 결과:\n{kb_text}"
    response = llm.invoke(final_prompt)
    print(response.content)


if __name__ == "__main__":
    main()
