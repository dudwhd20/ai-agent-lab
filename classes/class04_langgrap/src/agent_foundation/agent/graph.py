from __future__ import annotations

import os
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from agent_foundation.agent.state import AgentState
from agent_foundation.agent.prompts import prompt_guided, prompt_ticket_created
from agent_foundation.tools.search_kb import SearchKBTool
from agent_foundation.tools.create_ticket import CreateTicketTool


def build_graph():
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    kb = SearchKBTool()
    tickets = CreateTicketTool()

    def make_query(state: AgentState) -> AgentState:
        state.kb_query = state.user_text  # Class04-A: 원문 그대로
        return state

    def kb_search(state: AgentState) -> AgentState:
        state.kb_hits = kb.search(state.kb_query, top_k=3)
        return state

    def decide_next(state: AgentState) -> str:
        return "compose_guided" if state.kb_hits else "create_ticket"

    def compose_guided(state: AgentState) -> AgentState:
        msg = llm.invoke([{"role": "user", "content": prompt_guided(state.user_text, state.kb_hits)}])
        state.final_text = msg.content # type: ignore
        state.action = "guided"
        return state

    def create_ticket(state: AgentState) -> AgentState:
        state.ticket = tickets.create(
            title=f"헬프데스크 요청: {state.user_text[:30]}",
            description=state.user_text,
            priority="P3",
        )
        return state

    def compose_ticket(state: AgentState) -> AgentState:
        msg = llm.invoke([{"role": "user", "content": prompt_ticket_created(state.user_text, state.ticket)}])
        state.final_text = msg.content # type: ignore
        state.action = "ticket_created"
        return state

    g = StateGraph(AgentState)
    g.add_node("make_query", make_query)
    g.add_node("kb_search", kb_search)
    g.add_node("compose_guided", compose_guided)
    g.add_node("create_ticket", create_ticket)
    g.add_node("compose_ticket", compose_ticket)

    g.set_entry_point("make_query")
    g.add_edge("make_query", "kb_search")
    g.add_conditional_edges(
        "kb_search",
        decide_next,
        {"compose_guided": "compose_guided", "create_ticket": "create_ticket"},
    )
    g.add_edge("compose_guided", END)
    g.add_edge("create_ticket", "compose_ticket")
    g.add_edge("compose_ticket", END)

    return g.compile()
