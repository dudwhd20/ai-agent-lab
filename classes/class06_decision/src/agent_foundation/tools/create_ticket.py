from __future__ import annotations

import time
import uuid
from typing import Any, Dict


class CreateTicketTool:
    def create(self, title: str, description: str, priority: str = "P3") -> Dict[str, Any]:
        return {
            "ticket_id": f"TCK-{uuid.uuid4().hex[:8].upper()}",
            "created_at": int(time.time()),
            "priority": priority,
            "title": title,
            "description": description,
        }
