from __future__ import annotations

from typing import Any, Dict, List


def _guess_issue_type(user_text: str, kb_hits: List[Dict[str, Any]]) -> str:
    """
    설치형 없이 가벼운 분류:
    - user_text, KB title/snippet에 키워드가 있으면 해당 타입으로
    """
    t = (user_text or "").lower()

    # KB 힌트도 같이 본다
    kb_text = " ".join(
        [(h.get("title", "") + " " + h.get("snippet", "")) for h in (kb_hits or [])]
    ).lower()

    hay = t + " " + kb_text

    if "vpn" in hay:
        return "vpn"
    if "dns" in hay or "nslookup" in hay:
        return "dns"
    if "카카오톡" in hay or "알림" in hay or "집중모드" in hay:
        return "notification"
    if "로그인" in hay or "인증" in hay or "auth" in hay:
        return "auth"

    return "generic"


def build_clarifying_questions(
    user_text: str,
    kb_hits: List[Dict[str, Any]],
) -> List[str]:
    """
    mid confidence일 때 던질 질문 2개를 반환한다.
    원칙:
    - (재현 조건 1) + (환경 정보 1)
    - 항상 2개
    """
    issue_type = _guess_issue_type(user_text, kb_hits)

    if issue_type == "vpn":
        return [
            "VPN 클라이언트 이름/버전과 사용 중인 OS(Windows/macOS)를 알려주세요.",
            "끊김 또는 인증 오류가 발생할 때 표시되는 오류 메시지(코드/문구)를 그대로 알려주세요.",
        ]

    if issue_type == "notification":
        return [
            "사용 기기(OS: iOS/Android)와 OS 버전을 알려주세요.",
            "카카오톡만 알림이 안 오는지, 다른 앱 알림도 같이 지연/누락되는지 알려주세요.",
        ]

    if issue_type == "dns":
        return [
            "문제가 발생한 도메인(또는 URL)을 정확히 알려주세요.",
            "사내망/외부망(집, 핫스팟 등) 중 어느 환경에서 문제가 발생하는지 알려주세요.",
        ]

    if issue_type == "auth":
        return [
            "로그인/인증 실패가 발생하는 화면(또는 단계)과 오류 메시지를 알려주세요.",
            "해당 문제가 특정 네트워크(사내/외부)나 특정 시간대에만 발생하는지 알려주세요.",
        ]

    # generic fallback
    return [
        "문제가 언제부터/어떤 동작을 했을 때 발생하는지(재현 절차)를 간단히 알려주세요.",
        "사용 환경(OS/기기)과 네트워크 환경(사내망/외부망)을 알려주세요.",
    ]
