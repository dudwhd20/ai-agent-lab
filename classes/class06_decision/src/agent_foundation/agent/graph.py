from __future__ import annotations

import os
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from agent_foundation.agent.state import AgentState
from agent_foundation.agent.prompts import prompt_guided, prompt_ask, prompt_ticket
from agent_foundation.rag.faiss_retriever import FaissRetriever
from agent_foundation.tools.create_ticket import CreateTicketTool
from agent_foundation.agent.query_normalize import normalize_query, should_fallback_to_original
from agent_foundation.agent.clarify import build_clarifying_questions


# ✅ distance 기준(낮을수록 유사) 가정
HIGH_MAX = float(os.getenv("RAG_HIGH_MAX", "0.35"))
MID_MAX = float(os.getenv("RAG_MID_MAX", "0.65"))


def build_graph():
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), temperature=0)
    retriever = FaissRetriever()
    tickets = CreateTicketTool()

    def rag_search(state: AgentState) -> AgentState:
        state.kb_query = state.user_text
        state.kb_hits = retriever.search(state.kb_query, top_k=3)
        if state.kb_hits:
            state.best_score = float(state.kb_hits[0]["score"])
        else:
            state.best_score = None
        return state

    def evaluate(state: AgentState) -> AgentState:
        if not state.kb_hits or state.best_score is None:
            state.confidence = "low"
            return state

        s = state.best_score
        if s <= HIGH_MAX:
            state.confidence = "high"
        elif s <= MID_MAX:
            state.confidence = "mid"
        else:
            state.confidence = "low"
        return state

    def route(state: AgentState) -> str:
        return state.confidence  # high | mid | low

    def compose_guided(state: AgentState) -> AgentState:
        msg = llm.invoke(prompt_guided(state.user_text, state.kb_hits))
        state.final_text = msg.content
        state.action = "guided"
        return state

    def ask(state: AgentState) -> AgentState:
        qs = build_clarifying_questions(state.user_text, state.kb_hits)

        # out.final_text는 “포맷된 고정 텍스트”로 만든다 (LLM 호출 없음)
        # 이유: 질문 품질을 시스템이 통제하기 위함
        hits_repr = []
        for h in state.kb_hits:
            hits_repr.append(f"{h['id']} - {h['title']}")
        hits_str = "[" + ", ".join(hits_repr) + "]" if hits_repr else "[]"

        state.final_text = (
            f"- 근거(KB Hits): {hits_str}\n"
            f"- 확인 질문:\n"
            f"  1) {qs[0]}\n"
            f"  2) {qs[1]}\n"
            f"- 조치(Action Taken): asked\n"
            f"- 결과(Result): 추가 정보 요청"
        )
        state.action = "asked"
        return state

    def create_ticket(state: AgentState) -> AgentState:
        state.ticket = tickets.create(
            title=f"헬프데스크 요청: {state.user_text[:30]}",
            description=state.user_text,
            priority="P3",
        )
        return state

    def compose_ticket(state: AgentState) -> AgentState:
        msg = llm.invoke(prompt_ticket(state.user_text, state.ticket))
        state.final_text = msg.content
        state.action = "ticket_created"
        return state

    def query_normalize(state: AgentState) -> AgentState:
        candidate = normalize_query(state.user_text)

        if should_fallback_to_original(state.user_text, candidate):
            state.kb_query = state.user_text
            state.kb_query_source = "fallback"
        else:
            state.kb_query = candidate
            state.kb_query_source = "normalized"
        return state

    g = StateGraph(AgentState)
    g.add_node("rag_search", rag_search)
    g.add_node("evaluate", evaluate)
    g.add_node("compose_guided", compose_guided)
    g.add_node("ask", ask)
    g.add_node("create_ticket", create_ticket)
    g.add_node("compose_ticket", compose_ticket)

    g.add_node("query_normalize", query_normalize)
    g.set_entry_point("query_normalize")
    g.add_edge("query_normalize", "rag_search")
    g.add_edge("rag_search", "evaluate")

    g.add_conditional_edges(
        "evaluate",
        route,
        {"high": "compose_guided", "mid": "ask", "low": "create_ticket"},
    )
    g.add_edge("compose_guided", END)
    g.add_edge("ask", END)
    g.add_edge("create_ticket", "compose_ticket")
    g.add_edge("compose_ticket", END)

    return g.compile()
