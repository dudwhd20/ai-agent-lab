from __future__ import annotations
from agent_foundation.agent.issue_types import IssueType

PROTOTYPES = {
    IssueType.VPN: [
        "VPN 연결이 안 돼요",
        "사내 VPN 접속이 실패합니다",
        "VPN 인증 오류가 납니다",
        "VPN이 자주 끊겨요",
        "원격 접속이 안 됩니다",
        "VPN 연결이 자주 끊기고 인증 오류가 납니다",
        "VPN 접속은 되는데 일정 시간 후 끊기고 다시 로그인하라고 나옵니다",
    ],
    IssueType.MESSENGER: [
        "카카오톡 알림이 안 와요",
        "카톡 푸시 알림이 누락돼요",
        "메신저 알림이 늦게 와요",
        "알림 설정은 켰는데도 안 옵니다",
        "채팅 알림이 갑자기 안 떠요",
    ],
    IssueType.NETWORK: [
        "인터넷이 안 됩니다",
        "와이파이는 잡히는데 인터넷이 안 돼요",
        "DNS 문제 같은데요",
        "사내 네트워크가 느려요",
        "내부망 접속이 안 됩니다",
    ],
}
