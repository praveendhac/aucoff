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

## Phase 2: Agents
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-201 | TODO | agent.md | TODO | T-102 | todo |

## Phase 3: Frontend
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-301 | Next.js skeleton + auth shell | frontend-spec.md | App builds; login flow works | T-002 | todo |

## Phase 4: Infrastructure (local Helm)
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-401 | Dockerfiles for frontend and backend | infrastructure-spec.md §2 | Images build and run | T-101, T-301 | todo |
| T-402 | Helm chart + values-local.yaml | infrastructure-spec.md §3 | `helm install` brings up stack locally | T-401 | todo |
| T-403 | PostgreSQL in Helm chart (PVC, NetworkPolicy, Secrets, migration hook Job) | infrastructure-spec.md §6, database-spec.md §6, §7 | DB reachable only from backend; migrations run on upgrade | T-402, T-104 | todo |
| T-404 | Backup/restore procedure for local DB | database-spec.md §11 | Restore drill documented and passes | T-403 | todo |

## Phase 5: AWS (future)
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-501 | TODO | infrastructure-spec.md §7 | TODO | T-402 | todo |

## Blockers and Notes
TODO
