from __future__ import annotations

from pydantic import BaseModel

from backend.src.domain.events import Event
from backend.src.domain.metrics import MetricDefinition, MetricScore


class ScoringRequest(BaseModel):
    event_id: str
    metric_definition_ids: list[str]


RISK_BASELINE = {"low": 88.0, "medium": 58.0, "high": 25.0}


def _score_for_metric(event: Event, metric: MetricDefinition) -> float:
    name = metric.name.lower()
    compliance = 20.0 if event.violated_policy_ids else 95.0
    if "compliance" in name:
        return compliance
    if "violation" in name:
        return 100.0 - compliance
    return RISK_BASELINE[event.risk_category]


def score_event(event: Event, metric_definitions: list[MetricDefinition]) -> list[MetricScore]:
    return [
        MetricScore(
            metric_id=metric.id,
            system_id=event.system_id,
            event_id=event.id,
            policy_id=event.violated_policy_ids[0] if event.violated_policy_ids else None,
            value=_score_for_metric(event, metric),
        )
        for metric in metric_definitions
    ]


def aggregate_scores(scores: list[MetricScore]) -> dict[str, float]:
    totals: dict[str, list[float]] = {}
    for score in scores:
        totals.setdefault(score.metric_id, []).append(score.value)
    return {metric_id: sum(values) / len(values) for metric_id, values in totals.items()}
