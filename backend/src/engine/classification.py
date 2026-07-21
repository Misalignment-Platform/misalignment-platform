from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from backend.src.domain.events import Event
from backend.src.domain.policies import Policy


class ClassificationResult(BaseModel):
    event_id: str
    risk_category: Literal["low", "medium", "high"]
    incident_type: str
    violated_policy_ids: list[str]


def classify_event(event: Event, policies: list[Policy]) -> ClassificationResult:
    violated_policy_ids = [policy.id for policy in policies if policy.matches_event(event.content)]
    lowered = event.content.lower()

    if violated_policy_ids:
        risk = "high"
        incident_type = "policy-violation"
    elif any(token in lowered for token in ["outage", "error", "failure", "incident"]):
        risk = "medium"
        incident_type = "operational-risk"
    else:
        risk = "low"
        incident_type = "informational"

    return ClassificationResult(
        event_id=event.id,
        risk_category=risk,
        incident_type=incident_type,
        violated_policy_ids=violated_policy_ids,
    )


def apply_classification(event: Event, result: ClassificationResult) -> Event:
    event.apply_classification(
        risk_category=result.risk_category,
        incident_type=result.incident_type,
        violated_policy_ids=result.violated_policy_ids,
    )
    return event
