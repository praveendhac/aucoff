# AUCoFF Design

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.1.0 |
| Owner | TODO |
| Last updated | TODO |

> Purpose: system architecture and key technical decisions that satisfy [spec.md](spec.md) within [constitution.md](constitution.md).

Related: [frontend-spec.md](frontend-spec.md) · [backend-spec.md](backend-spec.md) · [agent.md](agent.md) · [api-contract.md](api-contract.md) · [infrastructure-spec.md](infrastructure-spec.md)

## 1. System Context
<!-- Users, external systems (LLM providers, identity provider, evidence sources). Diagram. -->
TODO

## 2. Architecture Overview
<!-- Next.js frontend -> FastAPI backend -> agent runtime -> data stores. Diagram. -->
TODO

## 3. Components
| Component | Responsibility | Tech | Spec |
|-----------|----------------|------|------|
| Web UI | TODO | Next.js | [frontend-spec.md](frontend-spec.md) |
| API | TODO | FastAPI | [backend-spec.md](backend-spec.md) |
| Agent runtime | TODO | TODO | [agent.md](agent.md) |
| Relational DB | TODO | TODO | - |
| Vector store | TODO | TODO | - |
| Queue / workers | TODO | TODO | - |

## 4. Data Model
<!-- Core entities: Framework, Control, Mapping, Evidence, Assessment, Finding, AuditLog, User, Role. ER diagram. -->
TODO

## 5. Key Data Flows
<!-- e.g. evidence ingestion -> agent analysis -> human approval -> report. -->
TODO

## 6. Security Architecture
- AuthN / AuthZ: TODO
- Data classification and encryption (at rest, in transit): TODO
- Tenant isolation: TODO
- Secrets management: TODO
- Threat model summary: TODO

## 7. Observability
Logs, metrics, traces, alerting: TODO

## 8. Decision Log (ADRs)
| ID | Decision | Alternatives | Rationale | Status |
|----|----------|--------------|-----------|--------|
| ADR-1 | TODO | TODO | TODO | Proposed |

## 9. Trade-offs and Risks
TODO

## 10. Open Questions
- [ ] TODO
