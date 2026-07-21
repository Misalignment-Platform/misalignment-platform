from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from backend.src.domain.events import Event
from backend.src.infra.db_models import InMemoryStore


class RawEventInput(BaseModel):
    system_id: str
    source: str
    content: str = Field(min_length=1)
    occurred_at: datetime | None = None


def ingest_event(raw_event: RawEventInput, store: InMemoryStore) -> Event:
    event = Event(
        system_id=raw_event.system_id,
        source=raw_event.source,
        content=raw_event.content,
        occurred_at=raw_event.occurred_at or datetime.now(timezone.utc),
    )
    store.events[event.id] = event
    return event


def ingest_events(raw_events: list[RawEventInput], store: InMemoryStore) -> list[Event]:
    return [ingest_event(raw_event, store) for raw_event in raw_events]
