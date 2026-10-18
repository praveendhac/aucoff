# AUCoFF Constitution

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.1.0 |
| Owner | TODO |
| Last updated | TODO |

> Purpose: the non-negotiable principles every other spec, design choice and code change must obey. If a spec conflicts with this file, this file wins.

Related: [spec.md](spec.md) · [design.md](design.md) · [agent.md](agent.md)

## 1. Mission
<!-- One or two sentences: why AUCoFF exists and who it serves. -->
TODO

## 2. Core Principles
<!-- Number each principle (P1, P2...) so specs and tasks can cite them. State it, then why, then how to verify. -->

### P1. Compliance first
- Statement: TODO
- Why: TODO
- Verification: TODO

### P2. Auditability and traceability
<!-- Every agent decision and data change must be reconstructable. -->
- Statement: TODO

### P3. Human in the loop
<!-- Which agent actions always require human approval? -->
- Statement: TODO

### P4. Security and privacy by default
<!-- PII handling, PCI scope, secrets, least privilege, data residency. -->
- Statement: TODO

### P5. Explainability
<!-- Agent outputs must cite sources / control IDs. -->
- Statement: TODO

## 3. Engineering Standards
- Languages and versions: TypeScript (Next.js), Python (FastAPI) - TODO versions
- Code style / linting / formatting: TODO
- Test bar (coverage, required test types): TODO
- Dependency policy (pinning, license, vulnerability scanning): TODO
- Secrets policy: TODO

## 4. Spec-Driven Development Rules
- Specs are the source of truth; code follows specs.
- Changes to behaviour start with a spec change (PR touching `specs/`).
- Every task in [tasks.md](tasks.md) cites the spec section it implements.
- Definition of done: TODO

## 5. AI / Agent Rules
<!-- Model usage, prompt versioning, evaluation gates, data sent to third-party LLMs, hallucination handling. -->
TODO

## 6. Governance
- Who can amend this constitution: TODO
- Amendment process: TODO

## 7. Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | TODO | Initial template |
