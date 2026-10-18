# AUCoFF Design

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.1.0 |
| Owner | TODO |
| Last updated | TODO |

> Purpose: system architecture and key technical decisions that satisfy [spec.md](spec.md) within [constitution.md](constitution.md).

Related: [frontend-spec.md](frontend-spec.md) · [backend-spec.md](backend-spec.md) · [agent.md](agent.md) · [api-contract.md](api-contract.md) · [infrastructure-spec.md](infrastructure-spec.md) · [database-spec.md](database-spec.md)

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
| Relational DB + vector store | System of record, RLS tenancy, embeddings | PostgreSQL 18.6 + pgvector | [database-spec.md](database-spec.md) |
| Scanner / agent microservices | Read-only scans, analysis (see [spec.md](spec.md) section 5.6) | Python | [agent.md](agent.md) |
| Queue / workers | TODO | TODO | - |
| Object store | Evidence files and reports | TODO (local: MinIO?; AWS: S3) | - |

## 4. Data Model
Defined in [database-spec.md](database-spec.md) sections 3 to 5 (tables, ER diagram, indexes). This section only records design-level decisions:
- Single database, tenant isolation by `tenant_id` + Row-Level Security.
- Append-only audit and agent-step tables with hash-chained audit rows.
- Embeddings stored in PostgreSQL via `pgvector`.

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
| ADR-1 | PostgreSQL 18.6 with pgvector as the single data store (relational + vectors) | Separate vector DB (e.g. Qdrant), MySQL | One engine to secure and operate; RLS for multi-tenancy; maps to RDS/Aurora | Accepted (owner) |
| ADR-2 | Multi-tenant SaaS with RLS isolation | Single-tenant per deployment | Required by [spec.md](spec.md) section 5.4 | Accepted (owner) |

## 9. Trade-offs and Risks
TODO

## 10. Open Questions
- [ ] TODO
