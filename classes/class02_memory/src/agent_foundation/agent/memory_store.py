from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class SessionState:
    session_id: str
    last_user_text: str = ""
    last_action: str = ""         # "guided" | "ticket_created"
    last_ticket_id: str = ""      # 티켓 생성 시만 채움


class FileMemoryStore:
    """
    매우 단순한 파일 기반 Memory.
    - 세션별 상태를 logs/memory/<session_id>.json 으로 저장
    - Class02 목표: '같은 질문 반복'을 감지해서 행동 바꾸기
    """
    def __init__(self, base_dir: str = "logs/memory"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        safe = "".join(c for c in session_id if c.isalnum() or c in ("-", "_"))
        if not safe:
            safe = "default"
        return self.base_dir / f"{safe}.json"

    def load(self, session_id: str) -> SessionState:
        p = self._path(session_id)
        if not p.exists():
            return SessionState(session_id=session_id)

        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return SessionState(
                session_id=session_id,
                last_user_text=data.get("last_user_text", ""),
                last_action=data.get("last_action", ""),
                last_ticket_id=data.get("last_ticket_id", ""),
            )
        except Exception:
            # 파일이 깨졌어도 실습은 계속 진행되게 기본값으로 복구
            return SessionState(session_id=session_id)

    def save(self, state: SessionState) -> None:
        p = self._path(state.session_id)
        p.write_text(json.dumps(asdict(state), ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def is_same_issue(a: str, b: str) -> bool:
        # Class02에서는 아주 단순하게 "완전 동일" 기준으로 판단
        # (Class03에서 정규화/유사도/해시로 발전시킬 예정)
        return (a or "").strip() == (b or "").strip()
