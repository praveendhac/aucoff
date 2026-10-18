# AUCoFF Database Spec

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.1.0 |
| Owner | Praveen Darshanam |
| Last updated | 2026-10-18 |

> Purpose: the database engine, schema, migrations and secure configuration for AUCoFF. Implements constitution rules ARC-6, DES-1, COD-9, SEC-2 to SEC-5, SEC-9 to SEC-11 and DB-1 to DB-8.

Related: [constitution.md](constitution.md) · [design.md](design.md) · [backend-spec.md](backend-spec.md) · [agent.md](agent.md) · [infrastructure-spec.md](infrastructure-spec.md) · [api-contract.md](api-contract.md)

## 1. Engine, Name and Versions
| Item | Value | Notes |
|------|-------|-------|
| Engine | PostgreSQL 18.6 | Confirmed by owner |
| Database name | `aucoff` | One database; tenant isolation by `tenant_id` + RLS |
| Vector extension | `pgvector` (version TODO) | Verify the pinned release supports PostgreSQL 18 before adoption |
| Other extensions | `pgcrypto`, `pg_audit` (TODO confirm availability locally and on AWS), `pg_stat_statements` | |
| ORM | SQLAlchemy 2.x (async) | See [backend-spec.md](backend-spec.md) |
| Migrations | Alembic | Versioned, forward-only in prod (COD-9) |
| Driver | `asyncpg` (TODO confirm) | |
| Pooling | PgBouncer (TODO decide local vs AWS RDS Proxy) | |

### Environments
| Env | Deployment | Notes |
|-----|-----------|-------|
| local | PostgreSQL 18.6 + pgvector in the Helm chart (StatefulSet or operator such as CloudNativePG - TODO decide), PVC storage | Synthetic data only (ENV-2) |
| aws (future) | RDS or Aurora PostgreSQL | Confirm 18.x and `pgvector` support at migration time; see section 12 |

## 2. Conventions
- Names: `snake_case`; tables plural; one schema `app` for domain tables, `audit` for the audit log, `ref` for reference data (frameworks, controls).
- Primary keys: UUID v7 (time-ordered), column `id`. (PostgreSQL 18 provides `uuidv7()` natively - verify.)
- Every tenant-owned table has `tenant_id uuid NOT NULL` (ARC-6).
- Timestamps: `timestamptz` in UTC; `created_at`, `updated_at` on mutable tables.
- Append-only tables (DES-1): no `updated_at`; changes are new rows.
- Deletion: soft delete (`deleted_at`) for user-facing entities; hard delete only via the retention job (section 9).
- Enums: PostgreSQL `CHECK` constraints on text columns or lookup tables (avoid native enum types so migrations stay simple).
- JSON: `jsonb` only for flexible payloads (evidence metadata, agent step I/O); core fields are columns.
- Money/scores: `numeric`, never float, where precision matters.

## 3. Tables

### 3.1 Tenancy and identity (`app`)
| Table | Purpose | Key columns |
|-------|---------|-------------|
| `tenants` | Customer organisation | `id`, `name`, `slug` (unique), `region` (data residency), `status`, `created_at` |
| `users` | People | `id`, `tenant_id`, `email` (unique per tenant), `display_name`, `idp_subject`, `status`, `last_login_at` |
| `roles` | Role definitions | `id`, `name` (compliance_officer, auditor, engineer, executive, ciso, admin), `permissions jsonb` |
| `user_roles` | Role assignment | `tenant_id`, `user_id`, `role_id` (PK on the three) |
| `integrations` | SSO, ticketing, notification, SaaS connectors | `id`, `tenant_id`, `type`, `config_ref` (secret reference, never the secret), `status` |

### 3.2 Reference and unified controls (`ref`, shared across tenants, read-only to the app role)
| Table | Purpose | Key columns |
|-------|---------|-------------|
| `frameworks` | Regulation/standard | `id`, `code` (e.g. `pci_dss_4_0_1`), `name`, `version`, `jurisdiction`, `type` (framework, regulation, messaging-standard) |
| `framework_requirements` | Clause-level requirement | `id`, `framework_id`, `ref` (clause number), `title`, `text`, unique(`framework_id`, `ref`) |
| `unified_controls` | Normalised AUCoFF control | `id`, `code`, `title`, `description`, `domain` |
| `control_mappings` | Requirement to unified control | `requirement_id`, `unified_control_id`, `strength`, `rationale`, `source` (human/agent), `approved_by`, `approved_at` |

### 3.3 Assessments (`app`)
| Table | Purpose | Key columns |
|-------|---------|-------------|
| `scopes` | What is assessed (systems, frameworks) | `id`, `tenant_id`, `name`, `framework_ids uuid[]`, `target_refs jsonb` |
| `evidence` | Collected artefact metadata | `id`, `tenant_id`, `scope_id`, `source_type` (cloud, k8s, repo, document, saas), `source_ref`, `object_key` (object store), `sha256`, `collected_at`, `classification` |
| `assessments` | One assessment run set | `id`, `tenant_id`, `scope_id`, `status`, `started_at`, `completed_at`, `created_by` |
| `control_results` | Result per unified control | `id`, `tenant_id`, `assessment_id`, `unified_control_id`, `status` (pass, fail, partial, not_applicable, unknown), `confidence`, `summary`, `agent_run_id`, `reviewed_by`, `reviewed_at` |
| `result_evidence` | Links results to evidence with citations | `control_result_id`, `evidence_id`, `citation` |
| `findings` | Gaps | `id`, `tenant_id`, `control_result_id`, `severity`, `title`, `description`, `recommendation`, `status`, `ticket_ref`, `opened_at`, `closed_at` |
| `reports` | Generated audit reports | `id`, `tenant_id`, `assessment_id`, `format`, `object_key`, `sha256`, `generated_by`, `generated_at` |

### 3.4 Agents and approvals (`app`)
| Table | Purpose | Key columns |
|-------|---------|-------------|
| `agent_runs` | One agent execution | `id`, `tenant_id`, `agent_id`, `assessment_id`, `model`, `model_version`, `prompt_version`, `status`, `input_tokens`, `output_tokens`, `cost_usd numeric`, `started_at`, `finished_at` |
| `agent_steps` | Tool calls and outputs (append-only) | `id`, `tenant_id`, `agent_run_id`, `seq`, `kind`, `input_redacted jsonb`, `output jsonb`, `created_at` |
| `approvals` | Human decisions on agent actions | `id`, `tenant_id`, `agent_run_id`, `action`, `requested_at`, `decided_by`, `decision`, `decided_at`, `comment` |
| `embeddings` | RAG vectors | `id`, `tenant_id` (NULL for shared reference text), `source_type`, `source_id`, `chunk_index`, `content`, `embedding vector(N)` (N depends on embedding model - TODO), `model` |

### 3.5 Audit (`audit`)
| Table | Purpose | Key columns |
|-------|---------|-------------|
| `audit_log` | Immutable security/compliance events (SEC-9) | `id`, `tenant_id`, `occurred_at`, `actor_type`, `actor_id`, `action`, `target_type`, `target_id`, `outcome`, `request_id`, `details jsonb`, `prev_hash`, `row_hash` |

`row_hash = sha256(prev_hash || canonical row)` per tenant, giving tamper evidence (SEC-10).

## 4. Relationships (ER overview)
```mermaid
erDiagram
  tenants ||--o{ users : has
  users ||--o{ user_roles : assigned
  roles ||--o{ user_roles : grants
  frameworks ||--o{ framework_requirements : contains
  framework_requirements ||--o{ control_mappings : maps
  unified_controls ||--o{ control_mappings : maps
  tenants ||--o{ scopes : owns
  scopes ||--o{ evidence : collects
  scopes ||--o{ assessments : assessed_in
  assessments ||--o{ control_results : produces
  unified_controls ||--o{ control_results : evaluated
  control_results ||--o{ result_evidence : cites
  evidence ||--o{ result_evidence : cited_by
  control_results ||--o{ findings : raises
  assessments ||--o{ reports : yields
  assessments ||--o{ agent_runs : triggers
  agent_runs ||--o{ agent_steps : records
  agent_runs ||--o{ approvals : requests
  tenants ||--o{ audit_log : logs
```

## 5. Indexes and Constraints
- B-tree on (`tenant_id`, `id`) for every tenant table; foreign keys always include `tenant_id` where the parent is tenant-owned (composite FK) so cross-tenant links are impossible.
- `control_results`: unique (`assessment_id`, `unified_control_id`); index on (`tenant_id`, `status`).
- `findings`: index on (`tenant_id`, `status`, `severity`).
- `embeddings`: HNSW index on `embedding` (cosine), plus (`tenant_id`, `source_type`, `source_id`). Tenant filter MUST be applied in every similarity query.
- `audit_log`: index on (`tenant_id`, `occurred_at`) and (`tenant_id`, `target_type`, `target_id`); partition by month on `occurred_at`.
- `agent_runs` / `agent_steps`: partition by month once volume warrants (threshold TODO).
- CHECK constraints for status/severity vocabularies; NOT NULL by default.

## 6. Secure Configuration

### 6.1 Roles and privileges (SEC-2)
| DB role | Used by | Privileges |
|---------|---------|------------|
| `aucoff_owner` | Nobody at runtime | Owns objects; no login in prod |
| `aucoff_migrator` | Alembic job | DDL on `app`, `ref`, `audit`; used only during deploy |
| `aucoff_app` | API and workers | DML on `app`; `SELECT` on `ref`; `INSERT`-only on `audit.audit_log`; no DDL; subject to RLS |
| `aucoff_readonly` | Reporting/support | `SELECT` on `app` (subject to RLS); no PII columns where avoidable |
| `aucoff_audit_reader` | Auditor export | `SELECT` on `audit.audit_log` |

No role is superuser; `aucoff_app` has `NOBYPASSRLS`.

### 6.2 Row-Level Security (SEC-11, ARC-6)
- RLS enabled and FORCED on every tenant table.
- Policy: `tenant_id = current_setting('app.tenant_id')::uuid`; the API sets `SET LOCAL app.tenant_id` per transaction from the authenticated token. Missing setting = no rows (fail closed, DES-3).
- Shared reference tables carry no tenant data and are read-only.
- RLS tests are mandatory (section 10).

### 6.3 Authentication and transport
- `scram-sha-256` password auth only; no `trust` or `md5`.
- TLS required (`hostssl` only), TLS 1.2+ ; certificates managed by the platform (cert-manager locally, ACM/RDS CA on AWS).
- Credentials come from Kubernetes Secrets locally and AWS Secrets Manager later; never in images, values files in git, logs or prompts (SEC-3). Rotation procedure TODO.

### 6.4 Encryption
- At rest: encrypted volumes locally where available; KMS-encrypted storage on AWS.
- Column-level: sensitive fields (e.g. integration tokens if stored, evidence classified restricted) encrypted with an application-managed key (`pgcrypto` or app-side envelope encryption, TODO decide). Prefer storing only secret references (`config_ref`).
- Backups encrypted.

### 6.5 Network and hardening
- Database reachable only from backend/worker pods (Kubernetes NetworkPolicy); not exposed via Ingress or NodePort.
- Run as non-root; read-only root filesystem where supported; resource limits set.
- `log_connections`, `log_disconnections`, `log_statement = ddl`; `pg_audit` for role/DDL events (TODO); logs exclude bind values to avoid leaking PII.
- `statement_timeout`, `idle_in_transaction_session_timeout` and `lock_timeout` set for `aucoff_app`.
- Public schema privileges revoked; `search_path` fixed per role.
- Cardholder data (PAN, CVV) MUST NOT be stored (SEC-6); an automated check scans schema and sampled data for PAN patterns.

## 7. Migrations (COD-9)
- Alembic revisions in `backend/app/db/migrations/`; one logical change per revision; names `YYYYMMDD_HHMM_short_description`.
- Never edit a merged revision; fix forward.
- Destructive changes use expand/contract in separate releases.
- Migrations run as `aucoff_migrator` in a Helm pre-upgrade hook Job locally; CI job on AWS.
- Every migration is tested on an empty DB and on the previous release's schema in CI.
- Row-Level Security, grants and extensions are managed in migrations, not by hand.

## 8. Data Classification
| Class | Examples | Handling |
|-------|----------|----------|
| Restricted | Evidence content, credentials references, audit details | Encrypted, access logged, tenant-scoped, minimal retention |
| Confidential | User identity, findings, reports | Encrypted, RBAC |
| Internal | Agent runs metadata, costs | RBAC |
| Public/reference | Framework text (if licensed for use), unified controls | Read-only; check licensing of standard texts (TODO) |

## 9. Retention, Deletion and Residency (SEC-5, SEC-10, SEC-14)
| Data | Retention | Deletion |
|------|-----------|----------|
| Audit log | TODO (proposal: 7 years) | Never edited; partitions dropped only after retention |
| Evidence and reports | TODO per tenant policy | Object + metadata deletion job, logged |
| Agent steps | TODO (proposal: 13 months) | Partition drop |
| User data | Account life + TODO | Erasure on request (GDPR/DPDP) with audit-log pseudonymisation |
- Each tenant has a `region`; tenant data MUST reside only in that region's database/storage (deployment-per-region model TODO in [design.md](design.md)).

## 10. Testing
- Migration tests: up from empty, up from previous version, downgrade where supported.
- RLS tests: for every tenant table, a session with tenant A cannot read or write tenant B and sees nothing when `app.tenant_id` is unset.
- Privilege tests: `aucoff_app` cannot `UPDATE`/`DELETE` `audit_log`, cannot DDL.
- Audit hash chain verification test.
- Embedding queries always include tenant filter (test with two tenants).
- Seed data: synthetic only (ENV-2).

## 11. Backup, Restore and DR
- Local: scheduled `pg_dump`/volume snapshot for developer convenience (TODO).
- AWS: automated backups plus PITR; RPO/RTO targets TODO (proposal: RPO 15 min, RTO 4 h).
- Restore drills documented and rehearsed per phase.

## 12. AWS Migration Notes (future)
| Local | AWS | Notes |
|-------|-----|-------|
| In-cluster PostgreSQL 18.6 | RDS/Aurora PostgreSQL | Confirm 18.x availability; `pgvector` and `pg_audit` support per engine version |
| PgBouncer | RDS Proxy or PgBouncer | TODO |
| K8s Secret credentials | Secrets Manager with rotation | IAM auth optional |
| cert-manager TLS | RDS CA bundle | |
| PVC storage | gp3/io2 with KMS | |

## 13. Open Questions
- [ ] Exact pgvector version and embedding dimension (depends on embedding model).
- [ ] Local deployment: plain StatefulSet vs CloudNativePG operator.
- [ ] Column-level encryption approach and key management.
- [ ] Retention periods and RPO/RTO targets.
- [ ] Tenant region model: one database per region vs per tenant.
- [ ] Licensing for storing framework text (PCI DSS, ISO standards are copyrighted).
