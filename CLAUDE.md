# AUCoFF: guidance for AI coding agents

Read `specs/constitution.md` first; it wins over every other document. Specs in `specs/` are the source of truth: change the spec in the same PR as any behaviour change, and cite spec sections and rule IDs (ARC-, DES-, COD-, QA-, SEC-, AI-, DB-, APIR-, LIC-, ENV-) in commits and PRs.

## Hard rules
- **v1 is local-only (ENV-4):** build, run and test on a laptop with kind. Do not add AWS/cloud deployment code, Terraform, or `values-aws.yaml`.
- **AUCoFF's own licence is MIT (LIC-9); keep the root `LICENSE` and the `license` fields in `pyproject.toml` and `package.json` in sync.**
- **Licences (LIC-1 to LIC-8):** permissive only (MIT, Apache-2.0, BSD, ISC, PostgreSQL, MPL-2.0 unmodified, OFL fonts, plus MIT-0, 0BSD, BlueOak-1.0.0, PSF-2.0, CC0-1.0 and CC-BY data with attribution in `NOTICE`, all approved by the owner). Never add AGPL/GPL/LGPL/SSPL/BUSL or unclear-provenance code. Verify a dependency's licence from its official source before adding it and update `LICENCES.md`. If a package has an issue, replace it; do not work around it. Do not copy text, code, images or standards wording from the internet.
- **Base images:** use official minimal images unmodified, pinned by digest, listed in `LICENCES.md` section 5a (LIC-2 exception); never add copyleft software to them.
- **Authentication everywhere (ZT-1 to ZT-9):** no anonymous endpoint of any kind (including health, docs, OpenAPI, metrics); every internal call uses a per-service token; every service uses its own database, broker and object-store credential; probes are `exec`, never HTTP; no auth-bypass flag in any environment.
- **Secrets:** never commit secrets; the global pre-commit hook runs Gitleaks. Synthetic data only.
- **Architecture (ARC-1..11):** frontend talks only to the FastAPI gateway; layers `api -> domain -> db/messaging/llm`; business rules in `domain`; every external dependency behind an interface; every tenant table has `tenant_id` and row-level security.
- **API (APIR-1..6):** every endpoint documented in OpenAPI; `backend/openapi.yaml` must match the generated spec; Spectral must pass.
- **AI (AI-1..16):** agents are advisory, read-only against customer systems; consequential actions need human approval; outputs leaving the tenant are approved and redacted.
- **Honesty:** record versions or licences you could not verify as unverified, and add a task to verify them.

## Workflow
1. Pick a task from `specs/tasks.md` and read its spec sections.
2. Write tests first for tenant isolation, RLS, audit, redaction and anything security relevant.
3. Run `make check` before committing. Small commits with a clear message; end commit messages with the Co-Authored-By trailer when Claude Code authored them.
4. `git pull --rebase origin main` before pushing; do not force-push.

## Useful commands
`make doctor`, `make setup`, `make check`, `make backend-run`, `make openapi`, `make cluster-up`, `make cluster-down`, `make helm-lint`.
