# AUCoFF Constitution

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.12.0 |
| Owner | Praveen Darshanam |
| Last updated | 2026-10-19 |

> Purpose: the non-negotiable rules every spec, design decision and code change must obey. If another spec conflicts with this file, this file wins. Rules use RFC 2119 keywords: **MUST**, **MUST NOT**, **SHOULD**, **MAY**. Each rule has an ID so specs, tasks and reviews can cite it.

Related: [spec.md](spec.md) · [design.md](design.md) · [agent.md](agent.md) · [backend-spec.md](backend-spec.md) · [database-spec.md](database-spec.md) · [frontend-spec.md](frontend-spec.md) · [infrastructure-spec.md](infrastructure-spec.md) · [tasks.md](tasks.md)

## 1. Mission and Principles

**Mission:** AUCoFF gives fintechs one agentic AI-assisted framework to map, assess and evidence compliance across multiple regulatory frameworks, with every conclusion traceable and every consequential action approved by a human.

| ID | Principle | Meaning |
|----|-----------|---------|
| P1 | Compliance first | A feature that weakens compliance posture or evidence quality is rejected, however useful. |
| P2 | Traceability | Every finding, mapping and agent output traces to source (control ID, evidence, prompt version, model). |
| P3 | Human accountability | Agents advise; humans decide anything consequential. |
| P4 | Secure and private by default | Least privilege, minimal data, encryption everywhere; opt in to exposure, not out. |
| P5 | Simplicity | Prefer the simplest design that meets the spec; complexity needs a recorded reason. |
| P6 | Spec is truth | Behaviour is defined in `specs/`; code follows specs, never the reverse. |

## 2. Architectural Rules

- **ARC-1** The system MUST be a Next.js (TypeScript) frontend and a FastAPI (Python) backend communicating only through the contract in [api-contract.md](api-contract.md).
- **ARC-2** The frontend MUST NOT access databases, the agent runtime, or LLM providers directly.
- **ARC-3** The backend MUST be layered: `api` (routing/validation) -> `domain` (business rules) -> `db`/`agents` (adapters). Lower layers MUST NOT import upper layers.
- **ARC-4** Business and compliance logic MUST live in `domain`, not in routers, UI components, prompts or SQL.
- **ARC-5** All external dependencies (LLM provider, vector store, identity provider, object store) MUST sit behind an interface so they can be swapped (e.g. local to AWS) without domain changes.
- **ARC-6** Multi-tenancy: every persisted record MUST carry a tenant identifier and every query MUST be tenant-scoped.
- **ARC-7** Services MUST be stateless; state lives in the database, queue or object store, so they run unchanged on local Kubernetes and AWS.
- **ARC-8** Configuration MUST come from environment/Helm values (12-factor); no environment-specific values in code.
- **ARC-9** Long-running agent work MUST run asynchronously (queue/worker) with status polling or streaming, never block a request.
- **ARC-10** Significant architectural decisions MUST be recorded as an ADR in [design.md](design.md) before implementation.
- **ARC-11** Infrastructure MUST be declared as code (Helm and kind configuration in v1; IaC for a hosted environment is post-v1); no manual cluster changes.

## 3. Design Philosophy

- **DES-1** Design for audit: model data as append-only where history matters (assessments, approvals, agent runs); corrections are new records, not edits.
- **DES-2** Explicit over implicit: typed schemas, explicit errors, no hidden global state or magic defaults.
- **DES-3** Fail closed: on uncertainty, missing authorisation or invalid agent output, deny or escalate to a human.
- **DES-4** Idempotent operations: retried requests, jobs and agent runs MUST NOT duplicate side effects.
- **DES-5** Small, composable modules with a single responsibility; prefer composition over inheritance.
- **DES-6** Do not build for hypothetical requirements; build what the current spec requires (YAGNI), but keep boundaries (ARC-5) clean.
- **DES-7** Contract first: change [api-contract.md](api-contract.md) before changing endpoints; the OpenAPI output MUST match it.

## 4. Coding Standards

| ID | Rule |
|----|------|
| COD-1 | Python: version pinned in repo; formatted and linted with Ruff; fully type-annotated and checked with mypy (strict for `domain`). |
| COD-2 | TypeScript: `strict` mode on; ESLint + Prettier; no `any` without a justification comment. |
| COD-3 | Names reveal intent; functions do one thing; avoid functions over ~50 lines or deep nesting. |
| COD-4 | Comments explain *why*, not *what*; no commented-out code or untracked TODOs (TODOs MUST reference a task ID from [tasks.md](tasks.md)). |
| COD-5 | Validate all external input at the boundary (Pydantic on the backend, schema validation on the frontend). |
| COD-6 | Errors MUST use the error format in [api-contract.md](api-contract.md); never swallow exceptions silently. |
| COD-7 | Dependencies MUST be pinned via lockfiles, justified, license-checked and kept minimal. |
| COD-8 | Logging MUST be structured (JSON) with a request/correlation ID; MUST NOT log secrets, credentials or PII. |
| COD-9 | Database changes MUST be versioned migrations, reversible where feasible, never edited after merge. |
| COD-10 | Git: small focused commits, imperative messages, branches reviewed via pull request; `main` stays releasable. |

## 5. Quality and Testing Baselines

| ID | Rule |
|----|------|
| QA-1 | Every task has acceptance criteria and is not done until they are verified by a test or a documented manual check. |
| QA-2 | Test pyramid: many unit tests, fewer integration/contract tests, few end-to-end tests. |
| QA-3 | Coverage floor: >= 80% line coverage overall and >= 90% for `domain`; coverage MUST NOT decrease in a PR. (Targets reviewable; see section 10.) |
| QA-4 | Bug fixes MUST include a regression test that fails before the fix. |
| QA-5 | API contract tests MUST confirm backend responses match [api-contract.md](api-contract.md). |
| QA-6 | Agent behaviour MUST be covered by an evaluation suite (see section 7) run in CI; regressions block merge. |
| QA-7 | CI MUST run lint, type checks, tests, dependency and secret scans on every PR; a failing check blocks merge. |
| QA-8 | Tests MUST be deterministic and independent; LLM calls in unit/integration tests are mocked or replayed. |
| QA-9 | Performance and availability targets come from NFRs in [spec.md](spec.md) and are checked before release. |
| QA-10 | Accessibility target: WCAG 2.2 AA for all UI. |
| QA-11 | Definition of done: code reviewed, tests green, spec/docs updated, migrations included, no new scan findings, observability added, licence scan clean and licence register updated (LIC-3, LIC-5). |

## 6. Security and Compliance

| ID | Rule |
|----|------|
| SEC-1 | Authentication is required on **every** endpoint without exception (see section 7d, ZT-1 to ZT-9); authorisation is role-based and enforced server-side (never only in the UI). |
| SEC-2 | Least privilege for users, services, database roles and Kubernetes service accounts. |
| SEC-3 | Secrets MUST NOT be in source control, images, logs or prompts; in v1 they come from Kubernetes Secrets on the local cluster (a managed secret store is a post-v1 option). A pre-commit secret scan (Gitleaks) MUST remain enabled. |
| SEC-4 | Encrypt in transit (TLS) and at rest for all sensitive data. |
| SEC-5 | Data classification: PII, financial and regulated data are classified; the highest class sets handling rules. Collect and retain the minimum needed, with defined retention and deletion. |
| SEC-6 | Cardholder data (PAN, CVV) MUST NOT be stored or processed by AUCoFF; keep the system out of PCI DSS cardholder-data scope. |
| SEC-7 | Follow OWASP ASVS/Top 10: input validation, output encoding, CSRF/XSS/SSRF/injection defences, secure headers, rate limiting. |
| SEC-8 | Containers run as non-root with minimal base images, scanned for vulnerabilities; critical/high findings block release. |
| SEC-9 | Every security-relevant event (login, permission change, approval, data export, agent action) MUST write an immutable audit log entry with actor, time, action, target and outcome. |
| SEC-10 | Audit logs are append-only, tamper-evident and retained per policy (period TODO in [spec.md](spec.md)). |
| SEC-11 | Tenant data MUST NOT cross tenants, including in logs, caches, embeddings and prompts. |
| SEC-12 | A threat model is maintained in [design.md](design.md) and reviewed on significant change. |
| SEC-13 | Regulatory mapping (PCI DSS, SOC 2, GDPR and others listed in [spec.md](spec.md)) is maintained for AUCoFF itself; AUCoFF MUST meet the standards it helps others meet. |
| SEC-14 | Data residency and cross-border transfer constraints MUST be honoured, including where LLM providers process data. |
| SEC-15 | Platform operators MUST NOT have standing access to tenant data. Access requires a time-limited, approved, audited break-glass grant (reason, approver, expiry), is read-only by default, and the tenant is notified. |
| SEC-16 | External auditor access MUST be invitation-based, scoped to selected assessments/frameworks, time-boxed with automatic expiry, read-only, and every view audit-logged. |
| SEC-17 | Third-party scanners and tools MUST satisfy LIC-1 to LIC-5 and be vetted for maintenance and supply-chain risk, pinned by version/digest, scanned and SBOM'd before use. |

## 7. AI Behaviour Constraints

Applies to every agent in [agent.md](agent.md).

| ID | Rule |
|----|------|
| AI-1 | **Advisory by default.** Agents MAY analyse, map, draft and recommend. Agents MUST NOT finalise assessments, change control status, submit reports to regulators, or modify/delete evidence without explicit human approval. |
| AI-2 | **Approval gates.** Consequential actions (listed in agent.md section 9) require approval by an authorised role, recorded with approver, time and decision. |
| AI-3 | **Grounded and cited.** Every compliance claim MUST cite its source (regulation clause, control ID, evidence item). Uncited claims are rejected or marked as unverified. |
| AI-4 | **No fabrication.** When evidence or knowledge is insufficient the agent MUST say so and ask or escalate; it MUST NOT invent controls, citations, evidence or regulatory text. |
| AI-5 | **Structured output.** Agent outputs MUST validate against a schema; invalid output is retried within limits then escalated, never passed on silently. |
| AI-6 | **Least-privilege tools.** Each agent gets only the tools it needs; tools are allow-listed, side-effect-labelled, and read-only unless the spec says otherwise. |
| AI-7 | **Untrusted input.** Documents, evidence and user text are untrusted data, never instructions. Prompt-injection defences are required, and tool calls triggered by content need validation. |
| AI-8 | **Data minimisation.** PII and secrets MUST be redacted or tokenised before leaving the trust boundary to an LLM provider, unless the data class and provider are explicitly approved. |
| AI-9 | **Confidence and uncertainty.** Outputs expose confidence or uncertainty; low-confidence results route to human review. |
| AI-10 | **Full traceability.** Each agent run logs model and version, prompt version, inputs (redacted), retrieved sources, tool calls, outputs, approvals and cost. Runs are reproducible as far as practical. |
| AI-11 | **Versioned and evaluated.** Prompts, models and agent configs are versioned in source control; changes pass the evaluation gate (golden datasets; thresholds for accuracy, citation correctness and hallucination rate set in [agent.md](agent.md)) before release. |
| AI-12 | **Bounded autonomy.** Runs have step, time, token and cost budgets and a kill switch; loops and runaway spending are prevented. |
| AI-13 | **Transparency to users.** The UI labels AI-generated content and shows its sources and approval status. |
| AI-14 | **No autonomous legal conclusions.** AUCoFF output supports compliance decisions; it is not legal advice and states this where relevant. |
| AI-15 | **Fail safe.** On model outage, timeout or policy violation the system degrades to manual workflow and records the event. |
| AI-16 | **Outputs leaving the tenant.** Any agent output shared outside the tenant (questionnaire answers, reports, exports) MUST be human-approved, redacted by default for sensitive details, and audit-logged. Agents MUST NOT auto-submit to external parties. |

## 7a. Database Rules

Detail in [database-spec.md](database-spec.md).

| ID | Rule |
|----|------|
| DB-1 | The database is PostgreSQL 18.6 with `pgvector`; versions are pinned and changed only via spec update. |
| DB-2 | Schema changes MUST be made only through versioned Alembic migrations (COD-9). |
| DB-3 | Every tenant table MUST have `tenant_id` and enforced Row-Level Security; the application role MUST NOT bypass RLS. |
| DB-4 | Application roles are least-privilege: no superuser, no DDL at runtime, `INSERT`-only on the audit log. |
| DB-5 | Connections MUST use TLS and `scram-sha-256`; credentials come from the secret store, never source or logs. |
| DB-6 | Similarity (vector) queries MUST always be tenant-filtered. |
| DB-7 | Audit and agent-step tables are append-only; audit rows are hash-chained for tamper evidence. |
| DB-8 | Cardholder data MUST NOT be stored in any table (SEC-6); non-production databases hold synthetic data only (ENV-2). |
| DB-9 | Assessment snapshots and metric points are immutable once written; the application role has no UPDATE/DELETE on them; corrections are new versions. |
| DB-10 | At least 12 months of snapshot and metric history MUST be retained and queryable (stored 13); tenant retention may be extended but never below 12 months, and history MUST survive evidence deletion. |

## 7b. API Rules

Detail in [api-contract.md](api-contract.md).

| ID | Rule |
|----|------|
| APIR-1 | Every endpoint MUST be documented in the generated OpenAPI 3.1 spec (Swagger UI/ReDoc) with schemas, examples, errors and required scopes; undocumented routes MUST NOT merge. |
| APIR-2 | The committed OpenAPI file MUST match the generated one; CI fails on drift, and the frontend client is generated from it. |
| APIR-3 | Endpoints are versioned under `/api/v1`; breaking changes need a new major version and deprecation period. |
| APIR-4 | State-changing POSTs that create or trigger work MUST support `Idempotency-Key`; list endpoints MUST use cursor pagination. |
| APIR-5 | Errors use RFC 9457 problem details with a request ID and never expose internals. |
| APIR-6 | The OWASP Top 10 and OWASP API Security Top 10 are release gates (NFR-1). |

## 7c. Licensing, Provenance and Content Rules

AUCoFF MUST NOT contain, depend on, or distribute anything that creates a free/open-source (FOSS) licence issue or a plagiarism/copyright issue. Anything freely available on the internet (libraries, tools, container images, fonts, icons, illustrations, datasets, prompts, text, standards) is **not** automatically free to use. If an item has a licence or provenance issue, it MUST NOT be used; an alternative MUST be found instead.

| ID | Rule |
|----|------|
| LIC-1 | **Permissive allow-list only.** Third-party code, tools, images and fonts MUST use one of: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, PostgreSQL licence, MPL-2.0 (unmodified), SIL OFL (fonts), or equivalent permissive terms reviewed by the owner. |
| LIC-2 | **Disallowed:** AGPL, GPL, LGPL, SSPL, BUSL/BSL, "source-available", non-commercial or field-of-use restricted licences, unlicensed code, and anything with unclear or unverifiable provenance - including transitive dependencies and container base images. **Exception for base images (owner decision 2026-10-19):** unmodified operating-system packages that ship inside an *official minimal* base image (for example `python:3.13-slim`, `node:22-slim`) are treated as mere aggregation and do not make AUCoFF a derivative work; the rule still applies in full to AUCoFF's own code and to every language-level (pip/npm/other) dependency. Base images MUST NOT be modified or have copyleft software added to them, MUST be pinned by digest, scanned, and recorded in `LICENCES.md`. |
| LIC-3 | **Check before adoption.** The licence of every direct and transitive dependency, tool, image, font, icon, dataset and content item MUST be verified from the official source and recorded in the licence register before use. Training-data knowledge or assumptions are not sufficient. |
| LIC-4 | **Replacement first.** If a licence or provenance issue is found at any time, the item MUST be removed and replaced with an alternative that meets LIC-1; the decision is recorded in the licence register (and an ADR if architectural). |
| LIC-5 | **Automated enforcement.** CI MUST generate an SBOM and run a licence scan that fails the build on any disallowed or unknown licence; exceptions are not allowed without an owner-approved, time-limited ADR. |
| LIC-6 | **No copied content.** Code, text, standards and regulatory wording, images, icons, fonts, prompts, test data and documentation MUST NOT be copied from the internet or other sources unless their licence permits it (LIC-1) and attribution requirements are met. Standards text (PCI DSS, ISO, SOC 2, etc.) MUST NOT be reproduced verbatim unless licensed; AUCoFF stores its own summaries and clause references only. |
| LIC-7 | **Attribution and notices.** Required attributions and licence texts are kept in a NOTICE/licence register that ships with the product. |
| LIC-8 | **Generated content.** AI-generated code, text, reports, prompts and questionnaire answers MUST NOT reproduce copyrighted or third-party material; generated deliverables are reviewed for originality (similarity checks where practical) before release, and source citations point to references instead of copying wording. |

AUCoFF's own licence:

| ID | Rule |
|----|------|
| LIC-9 | AUCoFF is licensed under the MIT License, Copyright (c) 2026 Praveen Darshanam. The root `LICENSE` file and the `license` metadata in `backend/pyproject.toml` and `frontend/package.json` MUST agree. Changing the project licence needs an owner decision recorded in this constitution and in `LICENCES.md`. Contributions are accepted only under the same licence, and only from people who may license them. |

## 7d. Authentication Everywhere (zero trust)

Owner requirement (2026-10-19): every REST API call uses an authentication token; there is no unauthenticated internal or external API; microservice-to-microservice and microservice-to-database calls are authenticated. Network position (cluster, namespace, NetworkPolicy) is never a substitute for authentication.

| ID | Rule |
|----|------|
| ZT-1 | **No anonymous endpoints.** Every HTTP, SSE, WebSocket or gRPC endpoint of every AUCoFF component (gateway, agent services, BFF route handlers, operator console, webhooks, API documentation, OpenAPI document, health, readiness, metrics, debug) MUST require a valid credential. Frameworks MUST be configured default-deny: a route without an explicit authentication requirement is rejected at start-up or at review, not served. |
| ZT-2 | **The only carve-outs** are mechanisms whose purpose is to establish authentication, and they are not application REST APIs: (a) the browser's OIDC authorization-code login, callback and logout handled by the BFF (protected by PKCE, state and nonce; they expose no application data); (b) the identity provider's own protocol endpoints (discovery, JWKS, token), which are public or client-authenticated by design; (c) static UI shell assets (HTML/JS/CSS/fonts of the login and app shell), which contain no tenant data. Inbound webhooks are *not* a carve-out: they are authenticated by HMAC signature and timestamp (the shared secret is the credential). |
| ZT-3 | **Users:** API calls carry an OIDC access token (`Authorization: Bearer`) validated for signature, issuer, audience, expiry and scopes on every request. The browser never holds tokens; the BFF keeps them server-side behind an `httpOnly` session cookie (frontend-spec section 5). |
| ZT-4 | **Services:** every service has its own identity (a confidential client in the identity provider) and calls other services with a short-lived, audience-scoped token obtained through the OAuth2 client-credentials flow, over TLS. Callees validate the token and authorise by scope (least privilege). No shared service secrets, no long-lived static API keys between services, no trust based on source network. |
| ZT-5 | **Messaging:** the broker requires authentication (per-service users, no default/guest account), TLS, and per-service permissions limited to that service's queues and exchanges. Consumers verify that a message's declared sender matches the broker-authenticated publisher and re-validate tenant context. |
| ZT-6 | **Data stores:** every service authenticates to PostgreSQL, the object store and any other store with its **own** credential or client certificate (PostgreSQL: `scram-sha-256` or certificate over TLS; never `trust`, `peer` over the network, or a shared account), mapped to least-privilege roles (DB-4). Credentials come from the secret store, are unique per service and environment, and are rotatable. |
| ZT-7 | **Probes and telemetry:** Kubernetes liveness/readiness probes MUST NOT call anonymous HTTP endpoints; they use `exec` probes (an in-container health-check command) or authenticated calls. Metrics, logs and traces are pushed to the collector with an authenticated identity or scraped over an authenticated channel; dashboards sit behind SSO. |
| ZT-8 | **Enforcement:** CI MUST include an automated authentication-coverage test that enumerates all routes of every service (framework route table and OpenAPI) and asserts `401` without credentials and `403` with insufficient scope; it MUST also fail on `httpGet` probes, Services/Ingresses exposing unauthenticated paths, and database/broker configurations that allow unauthenticated access. |
| ZT-9 | **No bypass, anywhere.** There is no "auth disabled", "dev mode", debug-token or allow-all setting in code or configuration, including on the local kind cluster and in tests (tests mint tokens from a test identity provider/keys instead). Authentication failures fail closed and are audit-logged without logging the credential. |

## 8. Spec-Driven Development Rules

- **SDD-1** No behaviour change without a spec change in the same PR or earlier.
- **SDD-2** Every task in [tasks.md](tasks.md) cites the spec section and rule IDs it implements.
- **SDD-3** Specs use stable IDs (US-, FR-, NFR-, API-, ADR-, T-) and are never renumbered.
- **SDD-4** Spec status moves Draft -> Review -> Approved; implementation starts only on Approved sections.
- **SDD-5** Deviations from a spec require recording a decision (ADR) and updating the spec.

## 9. Environment Rules

- **ENV-1** Container images and the Helm chart MUST stay environment-neutral so a future hosted deployment (e.g. AWS) differs only by values; v1 itself deploys only to a local kind cluster.
- **ENV-2** Real regulated or customer data MUST NOT be used in local/dev environments; use synthetic data.
- **ENV-3** The post-v1 AWS migration notes in [infrastructure-spec.md](infrastructure-spec.md) are informational and SHOULD be updated when a local component is added; they do not gate v1.
- **ENV-4** v1 (MVP) MUST be buildable, runnable and fully testable on a developer laptop with kind (minikube is not used), with no AWS or other cloud hosting; the only external dependencies allowed are the LLM API (with a recorded/mock mode for offline tests) and optional read-only scan targets. Cloud hosting work is out of scope until after v1.

## 10. Governance

- Owner and sole amender while the project is single-maintainer: Praveen Darshanam.
- Amendments are made by pull request, bump the version (MAJOR: rule removed/relaxed; MINOR: rule added; PATCH: clarification) and add a changelog row.
- Exceptions to a rule require a recorded ADR with rationale, scope and expiry date.
- Thresholds marked reviewable (e.g. QA-3) are revisited at each phase boundary in [tasks.md](tasks.md).

## 11. Open Items
- [ ] Confirm coverage thresholds (QA-3).
- [ ] Define audit log retention period (SEC-10).
- [x] LLM providers: Anthropic Claude only for v1 via the provider interface; redacted data only; US region unless a tenant requires otherwise. Fallback provider and residency-pinned options to be revisited with the first EU/India tenants (AI-8, SEC-14).
- [x] Frameworks in scope for SEC-13 are listed in [spec.md](spec.md) section 4 (still need exact versions).

## 12. Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | 2026-10-18 | Initial template |
| 0.2.0 | 2026-10-18 | Added architectural, design, coding, quality, security and AI rules |
| 0.3.0 | 2026-10-18 | Added database rules DB-1 to DB-8; frameworks in scope resolved |
| 0.4.0 | 2026-10-18 | Added API rules APIR-1 to APIR-6 |
| 0.5.0 | 2026-10-18 | Added AI-16 (outputs leaving the tenant) |
| 0.6.0 | 2026-10-19 | Added DB-9, DB-10 (immutable 12-month history) |
| 0.7.0 | 2026-10-19 | Added SEC-15 (break-glass), SEC-16 (auditor access), SEC-17 (third-party scanner vetting) |
| 0.8.0 | 2026-10-19 | Added licensing, provenance and content rules LIC-1 to LIC-8; QA-11 and SEC-17 updated |
| 0.9.0 | 2026-10-19 | v1 is local-only (kind): ENV-4 added; ARC-11, SEC-3, ENV-1, ENV-3 reworded |
| 0.10.0 | 2026-10-19 | AUCoFF relicensed from AGPL-3.0 to MIT: LIC-9 added |
| 0.11.0 | 2026-10-19 | LIC-2: unmodified OS packages in official minimal base images allowed as mere aggregation |
| 0.12.0 | 2026-10-19 | Authentication everywhere: ZT-1 to ZT-9 added; SEC-1 tightened (no health-check exception) |
