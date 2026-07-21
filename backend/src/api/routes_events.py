from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.src.engine.ingestion import RawEventInput
from backend.src.engine.workflows import PipelineResult, orchestrate_event_lifecycle
from backend.src.infra.auth import require_scope
from backend.src.infra.db_models import InMemoryStore, get_store

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/ingest", response_model=PipelineResult)
def ingest_event_route(
    payload: RawEventInput,
    _: object = Depends(require_scope("events:write")),
    store: InMemoryStore = Depends(get_store),
) -> PipelineResult:
    return orchestrate_event_lifecycle(payload, store)


@router.get("")
def list_events_route(
    system_id: str | None = Query(default=None),
    risk_category: str | None = Query(default=None),
    state: str | None = Query(default=None),
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> list[dict]:
    events = list(store.events.values())
    if system_id:
        events = [event for event in events if event.system_id == system_id]
    if risk_category:
        events = [event for event in events if event.risk_category == risk_category]
    if state:
        events = [event for event in events if event.state == state]
    return [event.model_dump() for event in events]


@router.get("/{event_id}/incident")
def get_incident_view_route(
    event_id: str,
    _: object = Depends(require_scope("read")),
    store: InMemoryStore = Depends(get_store),
) -> dict:
    event = store.events.get(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event not found")
    evaluations = [evaluation for evaluation in store.evaluations.values() if evaluation.event_id == event_id]
    interventions = [
        intervention for intervention in store.interventions.values() if intervention.event_id == event_id
    ]
    return {
        "event": event.model_dump(),
        "evaluations": [evaluation.model_dump() for evaluation in evaluations],
        "interventions": [intervention.model_dump() for intervention in interventions],
    }
