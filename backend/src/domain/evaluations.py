from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Evaluation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    system_id: str
    event_id: str
    policy_ids: list[str] = Field(default_factory=list)
    metric_score_ids: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high"]
    compliance_status: Literal["compliant", "violation"]
    recommended_actions: list[str] = Field(default_factory=list)
    stakeholder_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def requires_intervention(self) -> bool:
        return self.compliance_status == "violation" or self.risk_level in {"medium", "high"}
