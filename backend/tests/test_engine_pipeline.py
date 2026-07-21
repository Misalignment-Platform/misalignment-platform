from backend.src.domain.metrics import MetricDefinition
from backend.src.domain.policies import Policy
from backend.src.domain.stakeholders import Stakeholder
from backend.src.domain.systems import System
from backend.src.engine.ingestion import RawEventInput
from backend.src.engine.workflows import orchestrate_event_lifecycle
from backend.src.infra.db_models import InMemoryStore


def test_incident_lifecycle_creates_intervention_for_policy_violation() -> None:
    store = InMemoryStore()
    system = System(id="sys-1", name="Core API")
    store.systems[system.id] = system

    stakeholder = Stakeholder(id="owner-1", name="Owner", role="owner", email="owner@example.com")
    stakeholder.assign_system(system.id)
    store.stakeholders[stakeholder.id] = stakeholder

    policy = Policy(
        id="pol-1",
        system_id=system.id,
        name="No PII Leakage",
        rule_keywords=["ssn", "password"],
    )
    store.policies[policy.id] = policy

    risk_metric = MetricDefinition(id="m-risk", name="risk_score")
    compliance_metric = MetricDefinition(id="m-compliance", name="compliance_score")
    store.metrics[risk_metric.id] = risk_metric
    store.metrics[compliance_metric.id] = compliance_metric

    result = orchestrate_event_lifecycle(
        RawEventInput(system_id=system.id, source="webhook", content="User posted password in logs"),
        store,
    )

    assert result.event.risk_category == "high"
    assert result.evaluation.compliance_status == "violation"
    assert result.intervention is not None
    assert result.intervention.state == "open"
    assert result.intervention.stakeholder_ids == [stakeholder.id]
