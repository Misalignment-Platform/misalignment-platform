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

- **
