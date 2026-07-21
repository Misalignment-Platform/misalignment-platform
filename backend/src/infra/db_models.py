from __future__ import annotations

from dataclasses import dataclass, field

from backend.src.domain.evaluations import Evaluation
from backend.src.domain.events import Event
from backend.src.domain.interventions import Intervention
from backend.src.domain.metrics import MetricDefinition, MetricScore
from backend.src.domain.policies import Policy
from backend.src.domain.stakeholders import Stakeholder
from backend.src.domain.systems import System


@dataclass
class InMemoryStore:
    systems: dict[str, System] = field(default_factory=dict)
    policies: dict[str, Policy] = field(default_factory=dict)
    metrics: dict[str, MetricDefinition] = field(default_factory=dict)
    metric_scores: dict[str, MetricScore] = field(default_factory=dict)
    events: dict[str, Event] = field(default_factory=dict)
    evaluations: dict[str, Evaluation] = field(default_factory=dict)
    interventions: dict[str, Intervention] = field(default_factory=dict)
    stakeholders: dict[str, Stakeholder] = field(default_factory=dict)

    def reset(self) -> None:
        self.systems.clear()
        self.policies.clear()
        self.metrics.clear()
        self.metric_scores.clear()
        self.events.clear()
        self.evaluations.clear()
        self.interventions.clear()
        self.stakeholders.clear()


STORE = InMemoryStore()


def get_store() -> InMemoryStore:
    return STORE
