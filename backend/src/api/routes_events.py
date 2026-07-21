from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.src.api.dtos import (
    EvaluationResponse,
    EventIngestRequest,
    EventResponse,
    IncidentViewResponse,
    InterventionResponse,
    PipelineResultResponse,
)
from backend.src.engine.workflows import orchestrate_event_lifecycle
from backend.src.infra.auth import require_scope
from backend.src.infra.db_models import InMemoryStore, get_store

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/ingest", response_model=PipelineResultResponse)
def ingest_event_route(
    payload: EventIngestRequest,
    _: object = Depends(require_scope("events:write")),
    store: InMemoryStore = Depends(get_store),
) -> PipelineResultResponse:
    result = orchestrate_event_lifecycle(payload.to_domain(), store)
    return PipelineResultResponse.from_domain(result)


@router.get("", response_model=list[EventResponse])
def list_events_route(
    system_id: str | None = Query(default=None, min_length=1),
    risk_category: Literal["low", "medium", "high"] | None = Query(default=None),
    state: Literal["open", "in-progress", "resolved"] | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[EventResponse]:
    events = list(store.events.values())
    if system_id:
        events = [event for event in events if event.system_id == system_id]
    if risk_category:
        events = [event for event in events if event.risk_category == risk_category]
    if state:
        events = [event for event in events if event.state == state]
    return [EventResponse.from_domain(event) for event in events[offset : offset + limit]]


@router.get("/{event_id}/incident", response_model=IncidentViewResponse)
def get_incident_view_route(
    event_id: str,
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> IncidentViewResponse:
    event = store.events.get(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event not found")
    evaluations = [evaluation for evaluation in store.evaluations.values() if evaluation.event_id == event_id]
    interventions = [
        intervention for intervention in store.interventions.values() if intervention.event_id == event_id
    ]
    return IncidentViewResponse(
        event=EventResponse.from_domain(event),
        evaluations=[EvaluationResponse.from_domain(evaluation) for evaluation in evaluations],
        interventions=[InterventionResponse.from_domain(intervention) for intervention in interventions],
    )
