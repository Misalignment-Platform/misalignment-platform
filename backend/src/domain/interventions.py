from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Intervention(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    system_id: str
    event_id: str
    evaluation_id: str
    policy_ids: list[str] = Field(default_factory=list)
    stakeholder_ids: list[str] = Field(default_factory=list)
    action: str
    state: Literal["open", "in-progress", "resolved"] = "open"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def start(self) -> None:
        if self.state != "open":
            raise ValueError("intervention can only be started from open state")
        self.state = "in-progress"
        self._touch()

    def resolve(self) -> None:
        if self.state not in {"open", "in-progress"}:
            raise ValueError("intervention is already resolved")
        self.state = "resolved"
        self._touch()
