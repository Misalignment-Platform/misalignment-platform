from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from backend.src.api.dtos import (
    MetricAggregatesResponse,
    MetricDefinitionCreateRequest,
    MetricDefinitionResponse,
    MetricScoreResponse,
    MetricTrendAverageResponse,
    MetricTrendsResponse,
)
from backend.src.engine.scoring import aggregate_scores
from backend.src.engine.services import create_metric_definition
from backend.src.infra.auth import require_scope
from backend.src.infra.db_models import InMemoryStore, get_store

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/definitions", response_model=MetricDefinitionResponse, status_code=status.HTTP_201_CREATED)
def create_metric_definition_route(
    payload: MetricDefinitionCreateRequest,
    _: object = Depends(require_scope("metrics:write")),
    store: InMemoryStore = Depends(get_store),
) -> MetricDefinitionResponse:
    metric_definition = create_metric_definition(payload.to_domain(), store)
    return MetricDefinitionResponse.from_domain(metric_definition)


@router.get("/definitions", response_model=list[MetricDefinitionResponse])
def list_metric_definitions_route(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[MetricDefinitionResponse]:
    definitions = list(store.metrics.values())
    return [
        MetricDefinitionResponse.from_domain(metric)
        for metric in definitions[offset : offset + limit]
    ]


@router.get("/scores", response_model=list[MetricScoreResponse])
def list_metric_scores_route(
    system_id: str | None = Query(default=None, min_length=1),
    policy_id: str | None = Query(default=None, min_length=1),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[MetricScoreResponse]:
    scores = list(store.metric_scores.values())
    if system_id:
        scores = [score for score in scores if score.system_id == system_id]
    if policy_id:
        scores = [score for score in scores if score.policy_id == policy_id]
    return [MetricScoreResponse.from_domain(score) for score in scores[offset : offset + limit]]


@router.get("/trends", response_model=MetricTrendsResponse)
def metric_trends_route(
    system_id: str | None = Query(default=None, min_length=1),
    policy_id: str | None = Query(default=None, min_length=1),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> MetricTrendsResponse:
    scores = list(store.metric_scores.values())
    if system_id:
        scores = [score for score in scores if score.system_id == system_id]
    if policy_id:
        scores = [score for score in scores if score.policy_id == policy_id]
    metric_lookup = store.metrics
    return MetricTrendsResponse(
        averages=[
            MetricTrendAverageResponse(
                metric_id=metric_id,
                metric_name=metric_lookup.get(metric_id).name if metric_lookup.get(metric_id) else metric_id,
                average=average,
            )
            for metric_id, average in aggregate_scores(scores).items()
        ]
    )


@router.get("/aggregates", response_model=MetricAggregatesResponse)
def metric_aggregate_route(
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> MetricAggregatesResponse:
    return MetricAggregatesResponse(totals=aggregate_scores(list(store.metric_scores.values())))
