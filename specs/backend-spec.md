# AUCoFF Backend Spec (FastAPI)

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.1.0 |
| Owner | TODO |
| Last updated | TODO |

> Purpose: services, domain logic and persistence behind the API defined in [api-contract.md](api-contract.md).

Related: [spec.md](spec.md) · [design.md](design.md) · [agent.md](agent.md) · [infrastructure-spec.md](infrastructure-spec.md) · [database-spec.md](database-spec.md)

## 1. Tech Choices
- Python version / FastAPI version: TODO
- ORM and migrations: SQLAlchemy 2.x (async) + Alembic (see [database-spec.md](database-spec.md) section 7)
- Database: PostgreSQL 18.6 + pgvector (see [database-spec.md](database-spec.md)); the API sets `SET LOCAL app.tenant_id` per transaction to enforce RLS
- Async/background jobs: TODO
- Validation (Pydantic): TODO
- Testing (pytest, httpx): TODO

## 2. Project Layout
<!-- Proposed package structure. -->
```
backend/
  app/
    api/        # routers
    core/       # config, security
    domain/     # entities, services
    agents/     # agent runtime integration
    db/         # models, migrations
  tests/
```

## 3. Modules and Services
| Module | Responsibility | Depends on | Spec ref |
|--------|----------------|------------|----------|
| TODO | TODO | TODO | FR-? |

## 4. Domain Models
<!-- Fields, constraints, relationships; mirrors design.md data model. -->
TODO

## 5. AuthN / AuthZ
- Identity provider / token format: TODO
- Roles and permissions matrix: TODO
- Tenant scoping: TODO

## 6. Agent Integration
<!-- How the API triggers agent runs, streams results, stores approvals. See agent.md. -->
TODO

## 7. Background Jobs
TODO

## 8. Configuration and Secrets
Env vars, config sources, Kubernetes secrets: TODO

## 9. Logging, Metrics, Tracing
TODO

## 10. Error Handling
Maps to error format in [api-contract.md](api-contract.md): TODO

## 11. Testing Plan
Unit, integration, contract, agent eval: TODO
