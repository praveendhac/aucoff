# AUCoFF Tasks

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.1.0 |
| Owner | TODO |
| Last updated | TODO |

> Purpose: ordered, traceable work breakdown. Every task cites the spec section it implements and has verifiable acceptance criteria.

Related: [spec.md](spec.md) · [design.md](design.md) · [constitution.md](constitution.md)

Status values: `todo` · `in-progress` · `blocked` · `done`

## Phase 0: Foundations
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-001 | Fill in constitution and spec | constitution.md, spec.md | Reviewed and versioned 1.0.0 | - | todo |
| T-002 | Repo scaffold (frontend/, backend/, deploy/) | design.md | Directories and tooling committed | T-001 | todo |

## Phase 1: Backend
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-101 | FastAPI skeleton + health endpoint | backend-spec.md | `/health` returns 200; tests pass | T-002 | todo |
| T-102 | Domain models + migrations | backend-spec.md §4 | Migration applies cleanly | T-101 | todo |
| T-103 | PostgreSQL 18.6 + pgvector schema migrations (tables, indexes) | database-spec.md §3, §5 | Migrations apply from empty DB; ER matches spec | T-102 | todo |
| T-104 | DB roles, grants, TLS and Row-Level Security | database-spec.md §6, constitution DB-3..5 | RLS and privilege tests pass (database-spec.md §10) | T-103 | todo |
| T-105 | Audit log hash chain and append-only enforcement | database-spec.md §3.5 | Chain verification test passes; UPDATE/DELETE denied | T-104 | todo |
| T-106 | Synthetic seed data and catalogue loader (frameworks, unified controls) | spec.md §4, database-spec.md §3.2 | Seed loads; no real data | T-103 | todo |
| T-107 | Auth: OIDC JWT validation, tenant context, RBAC dependencies | backend-spec.md §8 | Unauthorised/cross-tenant calls rejected in tests | T-104 | todo |
| T-108 | OpenAPI pipeline: committed spec, drift check, lint, Swagger/ReDoc | api-contract.md §2 | CI fails on drift or undocumented route | T-101 | todo |
| T-109 | Catalogue/admin APIs (API-1x, API-2x) | api-contract.md §5.1-5.3 | Endpoints documented and tested | T-107, T-108 | todo |
| T-110 | RabbitMQ messaging layer: envelope, outbox relay, DLQs | backend-spec.md §5 | Idempotent consumer tests pass | T-103 | todo |
| T-111 | Snapshot/metric tables (database-spec §3.6): migrations, partitions, immutability grants | database-spec.md §3.6, constitution DB-9 | UPDATE/DELETE denied; monthly partitions created | T-104 | todo |
| T-112 | Snapshot writer at assessment finalisation (same transaction) | design.md §12 | Snapshot and metric points written atomically | T-111, T-202 | todo |
| T-113 | Retention jobs (13-month floor, partition drop, evidence-deletion safe) | database-spec.md §9, DB-10 | History survives evidence deletion in tests | T-111 | todo |
| T-114 | Metrics service and endpoints API-70..72, API-76 (M-01..M-20) | design.md §11, api-contract.md §5.6 | Values match fixture calculations | T-112 | todo |
| T-115 | Compare, history and export endpoints API-73..75 | api-contract.md §5.6 | 12-month seeded-data tests pass | T-112 | todo |

## Phase 2: Agents
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-201 | LLM provider interface, redaction pipeline, cost budgets | backend-spec.md §9, constitution AI-8, AI-12 | Mocked-provider tests; PII redaction tests pass | T-102 | todo |
| T-202 | LangGraph orchestrator + approval interrupts + Postgres checkpointer | agent.md §3 | Run pauses and resumes on approval | T-110, T-201 | todo |
| T-203 | Connector framework (read-only) + first scanner | backend-spec.md §7 | Connector validates read-only access; evidence stored | T-110 | todo |
| T-204 | Remaining scanners (cloud, k8s, repo, saas) | spec.md §5.2, §5.6 | Each service passes contract and eval tests | T-203 | todo |
| T-205 | document-analyzer (RAG, tenant-filtered pgvector) | agent.md §6, DB-6 | Cross-tenant retrieval test passes | T-201 | todo |
| T-206 | mapping-agent, remediation-advisor, report-generator | spec.md §5.6 | Outputs validate against schemas and cite sources | T-202 | todo |
| T-207 | Agent evaluation suite and CI gate | agent.md §11, constitution AI-11 | Gates (citation >= 98%, hallucination <= 1%, agreement >= 90%, redaction >= 99%) enforced in CI | T-202 | todo |
| T-208 | reviewer-agent and citation validator | agent.md §2, §8 | Unresolvable citations rejected in tests | T-202 | todo |
| T-209 | questionnaire-agent: parsing, answer library, drafting with live evidence | agent.md §10, database-spec.md §3.4b | Fixture questionnaires produce cited drafts; stale answers trigger re-scan | T-203, T-205, T-208 | todo |
| T-210 | Redaction pipeline and approval-gated export | agent.md §8, §10, constitution AI-16 | Redaction recall >= 99% on seeded corpus; export blocked without approval | T-209 | todo |
| T-211 | regulatory-change-agent (allow-listed sources, diff proposals) | agent.md §2, FR-20 | Proposals created, never auto-applied | T-202 | todo |
| T-212 | copilot-agent (tenant-scoped retrieval, SSE, refusal when ungrounded) | agent.md §2, FR-21 | Cross-tenant leakage tests pass | T-205 | todo |
| T-213 | Budget enforcement, kill switch, approval expiry | agent.md §3, §4, §9 | Hard stop at 100% budget; approvals expire at 7 days without auto-approval | T-202 | todo |

## Phase 3: Frontend
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-301 | Next.js skeleton + BFF auth shell (Keycloak) | frontend-spec.md §5 | App builds; login flow works | T-002 | todo |
| T-302 | Generated API client + TanStack Query setup | frontend-spec.md §1, §7 | Build fails on contract drift | T-108, T-301 | todo |
| T-303 | Design system components (DataTable, AiBadge, CitationList, ApprovalDialog) | frontend-spec.md §4 | Component and axe tests pass | T-301 | todo |
| T-304 | Catalogue, scopes, connectors, evidence screens | frontend-spec.md §2 | E2E covers create/list flows | T-302, T-109 | todo |
| T-305 | Assessments, run timeline (SSE), result review, approvals | frontend-spec.md §3 | E2E: run, review, approve | T-302, T-202 | todo |
| T-306 | Findings, reports, dashboard, audit log screens | frontend-spec.md §2 | E2E covers key flows | T-305 | todo |
| T-307 | Admin: users, roles, SSO, integrations | frontend-spec.md §2 | Role-gated; E2E passes | T-302 | todo |
| T-308 | Design tokens, theming (light/dark), app shell (sidebar, top bar, drawer) | design.md §10.2-10.4 | Contrast checks automated; axe passes in both themes | T-301 | todo |
| T-309 | Dashboard KPIs, charts and persona presets | design.md §10.5, §10.7, §11 | M-01..M-20 render from API with deltas; data-table alternatives | T-308, T-114 | todo |
| T-310 | Scan comparison, per-control history, history export UI | design.md §12, frontend-spec.md §3.6 | Any-two-scan compare works over 12 months of seeded data | T-309, T-115 | todo |
| T-311 | Questionnaire screens and copilot panel | frontend-spec.md §3.7 | E2E: upload, review, approve, export | T-308, T-209 | todo |

## Phase 4: Infrastructure (local Helm)
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-401 | Dockerfiles for frontend and backend | infrastructure-spec.md §2 | Images build and run | T-101, T-301 | todo |
| T-402 | Helm chart + values-local.yaml | infrastructure-spec.md §3 | `helm install` brings up stack locally | T-401 | todo |
| T-403 | PostgreSQL in Helm chart (PVC, NetworkPolicy, Secrets, migration hook Job) | infrastructure-spec.md §6, database-spec.md §6, §7 | DB reachable only from backend; migrations run on upgrade | T-402, T-104 | todo |
| T-404 | Backup/restore procedure for local DB | database-spec.md §11 | Restore drill documented and passes | T-403 | todo |
| T-405 | RabbitMQ, MinIO, Keycloak in chart; ingress + cert-manager TLS | infrastructure-spec.md §2, §3, §5 | Stack reachable over TLS locally | T-402 | todo |
| T-406 | NetworkPolicies, Pod Security, ServiceAccounts/RBAC | infrastructure-spec.md §4 | Default-deny verified; policy tests pass | T-402 | todo |
| T-407 | Observability stack (OTel, Prometheus, Grafana, Loki, Tempo) + dashboards | infrastructure-spec.md §8 | Traces, logs, metrics visible for a sample run | T-402 | todo |
| T-408 | Makefile local workflow (cluster-up, deploy, seed, e2e) | infrastructure-spec.md §6 | Fresh clone to running stack documented | T-402 | todo |
| T-409 | GitHub Actions pipelines (PR, build, chart, E2E on kind) | infrastructure-spec.md §7 | All required checks gate merges | T-401 | todo |

## Phase 5: AWS (future)
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-501 | Terraform modules (network, EKS, RDS, MQ, S3, IAM, secrets) | infrastructure-spec.md §10 | Plan/apply in a sandbox account | T-409 | todo |
| T-502 | `values-aws.yaml`; verify PostgreSQL 18.x/pgvector on RDS | infrastructure-spec.md §10, database-spec.md §12 | Staging deploy passes smoke/E2E | T-501 | todo |

## Blockers and Notes
TODO
