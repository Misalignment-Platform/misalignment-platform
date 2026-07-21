from __future__ import annotations

from pydantic import BaseModel

from backend.src.domain.evaluations import Evaluation
from backend.src.domain.events import Event
from backend.src.domain.metrics import MetricScore
from backend.src.domain.stakeholders import Stakeholder


class EvaluationInput(BaseModel):
    event_id: str
    score_ids: list[str]


def evaluate_event(event: Event, scores: list[MetricScore], stakeholders: list[Stakeholder]) -> Evaluation:
    average_score = sum(score.value for score in scores) / max(len(scores), 1)

    if average_score < 40:
        risk_level = "high"
    elif average_score < 70:
        risk_level = "medium"
    else:
        risk_level = "low"

    compliance_status = "violation" if event.violated_policy_ids else "compliant"

    recommended_actions: list[str] = []
    if compliance_status == "violation":
        recommended_actions.append("review violated policies")
    if risk_level in {"medium", "high"}:
        recommended_actions.append("initiate stakeholder triage")

    return Evaluation(
        system_id=event.system_id,
        event_id=event.id,
        policy_ids=event.violated_policy_ids,
        metric_score_ids=[score.id for score in scores],
        risk_level=risk_level,
        compliance_status=compliance_status,
        recommended_actions=recommended_actions,
        stakeholder_ids=[stakeholder.id for stakeholder in stakeholders],
    )
