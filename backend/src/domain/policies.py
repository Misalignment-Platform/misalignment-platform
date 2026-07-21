from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Policy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    system_id: str
    name: str
    description: str = ""
    rule_keywords: list[str] = Field(default_factory=list)
    min_compliance_score: float = 80.0
    severity: Literal["low", "medium", "high"] = "medium"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def matches_event(self, content: str) -> bool:
        lowered = content.lower()
        return any(keyword.lower() in lowered for keyword in self.rule_keywords)
