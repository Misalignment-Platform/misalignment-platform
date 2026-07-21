from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class MetricDefinition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    target: Literal["system", "policy", "incident"] = "system"


class MetricScore(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    metric_id: str
    system_id: str
    value: float
    event_id: str | None = None
    policy_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("value")
    @classmethod
    def validate_score(cls, value: float) -> float:
        if value < 0 or value > 100:
            raise ValueError("metric score must be between 0 and 100")
        return value
