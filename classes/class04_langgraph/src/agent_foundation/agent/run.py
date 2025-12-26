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
    out = app.invoke(AgentState(user_text=args.text.strip()))
    issue_type = out["issue_type"] if isinstance(out, dict) else out.issue_type
    router_score = out["router_score"] if isinstance(out, dict) else out.router_score
    kb_query = out["kb_query"] if isinstance(out, dict) else out.kb_query
    hits = out["kb_hits"] if isinstance(out, dict) else out.kb_hits
    action = out["action"] if isinstance(out, dict) else out.action
    ticket = out.get("ticket") if isinstance(out, dict) else out.ticket
    final_text = out["final_text"] if isinstance(out, dict) else out.final_text

    print(f"[Router] issue_type={issue_type} score={router_score:.3f}")
    print(f"[Query] kb_query={kb_query}")
    print(f"[KB] hits={len(hits)} action={action}")
    if ticket:
        print(f"[Ticket] id={ticket.get('ticket_id')} priority={ticket.get('priority')}")
    print(final_text)


if __name__ == "__main__":
    main()
