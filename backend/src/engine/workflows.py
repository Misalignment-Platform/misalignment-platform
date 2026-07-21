from __future__ import annotations

from pydantic import BaseModel

from backend.src.domain.evaluations import Evaluation
from backend.src.domain.events import Event
from backend.src.domain.interventions import Intervention
from backend.src.domain.metrics import MetricScore
from backend.src.domain.stakeholders import Stakeholder
from backend.src.engine.classification import apply_classification, classify_event
from backend.src.engine.evaluation import evaluate_event
from backend.src.engine.ingestion import RawEventInput, ingest_event
from backend.src.engine.scoring import score_event
from backend.src.infra.db_models import InMemoryStore


class PipelineResult(BaseModel):
    event: Event
    evaluation: Evaluation
    intervention: Intervention | None
    scores: list[MetricScore]


def create_intervention(evaluation: Evaluation, event: Event, stakeholders: list[Stakeholder]) -> Intervention:
    stakeholder_ids = [stakeholder.id for stakeholder in stakeholders]
    return Intervention(
        system_id=event.system_id,
        event_id=event.id,
        evaluation_id=evaluation.id,
        policy_ids=evaluation.policy_ids,
        stakeholder_ids=stakeholder_ids,
        action=(evaluation.recommended_actions or ["monitor event"])[0],
    )


def update_intervention_state(intervention: Intervention, state: str) -> Intervention:
    if state == "in-progress":
        intervention.start()
    elif state == "resolved":
        intervention.resolve()
    elif state != "open":
        raise ValueError("state must be one of open, in-progress, resolved")
    return intervention


def orchestrate_event_lifecycle(raw_event: RawEventInput, store: InMemoryStore) -> PipelineResult:
    event = ingest_event(raw_event, store)
    policies = [policy for policy in store.policies.values() if policy.system_id == event.system_id]
    stakeholders = [
        stakeholder
        for stakeholder in store.stakeholders.values()
        if event.system_id in stakeholder.system_ids
    ]

    classification = classify_event(event, policies)
    event = apply_classification(event, classification)
    store.events[event.id] = event

    metric_definitions = list(store.metrics.values())
    scores = score_event(event, metric_definitions)
    for score in scores:
        store.metric_scores[score.id] = score

    evaluation = evaluate_event(event, scores, stakeholders)
    store.evaluations[evaluation.id] = evaluation

    intervention = None
    if evaluation.requires_intervention():
        intervention = create_intervention(evaluation, event, stakeholders)
        store.interventions[intervention.id] = intervention

    return PipelineResult(event=event, evaluation=evaluation, intervention=intervention, scores=scores)
