# Misalignment Platform orchestration spec

This document describes how the Misalignment Platform’s layers coordinate: data flows, service boundaries, workflows, and deployment orchestration.

---

## 1. High-level architecture orchestration

**Goal:** Turn raw organizational signals (systems, policies, incidents, metrics) into alignment insights and interventions, with traceable workflows.

- **Frontend:** React/TypeScript views and components for systems, policies, incidents, trends, and scores.
- **Backend domain:** Core alignment concepts—systems, policies, metrics, events, evaluations, interventions, stakeholders.
- **Backend engine:** Ingestion, classification, scoring, evaluation, and workflow orchestration.
- **Backend API:** HTTP routes exposing domain and engine capabilities to the frontend and external integrations.
- **Infra/ops:** Azure deployment, configuration, auth, and persistence.

Data flow (simplified):

1. **Ingestion** → 2. **Classification** → 3. **Scoring & Evaluation** → 4. **Workflow orchestration** → 5. **Interventions & Reporting (frontend)**

---

## 2. Domain orchestration (backend/src/domain)

**Purpose:** Provide a stable, expressive model of “alignment” entities and relationships.

- **systems.py**
  - **Responsibility:** Represent AI systems, applications, and contexts under governance.
  - **Orchestration role:** Anchor metrics, policies, events, evaluations, and interventions to a specific system.

- **policies.py**
  - **Responsibility:** Represent alignment policies, constraints, and governance rules.
  - **Orchestration role:** Provide rulesets used by classification, scoring, and evaluation.

- **metrics.py**
  - **Responsibility:** Represent alignment metrics (risk, compliance, robustness, transparency, etc.).
  - **Orchestration role:** Define metric schemas and aggregation logic used by scoring and trends.

- **events.py**
  - **Responsibility:** Represent incidents, logs, and signals (e.g., model outputs, user reports, monitoring alerts).
  - **Orchestration role:** Serve as the primary input to ingestion and classification.

- **evaluations.py**
  - **Responsibility:** Represent evaluation runs, results, and alignment assessments.
  - **Orchestration role:** Connect metrics, policies, and events into structured assessments.

- **interventions.py**
  - **Responsibility:** Represent actions taken to correct or improve alignment (policy changes, model updates, guardrails).
  - **Orchestration role:** Provide a workflow endpoint—what happens after evaluation.

- **stakeholders.py**
  - **Responsibility:** Represent human and organizational actors (owners, reviewers, auditors).
  - **Orchestration role:** Attach accountability and permissions to systems, policies, and interventions.

**Domain orchestration principle:**  
All engine and API operations must express themselves in terms of these domain objects, keeping business logic centralized and consistent.

---

## 3. Engine orchestration (backend/src/engine)

**Purpose:** Implement the alignment engine pipeline: ingest, classify, score, evaluate, and drive workflows.

- **ingestion.py**
  - **Input:** Raw events from logs, webhooks, batch imports, or manual entry.
  - **Output:** Normalized `Event` domain objects.
  - **Orchestration:** Trigger classification once events are persisted.

- **classification.py**
  - **Input:** Normalized events + policies + system context.
  - **Output:** Labeled events (risk categories, policy violations, incident types).
  - **Orchestration:** Feed labeled events into scoring and evaluation.

- **scoring.py**
  - **Input:** Labeled events + metrics definitions.
  - **Output:** Metric scores per system, policy, incident, and time window.
  - **Orchestration:** Update metric aggregates used by `TrendsView` and `ScoreCard`.

- **evaluation.py**
  - **Input:** Scores + policy context + stakeholder configuration.
  - **Output:** `Evaluation` objects (risk level, compliance status, recommended actions).
  - **Orchestration:** Decide whether workflows should be triggered (e.g., incident pipeline, policy review).

- **workflows.py**
  - **Input:** Evaluations + stakeholder roles + system state.
  - **Output:** `Intervention` objects and workflow states (open, in-progress, resolved).
  - **Orchestration:** Coordinate multi-step processes (incident triage, policy updates, model retraining).

**Engine pipeline orchestration:**

1. **Event ingestion**
2. **Event classification**
3. **Metric scoring**
4. **Evaluation generation**
5. **Workflow execution (interventions)**

Each step should be callable independently (for batch jobs, re-runs) and as part of a composed pipeline.

---

## 4. API orchestration (backend/src/api)

**Purpose:** Expose domain and engine capabilities via HTTP routes, with clear boundaries.

- **routes_systems.py**
  - **Endpoints:** CRUD for systems, listing metrics/evaluations per system, linking stakeholders.
  - **Orchestration:** Provide system-centric views for frontend and external integrations.

- **routes_events.py**
  - **Endpoints:** Event ingestion, event listing/filtering, incident views.
  - **Orchestration:** Entry point for external signals and frontend incident pipelines.

- **routes_metrics.py**
  - **Endpoints:** Metric definitions, scores, trends, and aggregates.
  - **Orchestration:** Serve data for dashboards (ScoreCard, TrendsView, PolicyComplianceChart).

**API orchestration principle:**  
Routes should call engine functions and domain services, not embed business logic directly.

---

## 5. Infra orchestration (backend/src/infra + ops/azure)

**Purpose:** Provide secure, configurable, and reproducible deployment and runtime.

- **db_models.py**
  - **Responsibility:** Map domain objects to persistence (tables/collections).
  - **Orchestration:** Ensure all domain entities have consistent storage and relationships.

- **config.py**
  - **Responsibility:** Centralize configuration (DB URLs, feature flags, environment settings).
  - **Orchestration:** Provide a single source of truth for environment-specific behavior.

- **auth.py**
  - **Responsibility:** Authentication and authorization (users, roles, scopes).
  - **Orchestration:** Enforce stakeholder permissions across API routes and workflows.

- **ops/azure/infra-diagram.md**
  - **Responsibility:** Visual representation of services (App Service, DB, Key Vault, etc.).
  - **Orchestration:** Document how components are deployed and connected.

- **ops/azure/deployment-scripts.md**
  - **Responsibility:** Scripts/steps for provisioning and deploying the platform.
  - **Orchestration:** Define repeatable deployment workflows (CI/CD, environment promotion).

---

## 6. Frontend orchestration (frontend/src)

**Purpose:** Present alignment insights and workflows in a coherent, navigable UI.

### 6.1 Views

- **SystemOverview.tsx**
  - **Data:** Systems, key metrics, recent evaluations, open interventions.
  - **Orchestration:** Entry point for exploring a system’s alignment posture.

- **PolicyView.tsx**
  - **Data:** Policies, associated metrics, violations, and evaluations.
  - **Orchestration:** Support policy-centric governance and review workflows.

- **IncidentPipeline.tsx**
  - **Data:** Events, incident states, interventions, stakeholders.
  - **Orchestration:** Visualize and manage the incident workflow from detection to resolution.

- **TrendsView.tsx**
  - **Data:** Metric trends over time, per system/policy.
  - **Orchestration:** Provide longitudinal insight into alignment health.

### 6.2 Components

- **ScoreCard.tsx**
  - **Responsibility:** Display key scores (risk, compliance, robustness) for a system or policy.
  - **Orchestration:** Reusable metric summary component across views.

- **IncidentTable.tsx**
  - **Responsibility:** Tabular view of incidents/events with filters and status.
  - **Orchestration:** Core component for IncidentPipeline and system-level incident lists.

- **PolicyComplianceChart.tsx**
  - **Responsibility:** Visualize compliance vs. violation rates per policy/system.
  - **Orchestration:** Support quick assessment of policy effectiveness.

---

## 7. Orchestrated workflows (end-to-end)

### 7.1 Incident lifecycle

1. **Event ingestion** via `routes_events.py` → `ingestion.py` → `events.py`.
2. **Classification** via `classification.py` using `policies.py` and `systems.py`.
3. **Scoring** via `scoring.py` using `metrics.py`.
4. **Evaluation** via `evaluation.py` producing `evaluations.py` objects.
5. **Workflow** via `workflows.py` creating `interventions.py` and updating incident state.
6. **Frontend** via `IncidentPipeline.tsx` + `IncidentTable.tsx` for human review and action.

### 7.2 Policy governance

1. **Policy definition** in `policies.py` exposed via `routes_systems.py` / `PolicyView.tsx`.
2. **Event classification** uses policies to detect violations.
3. **Metrics & trends** via `metrics.py` and `TrendsView.tsx` / `PolicyComplianceChart.tsx`.
4. **Evaluations** recommend policy changes or interventions.
5. **Stakeholder workflows** via `stakeholders.py` and `workflows.py` for approvals and updates.

---

## 8. Next steps for implementation

**For GitHub Copilot:**

- **Step 1:** Implement domain models (`systems.py`, `policies.py`, `metrics.py`, `events.py`, `evaluations.py`, `interventions.py`, `stakeholders.py`) with clear relationships and methods.
- **Step 2:** Implement engine pipeline modules (`ingestion.py`, `classification.py`, `scoring.py`, `evaluation.py`, `workflows.py`) following the orchestration flows above.
- **Step 3:** Implement API routes (`routes_systems.py`, `routes_events.py`, `routes_metrics.py`) that call domain and engine services.
- **Step 4:** Implement infra layer (`db_models.py`, `config.py`, `auth.py`) and wire it into the backend.
- **Step 5:** Implement frontend views and components, consuming the API endpoints and reflecting the workflows.
- **Step 6:** Align Azure deployment scripts and infra diagram with the actual services used by the backend and frontend.

**For you as founder:**

- **Define:** Concrete metric definitions, policy schemas, and incident categories.
- **Decide:** Which workflows are MVP (incident triage, policy review, system onboarding).
- **Configure:** Stakeholder roles and permissions model.
- **Iterate:** On evaluation logic and scoring formulas as you learn from real usage.

---
