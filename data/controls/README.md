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
    requirements:                 # clause identifiers only, never the clause text
      - {framework: soc2-2017, ref: CC6.1}
      - {framework: pci-dss-4.0.1, ref: "8.4.2"}
```

First release covers: `soc2-2017` (Common Criteria / Security), `pci-dss-4.0.1`,
`rbi-dpsc-2026`, `iso27001-2022`. Rules: no copied standards wording, no links in the text
(constitution LIC-6); the catalogue is versioned with `catalogue_version` and reviewed by pull request.
