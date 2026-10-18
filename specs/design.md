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
Next.js frontend (BFF session) -> FastAPI gateway -> PostgreSQL (+ pgvector) and RabbitMQ -> Python agent microservices (LangGraph) -> read-only external sources, object store and LLM provider. See the diagram in [backend-spec.md](backend-spec.md) section 2; deployment topology in [infrastructure-spec.md](infrastructure-spec.md).

## 3. Components
| Component | Responsibility | Tech | Spec |
|-----------|----------------|------|------|
| Web UI | TODO | Next.js | [frontend-spec.md](frontend-spec.md) |
| API | TODO | FastAPI | [backend-spec.md](backend-spec.md) |
| Agent runtime | TODO | TODO | [agent.md](agent.md) |
| Relational DB + vector store | System of record, RLS tenancy, embeddings | PostgreSQL 18.6 + pgvector | [database-spec.md](database-spec.md) |
| Scanner / agent microservices | Read-only scans, analysis (see [spec.md](spec.md) section 5.6) | Python | [agent.md](agent.md) |
| Queue | Job and event transport | RabbitMQ (AWS: Amazon MQ) | [backend-spec.md](backend-spec.md) §5 |
| Object store | Evidence files and reports | MinIO locally, S3 on AWS | [infrastructure-spec.md](infrastructure-spec.md) |
| Identity provider | OIDC login, SAML brokering | Keycloak locally; Entra ID/Cognito later | [frontend-spec.md](frontend-spec.md) §5 |
| Observability | Logs, metrics, traces | OpenTelemetry, Prometheus, Grafana, Loki, Tempo | [infrastructure-spec.md](infrastructure-spec.md) §8 |

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
| ADR-3 | LangGraph for agent orchestration with Postgres checkpoints | Claude Agent SDK/plain loops, Temporal | Graph state, interrupts for human approval | Accepted (owner) |
| ADR-4 | FastAPI gateway + Python agent services over RabbitMQ | Sync gRPC/HTTP, modular monolith | Decouples long-running scans; retries and DLQs | Accepted (owner) |
| ADR-5 | External OIDC IdP (Keycloak locally) with BFF session in Next.js | Built-in auth, SaaS auth | Enterprise SSO/SAML, no tokens in browser storage | Accepted (owner) |
| ADR-6 | OpenAPI 3.1 as source of truth; generated TS client; Swagger UI for all endpoints | Hand-written clients | Prevents contract drift | Accepted (owner) |
| ADR-7 | kind + umbrella Helm chart locally; Terraform + EKS later | minikube, per-service charts | Same chart across environments | Accepted (owner) |

## 9. Trade-offs and Risks
TODO

## 10. Open Questions
- [ ] TODO
