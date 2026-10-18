# AUCoFF Product Spec

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.7.0 |
| Owner | Praveen Darshanam |
| Last updated | 2026-10-19 |

> Purpose: what AUCoFF (AgenticAI Unified Compliance Framework for Fintechs) must do and why. Describes behaviour, not implementation. Items marked *(proposal)* are suggested values awaiting owner confirmation.

Related: [constitution.md](constitution.md) · [agent.md](agent.md) · [design.md](design.md) · [database-spec.md](database-spec.md) · [api-contract.md](api-contract.md) · [tasks.md](tasks.md)

## 1. Vision
A multi-tenant SaaS in which agentic AI microservices read-only scan a fintech's cloud, Kubernetes, code, SaaS tools and documents, assess them against one unified control set mapped to many regulations and standards, and produce cited findings, remediation guidance and audit-ready reports, with humans approving every consequential outcome.

## 2. Problem Statement
Fintechs must satisfy many overlapping frameworks and regional regulations at once (payments, data protection, financial crime, operational resilience). Teams repeat the same evidence collection per framework, controls are tracked in spreadsheets, audits are slow and costly, and posture drifts between audits. AUCoFF unifies controls, automates evidence collection and analysis, and keeps compliance continuously assessable.

## 3. Personas
| ID | Persona | Goals | Pain points |
|----|---------|-------|-------------|
| PER-1 | Compliance officer | Maintain control mappings, run assessments, approve agent conclusions, prepare for audits | Duplicate work across frameworks, manual evidence chasing |
| PER-2 | Internal / external auditor | Review evidence, findings and the audit trail with confidence | Unverifiable evidence, no traceability |
| PER-3 | Fintech engineer / security team | Understand gaps in their systems and fix them | Vague findings, no technical remediation steps |
| PER-4 | Executive / risk owner | See posture, risk trends and readiness at a glance | No consolidated view |
| PER-5 | CISO | Own security and compliance posture; approve risk acceptance; report to board and regulators | Fragmented tooling, audit surprises |
| PER-6 | Tenant admin | Manage users, roles, SSO, integrations | Manual onboarding |
| PER-7 | Platform operator | Provision and support tenants, manage platform health | Safe access to tenant data when supporting |
| PER-8 | External auditor (time-boxed) | Review a defined slice of evidence, results and audit trail | Getting scoped access without broad privileges |

## 4. Frameworks and Regulations in Scope (all in v1)
| Framework | Version | Jurisdiction | Type | Notes |
|-----------|---------|--------------|------|-------|
| PCI DSS | v4.0.1 | Global | Standard | AUCoFF itself stays out of cardholder-data scope (SEC-6) |
| PCI 3DS | PCI 3DS Core Security Standard (aligned with EMV 3-D Secure v2.x) | Global | Standard | Part 1 baseline security requirements; Part 2 3DS security requirements |
| SOC 2 | AICPA 2017 Trust Services Criteria with revised points of focus (2022/2023) | Global | Attestation framework | Common Criteria (Security) plus optional Availability, Confidentiality, Processing Integrity, Privacy |
| ISO/IEC 27001 | 2022 | Global | Standard | |
| ISO/IEC 27701 | 2025 | Global | Standard | Privacy management extension |
| ISO 20022 | ISO 20022-1:2026 (Edition 3) | Global | Messaging standard | Scoped as data-format / message-handling controls, not a control framework |
| GDPR | EU 2016/679 | EU | Regulation | |
| DPDP | DPDP Act 2023 and DPDP Rules, 2025 (G.S.R. 846(E), 13 Nov 2025) | India | Regulation | Phased compliance timeline; track milestones |
| RBI DPSC | RBI (Commercial Banks - Digital Payment Security Controls) Directions, 2026 (updated as on 1 Oct 2026) | India | Regulation | Evolved from 2021 baseline |
| RBI PPI | RBI Master Directions on Prepaid Payment Instruments (MD-PPI) | India | Regulation | Under Payment and Settlement Systems Act, 2007; periodically updated |
| FFIEC BSA/AML Examination Manual | 2026 reference version | US | Examination guidance | Owner-supplied version |
| FFIEC IT Examination Handbook | Current handbook with 2026 updates | US | Examination guidance | Joint supervisory framework (OCC, FDIC, Federal Reserve, NCUA) |
| FTC Safeguards Rule | 16 CFR Part 314 | US | Regulation | Implements GLBA safeguards: encryption, MFA, risk assessment |
| GLBA | Gramm-Leach-Bliley Act | US | Statute | Assessed through the FTC Safeguards Rule (and FFIEC guidance for banks) |
| NYDFS 23 NYCRR 500 | 23 NYCRR Part 500 including the Second Amendment (fully phased in) | US | Regulation | Third-party and governance obligations |
| PSD2 | Directive (EU) 2015/2366 | EU | Regulation | Watch item: PSD3 (Directive) and the Payment Services Regulation (PSR) are in the EU legislative pipeline |
| DORA | EU 2022/2554 | EU | Regulation | |

Note: instrument names and versions above (except where already stated in earlier drafts) were supplied by the owner on 2026-10-19 and MUST be verified against the official sources before the catalogue is loaded.

Licensing note: standard texts (PCI DSS, ISO, SOC 2 and others) are copyrighted. Per constitution LIC-6, AUCoFF MUST NOT reproduce them verbatim unless licensed; it stores its own summaries and clause/section references only (see [database-spec.md](database-spec.md) section 13).

## 5. Scope Overview
### 5.1 Core capabilities
1. **Unified control mapping** - one AUCoFF control set mapped to all in-scope framework requirements.
2. **Evidence collection and analysis** - read-only collection from connected sources plus uploaded documents; agent analysis.
3. **Gap analysis and remediation** - control results, findings with severity, advisory remediation guidance, ticket creation.
4. **Audit-ready reporting** - exportable reports and evidence packs with citations and approval records.

### 5.2 Evidence sources
| Category | Sources |
|----------|---------|
| Cloud configuration | AWS, GCP, Azure (read-only APIs) |
| Kubernetes / containers | Cluster manifests, Helm values, RBAC, image scan results |
| Code and CI/CD | GitHub, Bitbucket (branch protection, secrets scanning, pipelines, dependency/SAST results) |
| Identity and SaaS | Microsoft Entra ID, Metabase |
| Documents | Uploaded policies, SOPs, reports (PDF, DOCX) |

### 5.3 Integrations
| Type | Systems |
|------|---------|
| Single sign-on | OIDC, SAML |
| Ticketing | Jira, ServiceNow |
| Notifications | Email, Slack, Microsoft Teams |

### 5.4 Tenancy
Multi-tenant SaaS. Strict tenant isolation (see [database-spec.md](database-spec.md), constitution ARC-6, SEC-11). Per-tenant data region.

### 5.5 Autonomy boundaries
Scanning is **read-only**. Agents never change customer systems. Remediation is advisory: agents recommend, humans apply fixes. Consequential outcomes (finalising a control result, accepting risk, publishing a report) require human approval (constitution AI-1, AI-2).

### 5.6 Agentic microservices (v1)
Python microservices coordinated by the backend (see [agent.md](agent.md)); names are proposals.
| Service | Responsibility |
|---------|----------------|
| `mapping-agent` | Maintain and propose mappings between framework requirements and unified controls |
| `cloud-scanner` | Read AWS/GCP/Azure configuration and verify against controls |
| `k8s-scanner` | Verify Kubernetes and container configuration |
| `repo-scanner` | Verify GitHub/Bitbucket and CI/CD settings |
| `saas-scanner` | Verify Entra ID and Metabase configuration |
| `document-analyzer` | Extract and assess evidence from uploaded documents (RAG) |
| `assessment-orchestrator` | Plan and coordinate runs, aggregate control results |
| `remediation-advisor` | Draft findings and remediation guidance |
| `report-generator` | Build cited reports and evidence packs |
| `reviewer-agent` | Independent verification of citations and conclusions before human review |
| `regulatory-change-agent` | Monitor allow-listed official sources and propose catalogue/mapping changes for approval |
| `copilot-agent` | Read-only Q&A on posture, controls and findings with citations |
| `questionnaire-agent` | Draft answers to customer due-diligence questionnaires from the answer library and live evidence |
Full definitions in [agent.md](agent.md) section 2.

## 6. User Stories
| ID | Story | Acceptance criteria | Priority |
|----|-------|---------------------|----------|
| US-1 | As a compliance officer, I want one unified control set mapped to all in-scope frameworks so that I assess once and satisfy many | Each requirement maps to >= 1 unified control; mappings show rationale and approval status | P0 |
| US-2 | As a compliance officer, I want to define an assessment scope (systems and frameworks) so that scans are targeted | Scope saved and used by every scanner in the run | P0 |
| US-3 | As a fintech engineer, I want to connect cloud, Kubernetes, repo and SaaS sources read-only so that evidence is collected automatically | Connection tests pass; only read permissions requested | P0 |
| US-4 | As a compliance officer, I want to upload policy documents so that process controls are assessed | Documents indexed per tenant; analysis cites document passages | P0 |
| US-5 | As a compliance officer, I want agent-generated control results with citations so that I can review and approve them | Every result has status, confidence and evidence citations; approval recorded | P0 |
| US-6 | As an engineer, I want findings with clear remediation steps so that I can fix gaps | Findings include severity, affected resource, steps; can be pushed to Jira/ServiceNow | P0 |
| US-7 | As an auditor, I want to view evidence, results and the immutable audit trail so that I can verify conclusions | Read-only role; tamper-evidence check available | P0 |
| US-8 | As a CISO / executive, I want a posture dashboard by framework so that I see readiness and trends | Coverage %, open findings, trend over time per framework | P1 |
| US-9 | As a compliance officer, I want audit-ready reports per framework so that audits are quicker | Export (PDF and structured) with citations and approvals | P0 |
| US-10 | As a tenant admin, I want SSO and role assignment so that access is controlled | OIDC/SAML login; roles from [database-spec.md](database-spec.md) | P0 |
| US-11 | As a CISO, I want notifications in Slack/Teams/email for findings and approvals so that nothing is missed | Configurable per event type | P1 |
| US-12 | As a compliance officer, I want continuous/scheduled assessments so that drift is detected | Schedules per scope; changes flagged | P1 |
| US-13 | As a CISO, I want to see regional regulation coverage (RBI, DPDP, GDPR, PSD2, DORA, NYDFS) so that I know jurisdictional gaps | Filter results by jurisdiction | P1 |
| US-14 | As a compliance officer, I want to upload a customer's due-diligence questionnaire (Excel/Word/PDF, or SIG/CAIQ/HECVAT/VSA) so that drafted answers are produced from our real environment | Questions parsed; each answer has confidence, citations and evidence timestamps | P0 |
| US-15 | As a compliance officer, I want approved past answers reused and flagged when stale so that responses are fast and consistent | Library answers shown with freshness; stale answers trigger a read-only re-scan | P0 |
| US-16 | As a CISO, I want only approved, redacted answers exported so that sensitive detail is not leaked to customers | Export blocked until approval; sensitive details redacted by default; export audit-logged | P0 |
| US-17 | As a compliance officer, I want to be alerted to regulation or standard changes with proposed mapping updates so that the catalogue stays current | Proposed diffs shown for approval; nothing applied automatically | P1 |
| US-18 | As any user, I want to ask a copilot about my posture, controls and findings and get cited answers | Answers cite sources; refuses when ungrounded; read-only | P2 |
| US-19 | As a compliance officer, CISO or auditor, I want to compare any two scans and see severity counts for the latest scan against the previous two so that I can see progress and regressions | Compare view lists new, resolved, regressed, unchanged items; deltas shown | P0 |
| US-20 | As an executive or auditor, I want 12 months of historical results and trends so that I can show posture over time | 12-month trends by framework, jurisdiction and severity; export as CSV/JSON | P0 |
| US-21 | As a platform operator, I want to provision tenants by invitation and offboard them with export and deletion so that onboarding is controlled | Tenant created with admin invite; offboarding exports data then deletes per policy; both audit-logged | P0 |
| US-22 | As a tenant admin, I want to invite an external auditor with a scope and expiry so that they see only what is needed | Invitation limited to chosen assessments/frameworks; expires automatically; all views audit-logged | P0 |
| US-23 | As a platform operator, I want audited, time-limited break-glass access for support so that tenant data is protected | Grant requires reason, approver and expiry; tenant notified; read-only by default; fully logged | P1 |
| US-24 | As a compliance officer, I want scheduled scans and drift alerts so that changes between audits are caught | Schedules per scope; drift between consecutive scans raises a notification | P1 |

## 7. Functional Requirements
| ID | Requirement | Traces to |
|----|-------------|-----------|
| FR-1 | Maintain framework, requirement and unified-control catalogues with versioning | US-1 |
| FR-2 | Propose and record requirement-to-control mappings; mappings require human approval | US-1 |
| FR-3 | Manage scopes and scheduled/on-demand assessments | US-2, US-12 |
| FR-4 | Connector management for cloud, Kubernetes, repo, SaaS sources with read-only credentials | US-3 |
| FR-5 | Document upload, storage, chunking and embedding per tenant | US-4 |
| FR-6 | Scanner microservices collect evidence and store it with hash and provenance | US-3 |
| FR-7 | Agents produce control results with status, confidence and citations; reviewer approves, rejects or edits | US-5 |
| FR-8 | Findings lifecycle (open, accepted risk, in progress, resolved) with severity | US-6 |
| FR-9 | Ticket creation and status sync with Jira and ServiceNow | US-6 |
| FR-10 | Immutable audit log of security-relevant events | US-7 |
| FR-11 | Dashboards by framework, jurisdiction and time | US-8, US-13 |
| FR-12 | Report generation and export with citations and approval history | US-9 |
| FR-13 | OIDC/SAML SSO, RBAC, tenant admin | US-10 |
| FR-14 | Notifications via email, Slack, Microsoft Teams | US-11 |
| FR-15 | Agent run tracing: model, prompt version, tools, cost | constitution AI-10 |
| FR-16 | Questionnaire ingestion (Excel, Word, PDF, standard templates, link-based drafting only) and question normalisation | US-14 |
| FR-17 | Answer drafting from answer library and live evidence, with on-demand read-only re-scan when evidence is stale | US-14, US-15 |
| FR-18 | Per-answer and batch approval, edit and reject; answer-library management (approve, stale, retire) | US-15, US-16 |
| FR-19 | Redacted export of approved answers with configurable detail level; export audit log | US-16 |
| FR-20 | Regulatory-change monitoring from allow-listed sources with approval-gated catalogue/mapping proposals | US-17 |
| FR-21 | Copilot Q&A with citations, read-only | US-18 |
| FR-22 | Immutable per-assessment snapshots and metric points; 12 months of history queryable | US-19, US-20 |
| FR-23 | Compare any two scans (new, resolved, regressed, unchanged) and show severity counts for the latest scan vs the previous two | US-19 |
| FR-24 | Metrics, trends, dashboards and history export per the catalogue in [design.md](design.md) section 11 | US-8, US-20 |
| FR-25 | Tenant provisioning by invitation, tenant lifecycle states, offboarding with export and deletion workflow | US-21 |
| FR-26 | External auditor invitations with scope and expiry, automatic revocation | US-22 |
| FR-27 | Break-glass access grants for platform operators with approval, expiry, tenant notification and audit | US-23 |
| FR-28 | Scan scheduling (cron-style per scope) and drift detection between consecutive scans | US-24 |
| FR-29 | Deterministic check engine wrapping open-source scanners with versioned rule packs and check-to-control mapping ([backend-spec.md](backend-spec.md) §4a) | US-3, US-5 |
| FR-30 | Notification event catalogue and per-user channel preferences | US-11 |

## 8. Non-Functional Requirements
| ID | Category | Requirement |
|----|----------|-------------|
| NFR-1 | Security | No OWASP Top 10 (web) or OWASP API Security Top 10 vulnerabilities; verified by SAST, DAST and API testing before each release; high/critical findings block release |
| NFR-2 | Security | Meet constitution section 6 (SEC-1 to SEC-14) |
| NFR-3 | Availability | v1 (local kind): services expose health/readiness, recover from pod restarts, and scans degrade gracefully when providers fail; the 99.9% monthly availability target *(proposal)* applies post-v1 once hosted |
| NFR-4 | Performance | API p95 < 500 ms for non-agent calls *(proposal)* |
| NFR-5 | Scan latency and scale | Single-scope assessment completes within TODO (proposal: 30 min for 1,000 resources); N concurrent assessments per tenant TODO; evidence volume per tenant TODO |
| NFR-6 | Data retention | Per [database-spec.md](database-spec.md) section 9; configurable per tenant within regulatory minimums |
| NFR-7 | Data residency | Tenant data stays in its configured region, including LLM processing where required (SEC-14); in v1 all data stays on the developer laptop (only redacted prompts go to the LLM API); regional hosting is post-v1 |
| NFR-8 | Cost | LLM budget per assessment and per tenant per month, enforced with alerts and hard stops (AI-12); numbers TODO |
| NFR-9 | Auditability | Every agent action and approval reproducible from logs (AI-10) |
| NFR-10 | Accessibility | WCAG 2.2 AA |
| NFR-11 | Privacy | PII redacted before LLM calls (AI-8); GDPR/DPDP erasure supported |
| NFR-12 | Deployment scope and portability | **v1 (MVP) is local-only:** build, run and test everything on a developer laptop using kind (minikube not used); no AWS or other cloud hosting in v1. Images and the Helm chart stay portable so a later AWS deployment needs only values changes (ENV-1, ENV-4) |
| NFR-13 | Data retention (history) | Scan/assessment snapshots and metric points retained at least 13 months (12 months visible); tenants may extend but never go below 12 months; snapshots are immutable and survive evidence deletion |
| NFR-14 | UX | Visual design, layout and metrics per [design.md](design.md) section 10 and 11; WCAG 2.2 AA with contrast verified |
| NFR-15 | Licensing and IP compliance | No FOSS licence issue and no plagiarism/copyright issue in any library, software, container image, font, icon, dataset, content or generated output; only items meeting constitution LIC-1 to LIC-8 are used; if an issue exists, the item is not used and an alternative is chosen |
| NFR-16 | Project licence | AUCoFF is released under the MIT License (constitution LIC-9); the root `LICENSE` and package metadata agree |

## 9. LLM Approach
Provider-agnostic cloud LLM API behind an interface (ARC-5), with Anthropic Claude as the default provider. v1 uses Anthropic Claude only, via the provider interface, with redacted data only and US-region processing unless a tenant requires otherwise; a fallback provider and residency-pinned options are revisited with the first EU/India tenants.

## 10. Success Metrics
Detailed definitions and formulas are in the metrics catalogue ([design.md](design.md) section 11): time to audit readiness = M-09, control coverage % = M-02, agent accuracy/citation correctness = M-13, remediation cycle time = M-08.

| Metric | Definition | Target |
|--------|-----------|--------|
| Time to audit readiness | Time from scope definition to an approved audit-ready report | TODO (proposal: -50% vs baseline) |
| Control coverage % | Unified controls with approved result and evidence / in-scope controls | TODO (proposal: >= 90% automated or evidenced) |
| Agent accuracy | Agreement with human reviewers on golden dataset | TODO |
| Citation correctness | % of claims with valid, verifiable citations | TODO (proposal: >= 98%) |
| Finding remediation cycle time | Median time from finding opened to resolved | TODO |

## 10a. Control Catalogue Authorship and Notification Events
- **Unified control catalogue:** the owner authors the v1 unified control set; the `mapping-agent` proposes mappings of framework requirements to those controls, and experts approve them (FR-2). Catalogue and mappings are versioned. Licensing of source texts remains an open question.
- **Notification events (stub):** finding opened/escalated, approval requested/expiring, assessment completed/failed, drift detected, budget threshold reached, regulatory change proposed, questionnaire ready for review, auditor invitation expiring. Channels: in-app, email, Slack, Microsoft Teams (per-user and per-tenant preferences). Templates TODO.
- **Scheduling:** cron-style schedules per scope with timezone; a drift is any change in a control result status or a new/changed failing check between consecutive scans of the same scope.

## 11. Out of Scope (v1)
- Automated remediation or any write access to customer systems.
- Storing or processing cardholder data (PAN, CVV).
- Legal advice or regulator filings submitted automatically.
- Frameworks not listed in section 4.
- Automatic submission of questionnaire answers to external portals (answers are drafted for manual entry).
- Self-service tenant signup and billing (tenants are operator-provisioned and invite-based in v1).
- Any AWS (or other cloud) hosting, Terraform/EKS, managed data services or multi-region deployment in v1; these are post-v1. Cloud scanners still read customer AWS/GCP/Azure accounts (read-only); in v1 they are exercised with recorded fixtures or optional read-only test accounts.

## 12. Assumptions, Risks, Dependencies
| ID | Item | Mitigation |
|----|------|-----------|
| R-1 | **Scope risk:** all listed frameworks in v1 is very large | Phase delivery in [tasks.md](tasks.md) by internal milestones; reuse unified controls to share effort |
| R-2 | Copyright of standard and regulatory texts | Own summaries and clause references only (LIC-6); legal review before any verbatim use; no scraping or copying of paywalled standards |
| R-3 | LLM hallucination in compliance conclusions | Constitution AI rules, citations, approval gates, evaluation suite |
| R-4 | Customer credentials for scanning are high-value targets | Read-only, scoped, short-lived credentials; secrets management (SEC-3) |
| R-5 | Data residency vs LLM provider region | Region-pinned deployments or approved providers (SEC-14) |
| R-6 | Regulation texts change | Versioned catalogues; mapping review process |
| R-7 | FOSS licence or plagiarism issue from libraries, tools, images, content or generated output | Permissive allow-list (LIC-1, LIC-2), verification before adoption (LIC-3), CI licence scan and SBOM (LIC-5), replacement-first policy (LIC-4), originality review of generated content (LIC-8); licence audit task T-009 |
| D-1 | Dependencies | LLM provider, identity providers, Jira/ServiceNow, cloud and SaaS APIs |

## 13. Open Questions
- [ ] Verify owner-supplied instrument names/versions (section 4) against official sources; FFIEC BSA/AML 2026 reference version and ISO 20022-1:2026 (Edition 3) are also owner-supplied and to be verified.
- [ ] How ISO 20022 translates into assessable controls.
- [ ] Numeric targets for NFR-3, NFR-4, NFR-5, NFR-8 and section 10 metrics.
- [ ] Order of delivery of frameworks within v1 (internal milestones).
- [ ] Report formats and templates per framework.
- [ ] Pricing/tenant plan limits (if any) affecting quotas.
- [ ] Which cloud providers and SaaS scanners ship first.
- [ ] Final list of open-source scanners per source after licence review (Steampipe AGPL-3.0, ScoutSuite GPL-2.0, Semgrep/Opengrep engines LGPL-2.1 and the Semgrep rules licence are not approved per the first-pass audit in LICENCES.md; confirm and finish under T-009).
- [ ] Licence audit (T-009) results and the replacements chosen for object store and observability stack.
- [ ] Notification templates and per-event defaults.
- [ ] Tenant offboarding retention exceptions (legal holds).
