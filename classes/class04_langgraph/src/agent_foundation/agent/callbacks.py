from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any, Dict, Optional

from langchain_core.callbacks.base import BaseCallbackHandler


class AuditCallbackHandler(BaseCallbackHandler):
    """
    최소 감사로그 스펙:
      - trace_id
      - tool_name
      - tool_input
      - tool_output_summary
      - latency_ms
      - error
    """

    def __init__(self, log_path: str = "logs/sample_run.jsonl", trace_id: Optional[str] = None):
        self.log_path = log_path
        self.trace_id = trace_id or uuid.uuid4().hex
        self._tool_start_ts: Dict[str, float] = {}

        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def _append(self, record: Dict[str, Any]) -> None:
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        tool_name = serialized.get("name", "unknown_tool")
        key = f"{tool_name}:{uuid.uuid4().hex}"
        self._tool_start_ts[key] = time.time()

        self._append(
            {
                "trace_id": self.trace_id,
                "event": "tool_start",
                "tool_name": tool_name,
                "tool_input": input_str,
                "ts": int(time.time() * 1000),
                "tool_call_id": key,
            }
        )

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        # langchain 콜백에서 tool_call_id를 항상 주지 않는 경우가 있어,
        # end는 latency를 엄밀하게 매칭 못할 수 있음(데모 범위).
        # 실무에선 tool_call_id를 상태로 더 강하게 붙이는 쪽 권장.
        self._append(
            {
                "trace_id": self.trace_id,
                "event": "tool_end",
                "tool_output_summary": str(output)[:500],
                "ts": int(time.time() * 1000),
            }
        )

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        self._append(
            {
                "trace_id": self.trace_id,
                "event": "tool_error",
                "error": repr(error),
                "ts": int(time.time() * 1000),
            }
        )
