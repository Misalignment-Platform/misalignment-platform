from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Stakeholder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    role: Literal["owner", "reviewer", "auditor"]
    email: str
    system_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def assign_system(self, system_id: str) -> None:
        if system_id not in self.system_ids:
            self.system_ids.append(system_id)
