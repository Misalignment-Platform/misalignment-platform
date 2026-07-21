from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    system_id: str
    source: str
    content: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    risk_category: Literal["low", "medium", "high"] = "low"
    incident_type: str = "signal"
    violated_policy_ids: list[str] = Field(default_factory=list)
    state: Literal["open", "in-progress", "resolved"] = "open"

    def apply_classification(
        self,
        *,
        risk_category: Literal["low", "medium", "high"],
        incident_type: str,
        violated_policy_ids: list[str],
    ) -> None:
        self.risk_category = risk_category
        self.incident_type = incident_type
        self.violated_policy_ids = violated_policy_ids

    def transition_state(self, next_state: Literal["open", "in-progress", "resolved"]) -> None:
        transitions = {
            "open": {"in-progress", "resolved"},
            "in-progress": {"resolved"},
            "resolved": set(),
        }
        if next_state not in transitions[self.state]:
            raise ValueError(f"invalid event transition from {self.state} to {next_state}")
        self.state = next_state
