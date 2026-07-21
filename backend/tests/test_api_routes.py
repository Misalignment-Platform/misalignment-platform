from fastapi.testclient import TestClient

from backend.src.api.app import create_app
from backend.src.infra.db_models import get_store


def _headers(scope: str) -> dict[str, str]:
    return {"Authorization": f"******;roles:admin;scopes:{scope},read"}


def test_event_ingestion_pipeline_and_system_views() -> None:
    store = get_store()
    store.reset()
    client = TestClient(create_app())

    create_system_response = client.post(
        "/api/systems",
        json={"id": "sys-1", "name": "Payments", "description": "Core service", "status": "active"},
        headers=_headers("systems:write"),
    )
    assert create_system_response.status_code == 201

    stakeholder_response = client.post(
        "/api/systems/sys-1/stakeholders",
        json={"id": "st-1", "name": "Alice", "role": "owner", "email": "alice@example.com"},
        headers=_headers("systems:write"),
    )
    assert stakeholder_response.status_code == 201

    policy_response = client.post(
        "/api/systems/sys-1/policies",
        json={
            "id": "pol-1",
            "system_id": "sys-1",
            "name": "No secrets",
            "description": "Disallow password exposure",
            "rule_keywords": ["password"]
        },
        headers=_headers("systems:write"),
    )
    assert policy_response.status_code == 201

    ingest_response = client.post(
        "/api/events/ingest",
        json={"system_id": "sys-1", "source": "webhook", "content": "password leaked"},
        headers=_headers("events:write"),
    )
    assert ingest_response.status_code == 200
    payload = ingest_response.json()
    assert payload["intervention"]["state"] == "open"

    metrics_response = client.get("/api/systems/sys-1/metrics", headers=_headers("read"))
    assert metrics_response.status_code == 200
    assert len(metrics_response.json()) >= 1


def test_system_policy_validation_error() -> None:
    store = get_store()
    store.reset()
    client = TestClient(create_app())

    client.post(
        "/api/systems",
        json={"id": "sys-1", "name": "Payments", "description": "Core service", "status": "active"},
        headers=_headers("systems:write"),
    )

    response = client.post(
        "/api/systems/sys-1/policies",
        json={
            "id": "pol-1",
            "system_id": "sys-2",
            "name": "No secrets",
            "description": "Disallow password exposure",
            "rule_keywords": ["password"]
        },
        headers=_headers("systems:write"),
    )
    assert response.status_code == 400
