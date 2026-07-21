from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class System(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    status: Literal["active", "inactive"] = "active"
    policy_ids: list[str] = Field(default_factory=list)
    stakeholder_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def add_policy(self, policy_id: str) -> None:
        if policy_id not in self.policy_ids:
            self.policy_ids.append(policy_id)

    def link_stakeholder(self, stakeholder_id: str) -> None:
        if stakeholder_id not in self.stakeholder_ids:
            self.stakeholder_ids.append(stakeholder_id)
