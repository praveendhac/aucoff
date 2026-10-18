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

## Phase 5: AWS (future)
| ID | Task | Spec ref | Acceptance criteria | Depends on | Status |
|----|------|----------|---------------------|------------|--------|
| T-501 | TODO | infrastructure-spec.md §7 | TODO | T-402 | todo |

## Blockers and Notes
TODO
