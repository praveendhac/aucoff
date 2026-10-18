## What and why
<!-- One or two sentences. Link the task ID (T-nnn) from specs/tasks.md. -->

## Spec references
<!-- Spec sections and rule IDs this change implements (e.g. backend-spec.md section 4a, SEC-1, LIC-3). -->

## Checklist (definition of done, QA-11)
- [ ] Specs updated in this PR if behaviour changed
- [ ] Tests added/updated (tenant isolation, RLS, redaction where relevant)
- [ ] `make check` passes (lint, types, tests, OpenAPI drift, licence scan)
- [ ] New dependencies: licence verified from the official source and recorded in `LICENCES.md` (LIC-1 to LIC-5)
- [ ] No secrets, no real customer data, no copied third-party content (LIC-6)
- [ ] v1 stays local-only: no cloud deployment code (ENV-4)
