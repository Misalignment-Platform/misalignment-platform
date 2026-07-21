from __future__ import annotations

from backend.src.domain.metrics import MetricDefinition
from backend.src.domain.policies import Policy
from backend.src.domain.stakeholders import Stakeholder
from backend.src.domain.systems import System
from backend.src.infra.db_models import InMemoryStore


def create_system(system: System, store: InMemoryStore) -> System:
    store.systems[system.id] = system
    return system


def update_system(system_id: str, payload: dict, store: InMemoryStore) -> System | None:
    system = store.systems.get(system_id)
    if not system:
        return None
    updated = system.model_copy(update=payload)
    store.systems[system_id] = updated
    return updated


def delete_system(system_id: str, store: InMemoryStore) -> bool:
    if system_id not in store.systems:
        return False
    del store.systems[system_id]
    return True


def link_stakeholder(system_id: str, stakeholder: Stakeholder, store: InMemoryStore) -> tuple[System, Stakeholder] | None:
    system = store.systems.get(system_id)
    if not system:
        return None
    store.stakeholders[stakeholder.id] = stakeholder
    system.link_stakeholder(stakeholder.id)
    stakeholder.assign_system(system_id)
    store.systems[system_id] = system
    store.stakeholders[stakeholder.id] = stakeholder
    return system, stakeholder


def create_policy(policy: Policy, store: InMemoryStore) -> Policy | None:
    system = store.systems.get(policy.system_id)
    if not system:
        return None
    store.policies[policy.id] = policy
    system.add_policy(policy.id)
    store.systems[system.id] = system
    return policy


def create_metric_definition(metric: MetricDefinition, store: InMemoryStore) -> MetricDefinition:
    store.metrics[metric.id] = metric
    return metric
