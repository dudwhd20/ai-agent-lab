from __future__ import annotations
from agent_foundation.agent.issue_types import IssueType

def build_kb_query(issue: IssueType, user_text: str) -> str:
    if issue == IssueType.VPN:
        return "VPN 접속 불가 대응"
    if issue == IssueType.MESSENGER:
        return "메신저 알림 문제"
    if issue == IssueType.NETWORK:
        return "사내 DNS 이슈 점검"
    # UNKNOWN이면 원문을 그대로 쓰되, 과장된 재해석은 금지
    return user_text.strip()
