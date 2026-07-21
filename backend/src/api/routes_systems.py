from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.src.domain.policies import Policy
from backend.src.domain.stakeholders import Stakeholder
from backend.src.domain.systems import System
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


@router.post("", response_model=System, status_code=status.HTTP_201_CREATED)
def create_system_route(
    payload: System,
    _: object = Depends(require_scope("systems:write")),
    store: InMemoryStore = Depends(get_store),
) -> System:
    return create_system(payload, store)


@router.get("", response_model=list[System])
def list_systems_route(
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[System]:
    return list(store.systems.values())


@router.get("/{system_id}", response_model=System)
def get_system_route(
    system_id: str,
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> System:
    system = store.systems.get(system_id)
    if not system:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="system not found")
    return system


@router.put("/{system_id}", response_model=System)
def update_system_route(
    system_id: str,
    payload: System,
    _: object = Depends(require_scope("systems:write")),
    store: InMemoryStore = Depends(get_store),
) -> System:
    updated = update_system(system_id, payload.model_dump(), store)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="system not found")
    return updated


@router.delete("/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_system_route(
    system_id: str,
    _: object = Depends(require_scope("systems:write")),
    store: InMemoryStore = Depends(get_store),
) -> None:
    if not delete_system(system_id, store):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="system not found")


@router.post("/{system_id}/stakeholders", response_model=Stakeholder, status_code=status.HTTP_201_CREATED)
def link_stakeholder_route(
    system_id: str,
    stakeholder: Stakeholder,
    _: object = Depends(require_scope("systems:write")),
    store: InMemoryStore = Depends(get_store),
) -> Stakeholder:
    linked = link_stakeholder(system_id, stakeholder, store)
    if not linked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="system not found")
    return linked[1]


@router.post("/{system_id}/policies", response_model=Policy, status_code=status.HTTP_201_CREATED)
def create_policy_route(
    system_id: str,
    payload: Policy,
    _: object = Depends(require_scope("systems:write")),
    store: InMemoryStore = Depends(get_store),
) -> Policy:
    if payload.system_id != system_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="system_id mismatch")
    policy = create_policy(payload, store)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="system not found")
    return policy


@router.get("/{system_id}/evaluations")
def list_system_evaluations_route(
    system_id: str,
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[dict]:
    return [
        evaluation.model_dump()
        for evaluation in store.evaluations.values()
        if evaluation.system_id == system_id
    ]


@router.get("/{system_id}/metrics")
def list_system_metrics_route(
    system_id: str,
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[dict]:
    return [score.model_dump() for score in store.metric_scores.values() if score.system_id == system_id]


@router.get("/{system_id}/interventions")
def list_system_interventions_route(
    system_id: str,
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[dict]:
    return [
        intervention.model_dump()
        for intervention in store.interventions.values()
        if intervention.system_id == system_id
    ]
