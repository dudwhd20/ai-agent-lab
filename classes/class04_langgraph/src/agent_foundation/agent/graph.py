from __future__ import annotations

import os
import re
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from agent_foundation.agent.state import AgentState
from agent_foundation.agent.prompts import prompt_guided, prompt_ticket_created
from agent_foundation.tools.search_kb import SearchKBTool
from agent_foundation.tools.create_ticket import CreateTicketTool


def _simple_router(text: str) -> tuple[str, float]:
    """룰 기반 라우터: issue_type과 score를 반환 (score는 신뢰도 느낌용)."""
    t = (text or "").lower()

    # 한국어/영어 키워드 혼합 대응
    vpn = ["vpn", "접속", "인증", "끊", "로그인", "tunnel"]
    kakao = ["카카오", "kakao", "알림", "notification", "푸시", "push"]
    dns = ["dns", "nslookup", "도메인", "해석", "resolve"]
    iis = ["iis", "websocket", "프록시", "arr", "reverse proxy"]

    def score_for(keys: list[str]) -> int:
        return sum(1 for k in keys if k in t)

    scores = {
        "vpn": score_for(vpn),
        "kakao": score_for(kakao),
        "dns": score_for(dns),
        "iis": score_for(iis),
    }

    best_type = max(scores, key=lambda k: scores[k])
    best_score = scores[best_type]

    if best_score == 0:
        return "unknown", 0.0

    # 단순 스코어 정규화(0~1 느낌)
    return best_type, min(1.0, 0.6 + 0.2 * best_score)


def _query_builder(issue_type: str, user_text: str) -> str:
    """
    KB에 있는 '제목' 스타일로 쿼리를 만드는 단계.
    - user_text 그대로 넣지 않고, KB 제목에 가까운 대표 문구로 변환
    """
    user_text = (user_text or "").strip()

    if issue_type == "vpn":
        return "VPN 접속 불가 대응"
    if issue_type == "kakao":
        return "카카오톡 알림 미수신 점검"
    if issue_type == "dns":
        return "사내 DNS 이슈 점검"
    if issue_type == "iis":
        return "IIS + WebSocket 프록시 설정"

    # unknown이면 원문을 조금 정리해서 검색
    # (너무 긴 문장/잡담이면 오탐 가능하니 30자 컷 + 특수문자 제거)
    cleaned = re.sub(r"[^0-9a-zA-Z가-힣\s]+", " ", user_text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:30] if cleaned else "KB"


def build_graph():
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    kb = SearchKBTool()
    tickets = CreateTicketTool()

    # ✅ Class04-B: router node
    def router(state: AgentState) -> AgentState:
        issue_type, score = _simple_router(state.user_text)
        state.issue_type = issue_type
        state.router_score = score
        return state

    # ✅ Class04-B: query builder node
    def build_query(state: AgentState) -> AgentState:
        state.kb_query = _query_builder(state.issue_type, state.user_text)
        return state

    def kb_search(state: AgentState) -> AgentState:
        state.kb_hits = kb.search(state.kb_query, top_k=3)
        return state

    def decide_next(state: AgentState) -> str:
        return "compose_guided" if state.kb_hits else "create_ticket"

    def compose_guided(state: AgentState) -> AgentState:
        msg = llm.invoke([{"role": "user", "content": prompt_guided(state.user_text, state.kb_hits)}])
        state.final_text = msg.content #type: ignore
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
        state.final_text = msg.content #type: ignore
        state.action = "ticket_created"
        return state

    g = StateGraph(AgentState)

    # 노드 등록
    g.add_node("router", router)
    g.add_node("build_query", build_query)
    g.add_node("kb_search", kb_search)
    g.add_node("compose_guided", compose_guided)
    g.add_node("create_ticket", create_ticket)
    g.add_node("compose_ticket", compose_ticket)

    # 엔트리
    g.set_entry_point("router")

    # 엣지
    g.add_edge("router", "build_query")
    g.add_edge("build_query", "kb_search")
    g.add_conditional_edges(
        "kb_search",
        decide_next,
        {"compose_guided": "compose_guided", "create_ticket": "create_ticket"},
    )
    g.add_edge("compose_guided", END)
    g.add_edge("create_ticket", "compose_ticket")
    g.add_edge("compose_ticket", END)

    return g.compile()
