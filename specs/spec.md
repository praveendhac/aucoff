# AUCoFF Product Spec

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.2.0 |
| Owner | Praveen Darshanam |
| Last updated | 2026-10-18 |

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
| PER-6 | Platform admin (tenant admin) | Manage users, roles, SSO, integrations | Manual onboarding |

## 4. Frameworks and Regulations in Scope (all in v1)
| Framework | Version | Jurisdiction | Type | Notes |
|-----------|---------|--------------|------|-------|
| PCI DSS | v4.0.1 | Global | Standard | AUCoFF itself stays out of cardholder-data scope (SEC-6) |
| PCI 3DS | TODO version | Global | Standard | 3-D Secure core security requirements |
| SOC 2 | Trust Services Criteria (TODO year) | Global | Attestation framework | |
| ISO/IEC 27001 | 2022 | Global | Standard | |
| ISO/IEC 27701 | 2025 | Global | Standard | Privacy management extension |
| ISO 20022 | TODO | Global | Messaging standard | Scoped as data-format / message-handling controls, not a control framework |
| GDPR | EU 2016/679 | EU | Regulation | |
| DPDP | Act 2023, 2025 rules (TODO confirm) | India | Regulation | |
| RBI DPSC | TODO exact instrument | India | Regulation | Digital payment security controls |
| RBI PPI | TODO exact instrument | India | Regulation | Prepaid payment instruments |
| FFIEC BSA/AML Examination Manual | TODO edition | US | Examination guidance | |
| FTC Safeguards Rule | 16 CFR Part 314 | US | Regulation | |
| GLBA | TODO | US | Regulation | |
| NYDFS 23 NYCRR 500 | TODO | US | Regulation | |
| PSD2 | TODO | EU | Regulation | |
| DORA | EU 2022/2554 | EU | Regulation | |

Licensing note: standard texts (PCI DSS, ISO) are copyrighted; how they are stored and displayed is an open question (see [database-spec.md](database-spec.md) section 13).

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

## 8. Non-Functional Requirements
| ID | Category | Requirement |
|----|----------|-------------|
| NFR-1 | Security | No OWASP Top 10 (web) or OWASP API Security Top 10 vulnerabilities; verified by SAST, DAST and API testing before each release; high/critical findings block release |
| NFR-2 | Security | Meet constitution section 6 (SEC-1 to SEC-14) |
| NFR-3 | Availability | 99.9% monthly API availability *(proposal)*; scans degrade gracefully when providers fail |
| NFR-4 | Performance | API p95 < 500 ms for non-agent calls *(proposal)* |
| NFR-5 | Scan latency and scale | Single-scope assessment completes within TODO (proposal: 30 min for 1,000 resources); N concurrent assessments per tenant TODO; evidence volume per tenant TODO |
| NFR-6 | Data retention | Per [database-spec.md](database-spec.md) section 9; configurable per tenant within regulatory minimums |
| NFR-7 | Data residency | Tenant data stays in its configured region, including LLM processing where required (SEC-14) |
| NFR-8 | Cost | LLM budget per assessment and per tenant per month, enforced with alerts and hard stops (AI-12); numbers TODO |
| NFR-9 | Auditability | Every agent action and approval reproducible from logs (AI-10) |
| NFR-10 | Accessibility | WCAG 2.2 AA |
| NFR-11 | Privacy | PII redacted before LLM calls (AI-8); GDPR/DPDP erasure supported |
| NFR-12 | Portability | Same images and Helm chart for local Kubernetes and AWS (ENV-1) |

## 9. LLM Approach
Provider-agnostic cloud LLM API behind an interface (ARC-5), with Anthropic Claude as the default provider. Approved providers and data classes allowed per provider remain to be decided (constitution open items).

## 10. Success Metrics
| Metric | Definition | Target |
|--------|-----------|--------|
| Time to audit readiness | Time from scope definition to an approved audit-ready report | TODO (proposal: -50% vs baseline) |
| Control coverage % | Unified controls with approved result and evidence / in-scope controls | TODO (proposal: >= 90% automated or evidenced) |
| Agent accuracy | Agreement with human reviewers on golden dataset | TODO |
| Citation correctness | % of claims with valid, verifiable citations | TODO (proposal: >= 98%) |
| Finding remediation cycle time | Median time from finding opened to resolved | TODO |

## 11. Out of Scope (v1)
- Automated remediation or any write access to customer systems.
- Storing or processing cardholder data (PAN, CVV).
- Legal advice or regulator filings submitted automatically.
- Frameworks not listed in section 4.

## 12. Assumptions, Risks, Dependencies
| ID | Item | Mitigation |
|----|------|-----------|
| R-1 | **Scope risk:** all listed frameworks in v1 is very large | Phase delivery in [tasks.md](tasks.md) by internal milestones; reuse unified controls to share effort |
| R-2 | Licensing of standard texts | Legal review; store references/summaries rather than full text where required |
| R-3 | LLM hallucination in compliance conclusions | Constitution AI rules, citations, approval gates, evaluation suite |
| R-4 | Customer credentials for scanning are high-value targets | Read-only, scoped, short-lived credentials; secrets management (SEC-3) |
| R-5 | Data residency vs LLM provider region | Region-pinned deployments or approved providers (SEC-14) |
| R-6 | Regulation texts change | Versioned catalogues; mapping review process |
| D-1 | Dependencies | LLM provider, identity providers, Jira/ServiceNow, cloud and SaaS APIs |

## 13. Open Questions
- [ ] Exact versions/instruments for PCI 3DS, SOC 2 TSC, RBI DPSC, RBI PPI, DPDP rules, FFIEC edition, GLBA, NYDFS, PSD2.
- [ ] How ISO 20022 translates into assessable controls.
- [ ] Numeric targets for NFR-3, NFR-4, NFR-5, NFR-8 and section 10 metrics.
- [ ] Order of delivery of frameworks within v1 (internal milestones).
- [ ] Report formats and templates per framework.
- [ ] Pricing/tenant plan limits (if any) affecting quotas.
- [ ] Which cloud providers and SaaS scanners ship first.
