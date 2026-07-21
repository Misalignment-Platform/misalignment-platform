from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.src.api.dtos import (
    EvaluationResponse,
    MetricScoreResponse,
    PolicyCreateRequest,
    PolicyResponse,
    StakeholderCreateRequest,
    StakeholderResponse,
    SystemCreateRequest,
    SystemResponse,
    SystemUpdateRequest,
    InterventionResponse,
)
from backend.src.engine.services import (
    create_policy,
    create_system,
    delete_system,
    link_stakeholder,
    update_system,
)
from backend.src.infra.auth import require_scope
from backend.src.infra.db_models import InMemoryStore, get_store

router = APIRouter(prefix="/systems", tags=["systems"])


@router.post("", response_model=SystemResponse, status_code=status.HTTP_201_CREATED)
def create_system_route(
    payload: SystemCreateRequest,
    _: object = Depends(require_scope("systems:write")),
    store: InMemoryStore = Depends(get_store),
) -> SystemResponse:
    system = create_system(payload.to_domain(), store)
    return SystemResponse.from_domain(system)


@router.get("", response_model=list[SystemResponse])
def list_systems_route(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[SystemResponse]:
    systems = list(store.systems.values())
    return [SystemResponse.from_domain(system) for system in systems[offset : offset + limit]]


@router.get("/{system_id}", response_model=SystemResponse)
def get_system_route(
    system_id: str,
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> SystemResponse:
    system = store.systems.get(system_id)
    if not system:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="system not found")
    return SystemResponse.from_domain(system)


@router.put("/{system_id}", response_model=SystemResponse)
def update_system_route(
    system_id: str,
    payload: SystemUpdateRequest,
    _: object = Depends(require_scope("systems:write")),
    store: InMemoryStore = Depends(get_store),
) -> SystemResponse:
    updated = update_system(system_id, payload.model_dump(), store)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="system not found")
    return SystemResponse.from_domain(updated)


@router.delete("/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_system_route(
    system_id: str,
    _: object = Depends(require_scope("systems:write")),
    store: InMemoryStore = Depends(get_store),
) -> None:
    if not delete_system(system_id, store):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="system not found")


@router.post("/{system_id}/stakeholders", response_model=StakeholderResponse, status_code=status.HTTP_201_CREATED)
def link_stakeholder_route(
    system_id: str,
    stakeholder: StakeholderCreateRequest,
    _: object = Depends(require_scope("systems:write")),
    store: InMemoryStore = Depends(get_store),
) -> StakeholderResponse:
    linked = link_stakeholder(system_id, stakeholder.to_domain(), store)
    if not linked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="system not found")
    return StakeholderResponse.from_domain(linked[1])


@router.post("/{system_id}/policies", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy_route(
    system_id: str,
    payload: PolicyCreateRequest,
    _: object = Depends(require_scope("systems:write")),
    store: InMemoryStore = Depends(get_store),
) -> PolicyResponse:
    policy = create_policy(payload.to_domain(system_id), store)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="system not found")
    return PolicyResponse.from_domain(policy)


@router.get("/{system_id}/evaluations", response_model=list[EvaluationResponse])
def list_system_evaluations_route(
    system_id: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[EvaluationResponse]:
    evaluations = [
        evaluation for evaluation in store.evaluations.values() if evaluation.system_id == system_id
    ]
    return [
        EvaluationResponse.from_domain(evaluation)
        for evaluation in evaluations[offset : offset + limit]
    ]


@router.get("/{system_id}/metrics", response_model=list[MetricScoreResponse])
def list_system_metrics_route(
    system_id: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[MetricScoreResponse]:
    scores = [score for score in store.metric_scores.values() if score.system_id == system_id]
    return [MetricScoreResponse.from_domain(score) for score in scores[offset : offset + limit]]


@router.get("/{system_id}/interventions", response_model=list[InterventionResponse])
def list_system_interventions_route(
    system_id: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[InterventionResponse]:
    interventions = [
        intervention
        for intervention in store.interventions.values()
        if intervention.system_id == system_id
    ]
    return [
        InterventionResponse.from_domain(intervention)
        for intervention in interventions[offset : offset + limit]
    ]
