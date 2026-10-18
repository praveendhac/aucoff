# AUCoFF API Contract

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.1.0 |
| Owner | TODO |
| Last updated | TODO |

> Purpose: the contract between frontend and backend. FastAPI's generated OpenAPI must match this document.

Related: [frontend-spec.md](frontend-spec.md) · [backend-spec.md](backend-spec.md) · [database-spec.md](database-spec.md)

## 1. Conventions
- Base URL: `/api/v1` (TODO confirm)
- Format: JSON, UTF-8
- Identifiers: UUID v7 strings; timestamps ISO 8601 UTC
- Tenancy: tenant derived from the authenticated token, never from client-supplied parameters (see [database-spec.md](database-spec.md) section 6.2)
- Versioning policy: TODO
- Auth: `Authorization: Bearer <token>` (TODO confirm)
- Pagination: TODO (cursor vs page)
- Filtering / sorting: TODO
- Idempotency: TODO
- Rate limiting: TODO

## 2. Error Format
```json
{
  "error": {
    "code": "TODO",
    "message": "TODO",
    "details": [],
    "request_id": "TODO"
  }
}
```
Status code usage: TODO

## 3. Auth Scopes / Roles
| Scope | Description | Roles |
|-------|-------------|-------|
| TODO | TODO | TODO |

## 4. Endpoints
| ID | Method | Path | Summary | Auth | Spec ref |
|----|--------|------|---------|------|----------|
| API-1 | GET | `/frameworks` | TODO | TODO | FR-? |
| API-2 | POST | `/assessments` | TODO | TODO | FR-? |
| API-3 | POST | `/agent-runs` | TODO | TODO | FR-? |
| API-4 | POST | `/approvals/{id}/decision` | TODO | TODO | FR-? |

### 4.1 API-1 `GET /frameworks`
- Query params: TODO
- Response 200:
```json
{}
```
- Errors: TODO

<!-- Repeat per endpoint. -->

## 5. Schemas
<!-- Shared object definitions (Framework, Control, Assessment, Finding, AgentRun, Approval). -->
TODO

## 6. Streaming and Events
<!-- SSE / WebSocket for agent progress; webhook payloads. -->
TODO

## 7. Changelog
| Version | Date | Change | Breaking |
|---------|------|--------|----------|
| 0.1.0 | TODO | Initial template | - |
