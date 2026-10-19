# Unified control catalogue (owner-authored, v1)

One YAML file per control domain (for example `identity-access.yaml`). Format and checks live in
`backend/app/domain/controls.py`; run `make controls` to validate.

```yaml
catalogue_version: 0.1.0          # same in every file
controls:
  - id: UC-IAM-001                # UC-<DOMAIN 2-6 capitals>-<3 digits>, unique across all files
    title: Short name
    description: One or two sentences in YOUR OWN WORDS (max 600 characters).
    domain: identity-access       # lowercase, hyphens
    severity: high                # critical | high | medium | low
    check_type: hybrid            # automated | manual | hybrid
    status: draft                 # draft | approved (approved = you reviewed it)
    author: Your Name
    requirements:                 # clause identifiers only, never the clause text; may be empty while draft
      - {framework: soc2-2017, ref: CC6.1}                      # verified defaults to false
      - {framework: pci-dss-4.0.1, ref: "8.4.2", verified: true}  # true = checked against the supplied document
```

First release covers: `soc2-2017` (Common Criteria / Security), `pci-dss-4.0.1`,
`rbi-dpsc-2026`, `iso27001-2022`. Rules: no copied standards wording, no links in the text
(constitution LIC-6); the catalogue is versioned with `catalogue_version` and reviewed by pull request.

## Current content (catalogue 0.2.0, AI-drafted, updated 2026-10-20)

158 controls in 8 domains (identity-access, data-protection, logging-monitoring, infrastructure, secure-development, governance-risk, resilience-response, payment-security), all `status: draft`, written in our own words by Claude at the owner's request. Severity and check type are judgement calls to review.

References are checked per requirement (`verified: true`) against the documents the owner placed in `reference/` (local only, never committed):
- ISO/IEC 27001:2022: every Annex A reference was confirmed to exist in the supplied standard and matched by title.
- PCI DSS v4.0.1: references were confirmed to exist in the supplied document and matched by requirement title. Two doubtful ones were removed (12.3.1 is targeted risk analysis; 3.5.1 is specific to stored card numbers).
- RBI: the supplied documents are the Master Directions on Cyber Resilience and Digital Payment Security Controls for non-bank PSOs (RBI/DPSS/2024-25/123, 30 July 2024; framework id `rbi-pso-md-2024`, references are paragraph numbers such as `15(e)`) and the DRAFT Framework on Alternative Authentication Mechanisms (`rbi-afa-draft`, references such as `3(a)`). They are NOT the commercial-bank directions the spec names as `rbi-dpsc-2026`; no controls reference that id yet.
- SOC 2 (`soc2-2017`): no document was supplied, so every SOC 2 reference is unverified.

The validator refuses to let a control become `approved` unless it has at least one reference and all of them are `verified: true`. "Verified" here means an AI matched the clause against the supplied text; approval is still your decision.
