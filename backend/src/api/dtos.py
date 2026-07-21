from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.src.domain.evaluations import Evaluation
from backend.src.domain.events import Event
from backend.src.domain.interventions import Intervention
from backend.src.domain.metrics import MetricDefinition, MetricScore
from backend.src.domain.policies import Policy
from backend.src.domain.stakeholders import Stakeholder
from backend.src.domain.systems import System
from backend.src.engine.ingestion import RawEventInput
from backend.src.engine.workflows import PipelineResult


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SystemCreateRequest(_StrictModel):
    id: str | None = None
    name: str = Field(min_length=1)
    description: str = ""
    status: Literal["active", "inactive"] = "active"

    def to_domain(self) -> System:
        payload = self.model_dump(exclude_none=True)
        return System(**payload)


class SystemUpdateRequest(_StrictModel):
    name: str = Field(min_length=1)
    description: str = ""
    status: Literal["active", "inactive"] = "active"


class StakeholderCreateRequest(_StrictModel):
    id: str | None = None
    name: str = Field(min_length=1)
    role: Literal["owner", "reviewer", "auditor"]
    email: str = Field(min_length=3)

    def to_domain(self) -> Stakeholder:
        payload = self.model_dump(exclude_none=True)
        return Stakeholder(**payload)


class PolicyCreateRequest(_StrictModel):
    id: str | None = None
    name: str = Field(min_length=1)
    description: str = ""
    rule_keywords: list[str] = Field(default_factory=list)
    min_compliance_score: float = 80.0
    severity: Literal["low", "medium", "high"] = "medium"

    def to_domain(self, system_id: str) -> Policy:
        payload = self.model_dump(exclude_none=True)
        return Policy(system_id=system_id, **payload)


class EventIngestRequest(_StrictModel):
    system_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    content: str = Field(min_length=1)
    occurred_at: datetime | None = None

    def to_domain(self) -> RawEventInput:
        return RawEventInput(**self.model_dump())


class MetricDefinitionCreateRequest(_StrictModel):
    id: str | None = None
    name: str = Field(min_length=1)
    description: str = ""
    target: Literal["system", "policy", "incident"] = "system"

    def to_domain(self) -> MetricDefinition:
        payload = self.model_dump(exclude_none=True)
        return MetricDefinition(**payload)


class SystemResponse(BaseModel):
    id: str
    name: str
    description: str
    status: Literal["active", "inactive"]
    policy_ids: list[str]
    stakeholder_ids: list[str]
    created_at: datetime

    @classmethod
    def from_domain(cls, system: System) -> "SystemResponse":
        return cls.model_validate(system.model_dump())


class StakeholderResponse(BaseModel):
    id: str
    name: str
    role: Literal["owner", "reviewer", "auditor"]
    email: str
    system_ids: list[str]
    created_at: datetime

    @classmethod
    def from_domain(cls, stakeholder: Stakeholder) -> "StakeholderResponse":
        return cls.model_validate(stakeholder.model_dump())


class PolicyResponse(BaseModel):
    id: str
    system_id: str
    name: str
    description: str
    rule_keywords: list[str]
    min_compliance_score: float
    severity: Literal["low", "medium", "high"]
    created_at: datetime

    @classmethod
    def from_domain(cls, policy: Policy) -> "PolicyResponse":
        return cls.model_validate(policy.model_dump())


class EventResponse(BaseModel):
    id: str
    system_id: str
    source: str
    content: str
    occurred_at: datetime
    risk_category: Literal["low", "medium", "high"]
    incident_type: str
    violated_policy_ids: list[str]
    state: Literal["open", "in-progress", "resolved"]

    @classmethod
    def from_domain(cls, event: Event) -> "EventResponse":
        return cls.model_validate(event.model_dump())


class EvaluationResponse(BaseModel):
    id: str
    system_id: str
    event_id: str
    policy_ids: list[str]
    metric_score_ids: list[str]
    risk_level: Literal["low", "medium", "high"]
    compliance_status: Literal["compliant", "violation"]
    recommended_actions: list[str]
    stakeholder_ids: list[str]
    created_at: datetime

    @classmethod
    def from_domain(cls, evaluation: Evaluation) -> "EvaluationResponse":
        return cls.model_validate(evaluation.model_dump())


class InterventionResponse(BaseModel):
    id: str
    system_id: str
    event_id: str
    evaluation_id: str
    policy_ids: list[str]
    stakeholder_ids: list[str]
    action: str
    state: Literal["open", "in-progress", "resolved"]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, intervention: Intervention) -> "InterventionResponse":
        return cls.model_validate(intervention.model_dump())


class MetricDefinitionResponse(BaseModel):
    id: str
    name: str
    description: str
    target: Literal["system", "policy", "incident"]

    @classmethod
    def from_domain(cls, metric_definition: MetricDefinition) -> "MetricDefinitionResponse":
        return cls.model_validate(metric_definition.model_dump())


class MetricScoreResponse(BaseModel):
    id: str
    metric_id: str
    system_id: str
    value: float
    event_id: str | None
    policy_id: str | None
    timestamp: datetime

    @classmethod
    def from_domain(cls, metric_score: MetricScore) -> "MetricScoreResponse":
        return cls.model_validate(metric_score.model_dump())


class PipelineResultResponse(BaseModel):
    event: EventResponse
    evaluation: EvaluationResponse
    intervention: InterventionResponse | None
    scores: list[MetricScoreResponse]

    @classmethod
    def from_domain(cls, result: PipelineResult) -> "PipelineResultResponse":
        return cls(
            event=EventResponse.from_domain(result.event),
            evaluation=EvaluationResponse.from_domain(result.evaluation),
            intervention=(
                InterventionResponse.from_domain(result.intervention)
                if result.intervention
                else None
            ),
            scores=[MetricScoreResponse.from_domain(score) for score in result.scores],
        )


class IncidentViewResponse(BaseModel):
    event: EventResponse
    evaluations: list[EvaluationResponse]
    interventions: list[InterventionResponse]


class MetricTrendAverageResponse(BaseModel):
    metric_id: str
    metric_name: str
    average: float


class MetricTrendsResponse(BaseModel):
    averages: list[MetricTrendAverageResponse]


class MetricAggregatesResponse(BaseModel):
    totals: dict[str, float]
