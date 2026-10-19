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
    refs_verified: false          # true only after you checked every reference against the licensed text
    requirements:                 # clause identifiers only, never the clause text; may be empty while draft
      - {framework: soc2-2017, ref: CC6.1}
      - {framework: pci-dss-4.0.1, ref: "8.4.2"}
```

First release covers: `soc2-2017` (Common Criteria / Security), `pci-dss-4.0.1`,
`rbi-dpsc-2026`, `iso27001-2022`. Rules: no copied standards wording, no links in the text
(constitution LIC-6); the catalogue is versioned with `catalogue_version` and reviewed by pull request.

## Current content (catalogue 0.1.0, AI-drafted starter set)

101 controls in 7 domains (identity-access, data-protection, logging-monitoring, infrastructure, secure-development, governance-risk, resilience-response), all `status: draft`, written in our own words by Claude on 2026-10-19 at the owner's request. Severity and check type are judgement calls to review: severity reflects the impact if the control fails; `check_type` says whether a read-only scanner could decide it (`automated`), a person must (`manual`) or both (`hybrid`).

References are **best-known and unverified** (`refs_verified: false`). `rbi-dpsc-2026` references are not filled in at all. The validator refuses to let a control become `approved` unless it has at least one reference and `refs_verified: true`, so nothing can be approved by accident.

To approve a control: check each reference against your licensed copy, fix it, then set `refs_verified: true` and `status: approved`.
