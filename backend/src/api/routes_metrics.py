from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from backend.src.domain.metrics import MetricDefinition
from backend.src.engine.scoring import aggregate_scores
from backend.src.engine.services import create_metric_definition
from backend.src.infra.auth import require_scope
from backend.src.infra.db_models import InMemoryStore, get_store

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/definitions", response_model=MetricDefinition, status_code=status.HTTP_201_CREATED)
def create_metric_definition_route(
    payload: MetricDefinition,
    _: object = Depends(require_scope("metrics:write")),
    store: InMemoryStore = Depends(get_store),
) -> MetricDefinition:
    return create_metric_definition(payload, store)


@router.get("/definitions", response_model=list[MetricDefinition])
def list_metric_definitions_route(
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[MetricDefinition]:
    return list(store.metrics.values())


@router.get("/scores")
def list_metric_scores_route(
    system_id: str | None = Query(default=None),
    policy_id: str | None = Query(default=None),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[dict]:
    scores = list(store.metric_scores.values())
    if system_id:
        scores = [score for score in scores if score.system_id == system_id]
    if policy_id:
        scores = [score for score in scores if score.policy_id == policy_id]
    return [score.model_dump() for score in scores]


@router.get("/trends")
def metric_trends_route(
    system_id: str | None = Query(default=None),
    policy_id: str | None = Query(default=None),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> dict:
    scores = list(store.metric_scores.values())
    if system_id:
        scores = [score for score in scores if score.system_id == system_id]
    if policy_id:
        scores = [score for score in scores if score.policy_id == policy_id]
    metric_lookup = store.metrics
    return {
        "averages": [
            {
                "metric_id": metric_id,
                "metric_name": metric_lookup.get(metric_id).name if metric_lookup.get(metric_id) else metric_id,
                "average": average,
            }
            for metric_id, average in aggregate_scores(scores).items()
        ]
    }


@router.get("/aggregates")
def metric_aggregate_route(
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> dict:
    return {"totals": aggregate_scores(list(store.metric_scores.values()))}
