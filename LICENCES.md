# Licence and provenance register

Maintained under constitution rules LIC-1 to LIC-8 (see [`specs/constitution.md`](specs/constitution.md)) and task T-009. Every direct dependency, tool, image, font, icon and dataset is recorded here with its licence and the source of that information. Anything with a licence or provenance issue is **not used**; an alternative is chosen and the decision is recorded here.

Last updated: 2026-10-19. Status: **T-009 in progress** (first pass; not complete).

## 1. How information in this register was obtained

- **Installed package metadata** (`pip-licenses`, `license-checker-rseidelsohn`): the licence declared by the exact installed version. CI re-checks this on every change (`make licences`).
- **Web search results of 2026-10-19:** used for tools not yet installed. These are secondary sources and are marked *unconfirmed* until the third-party project's own LICENSE file is read when the tool is adopted. Nothing here was read from a lawyer or from the projects' LICENSE files unless stated.

## 2. Policy decisions that need the owner

The constitution's allow-list (LIC-1) is: MIT, Apache-2.0, BSD-2/3-Clause, ISC, PostgreSQL, MPL-2.0 (unmodified), OFL fonts. The dependency scan found these permissive-style licences that are **not on the list yet**. CI currently passes them with a notice. Please decide for each: add to the allow-list, or require replacement.

| Licence | Where it appears | Notes |
|---------|------------------|-------|
| PSF-2.0 | Python `typing_extensions` (required by pydantic/FastAPI) and `greenlet` (MIT AND PSF-2.0, required by SQLAlchemy asyncio) | Explicit per-package exception in `backend/scripts/check_licences.py`. Removing it is not realistic. Recommend approving. |
| MIT-0 | npm `@csstools/*` (Tailwind/PostCSS chain); Python `cffi` (required by `cryptography`, hence by PyJWT) | MIT without the attribution clause; explicit per-package exception for `cffi` in `backend/scripts/check_licences.py`; recommend approving. |
| BlueOak-1.0.0 | npm `glob`, `minimatch`, `tar`, `lru-cache`, others (11 packages) | Permissive, OSI-approved; recommend approving. |
| 0BSD | npm `tslib` | Public-domain-equivalent; recommend approving. |
| CC0-1.0 | npm `language-subtag-registry`, `mdn-data`, `spdx-license-ids` | Public-domain dedication (data); recommend approving. |
| CC-BY-4.0 / CC-BY-3.0 | npm `caniuse-lite` (data), `spdx-exceptions` | Data licences requiring attribution; attribution must be carried in NOTICE (LIC-7). |
| Python-2.0 | npm `argparse` | PSF-style, permissive; recommend approving. |

**Project licence (decided 2026-10-19):** AUCoFF itself is licensed under the **MIT License** (see [`LICENSE`](LICENSE)), relicensed by the copyright holder from the GNU AGPL v3. The rules above govern what AUCoFF may depend on; MIT governs what others may do with AUCoFF.

## 3. Issue found and fixed during scaffolding

| Item | Problem | Action |
|------|---------|--------|
| `sharp` (optional dependency of Next.js, for image optimisation) | Its prebuilt `libvips` binaries are LGPL-3.0-or-later (disallowed by LIC-2) | Replaced with an in-repo stub via `overrides` in `frontend/package.json` (`frontend/stubs/sharp`) and set `images.unoptimized: true`. The licence scan confirms no LGPL package remains. |

## 4. Tools named in the specs (first-pass verification)

| Tool | Finding (web search 2026-10-19) | Decision |
|------|-------------------------------|----------|
| MinIO | GNU AGPL v3; community repository archived 25 April 2026, source-only, no binaries | **Not approved** |
| Grafana, Loki, Tempo | Relicensed from Apache-2.0 to AGPLv3 (April 2021) | **Not approved** |
| Steampipe | AGPL-3.0 | **Not approved** |
| ScoutSuite | GPL-2.0 (NCC Group) | **Not approved** |
| Semgrep / Opengrep engines | LGPL-2.1 | **Not approved** (LIC-2 denies LGPL) |
| Semgrep rules | Semgrep Rules License (restricts competing/commercial use) | **Not approved** |
| Redis (current) | Tri-licensed RSALv2 / SSPLv1 / AGPLv3 | **Not approved**; Valkey (BSD-3-Clause per search) is the candidate if a cache is ever needed. v1 avoids a cache by keeping the session in an encrypted cookie. |
| Trivy v0.76.0 (image scanning and SBOM) | Apache-2.0 (read from the aquasecurity/trivy LICENSE, 2026-10-19); run from a digest-pinned container | Allowed; in use (`make scan`). Its vulnerability data is downloaded at scan time; no data is copied into the repository |
| Prowler | Apache-2.0 | Candidate (cloud scanning) - confirm from LICENSE on adoption |
| Trivy, Checkov, kube-bench | Apache-2.0 | Candidates - confirm from LICENSE on adoption |
| kubescape | Not found in search | **Unverified** - do not adopt until confirmed |
| ingress-nginx | Retired by Kubernetes SIG Network: no releases, bug fixes or security updates after March 2026 | **Not approved** (unmaintained, security risk); replaced by Traefik (MIT per web search) |
| SeaweedFS | Apache-2.0 | Candidate replacement for MinIO (S3-compatible) - confirm and test |
| Perses | Apache-2.0 | Candidate dashboard tool replacing Grafana |
| VictoriaLogs | Apache-2.0 (single-node and cluster) | Candidate log store replacing Loki |
| Jaeger | Not found in search | **Unverified** - candidate for traces; confirm |
| Prometheus | Not checked | **Unverified** - confirm before adopting |
| RabbitMQ 4.3.6 | Server MPL-2.0 with some Apache-2.0 files (read from the rabbitmq-server LICENSE and the image's /opt/rabbitmq/LICENSE, 2026-10-19) | Allowed (MPL-2.0, unmodified official image); in use |
| Keycloak 26.8.1 | Apache-2.0 (read from `LICENSE.txt` in the keycloak/keycloak repository, 2026-10-19) | Allowed; in use (identity provider) |
| cert-manager v1.21.2 | Apache-2.0 (read from `LICENSE` in the cert-manager/cert-manager repository, 2026-10-19) | Allowed; in use (local CA, in-cluster TLS) |
| PostgreSQL, pgvector, CloudNativePG | PostgreSQL licence (PostgreSQL); pgvector uses the PostgreSQL licence; CloudNativePG Apache-2.0 - **not confirmed in this pass** | **Unverified** - confirm on adoption |

## 5. Direct dependencies in use

| Package | Ecosystem | Version | Licence | Status | Source |
|---------|-----------|---------|---------|--------|--------|
| fastapi | Python | 0.146.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| pydantic-settings | Python | 2.16.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| pyjwt | Python | 2.15.1 | MIT | Allowed | Installed package metadata, 2026-10-19 (JWT validation, ZT-3) |
| cryptography | Python | 50.0.2 | Apache-2.0 OR BSD-3-Clause | Allowed | Installed package metadata, 2026-10-19 (via pyjwt[crypto]) |
| sqlalchemy | Python | 2.1.5 | MIT | Allowed | Installed package metadata, 2026-10-19 |
| asyncpg | Python | 0.32.0 | Apache-2.0 | Allowed | Installed package metadata, 2026-10-19 (chosen over psycopg, which is LGPL) |
| alembic | Python | 1.20.0 | MIT | Allowed | Installed package metadata, 2026-10-19 |
| greenlet | Python | 3.5.6 | MIT AND PSF-2.0 | Allowed with per-package exception (PSF-2.0 pending owner approval) | Installed package metadata, 2026-10-19 (via sqlalchemy[asyncio]) |
| aio-pika | Python | 10.1.1 | Apache-2.0 | Allowed | Passed the Python licence gate, 2026-10-19 (AMQP client; with aiormq 7.2.2, pamqp 4.0.1, yarl, multidict, propcache, idna) |
| pytest-asyncio | Python | 1.4.0 | Apache-2.0 | Allowed (dev) | Installed package metadata, 2026-10-19 |
| uvicorn | Python | 0.54.0 | BSD-3-Clause | Allowed | Read from installed package metadata, 2026-10-19 |
| httpx | Python | 0.28.1 | BSD License | Allowed | Read from installed package metadata, 2026-10-19 |
| mypy | Python | 2.4.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| pip-licenses | Python | 5.5.5 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| pytest | Python | 9.1.1 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| pyyaml | Python | 6.0.3 | MIT License | Allowed | Read from installed package metadata, 2026-10-19 |
| ruff | Python | 0.17.1 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| types-pyyaml | Python | 6.0.12.20260906 | Apache-2.0 | Allowed | Read from installed package metadata, 2026-10-19 |
| @tailwindcss/turbopack | npm | 4.3.3 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| @testing-library/jest-dom | npm | 7.0.1 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| @testing-library/react | npm | 16.3.3 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| @types/node | npm | 24.19.2 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| @types/react | npm | 19.3.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| @types/react-dom | npm | 19.3.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| @vitejs/plugin-react | npm | 6.1.2 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| eslint | npm | 9.39.5 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| eslint-config-next | npm | 16.4.2 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| jsdom | npm | 29.1.1 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| license-checker-rseidelsohn | npm | 5.0.1 | BSD-3-Clause | Allowed | Read from installed package metadata, 2026-10-19 |
| next | npm | 16.4.2 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| prettier | npm | 3.9.10 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| next-auth (Auth.js v4) | npm | 4.24.15 | ISC | Allowed | Registry metadata and installed package, 2026-10-19 (BFF login). v5 is still a beta release, so the stable v4 line is used. Its dependencies jose, openid-client, oauth, cookie, @panva/hkdf, uuid, preact and preact-render-to-string are all MIT (read from installed metadata). |
| react | npm | 19.3.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| react-dom | npm | 19.3.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| tailwindcss | npm | 4.3.3 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| typescript | npm | 5.9.3 | Apache-2.0 | Allowed | Read from installed package metadata, 2026-10-19 |
| vitest | npm | 5.0.5 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |

Transitive dependencies (about 30 Python and 550 npm packages) are covered by the automated scans; see section 2 for licences outside the allow-list. Full listings: `cd backend && uv run pip-licenses` and `cd frontend && npx license-checker-rseidelsohn --summary`.

## 5a. Container base images (policy decision 2026-10-19)

Every common base image (Debian, Ubuntu, Alpine, distroless) contains GPL or LGPL system components such as glibc or BusyBox, so the rule cannot be applied literally to OS layers. **Owner decision:** unmodified OS packages inside official minimal base images are treated as mere aggregation (constitution LIC-2 exception). The strict permissive-only rule still applies to AUCoFF's code and all language-level dependencies. Base images must stay unmodified, be pinned by digest, be vulnerability-scanned, and be listed here.

| Image | Used for | Pinned digest | Status |
|-------|----------|---------------|--------|
| `python:3.13-slim` | backend | `sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f` (pulled 2026-10-19) | In use; pip and setuptools are uninstalled from the final image (their vendored libraries had 4 HIGH findings); scanned clean (T-010) |
| `node:24-trixie-slim` (Node 24.22, Debian 13.7) | frontend | `sha256:7f486cabe892bff8fef04c0f7da8dba84a560be3e4e2740b7a86afc57ebec315` (pulled 2026-10-19) | In use; replaced `node:22-slim`, whose Debian 12 layer had 7 fixable HIGH/CRITICAL perl findings with no fixed image available. npm/npx/corepack are deleted from the final image. Scanned clean (T-010) |
| `kindest/node:v1.37.0` | kind cluster nodes | `sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5` (from the kind v0.33.0 release notes; pulled by digest successfully) | In use (local dev only) |
| `postgres:18` | database tests only (throwaway container) | tag only (test use) | In use in tests; PostgreSQL licence per upstream, confirm (T-009) |
| `ghcr.io/cloudnative-pg/postgresql:18.6-minimal-trixie` | PostgreSQL 18.6 operand image | `sha256:c9be7f221a05b18fe65259d9136affbabe3b39ad91c3b68f8f2f990a45f35f38` | In use; PostgreSQL licence expected, confirm (T-009) |
| `ghcr.io/cloudnative-pg/pgvector:0.8.6-18-trixie` | pgvector 0.8.6 extension image volume | `sha256:2da4ddaf07cec8edf9ea265968c5368a5df4568737964d2a268d9843589e3e42` | In use; image label says licence "PostgreSQL" (read from the image on 2026-10-19) |
| CloudNativePG operator (chart `cnpg/cloudnative-pg` 0.29.1, app 1.30.1) | PostgreSQL operator | pulled by the chart | In use; Apache-2.0 expected (extensions repo is Apache-2.0 per web fetch); confirm (T-009) |
| `quay.io/keycloak/keycloak:26.8.1` | identity provider | `sha256:79c623a22abacf3fe6c00a5fb30f5b7843d717b234033b80995891c06116d244` (pulled 2026-10-19) | In use; Apache-2.0 for Keycloak itself; scanned clean 2026-10-19 (T-010) |
| cert-manager images (chart `jetstack/cert-manager` v1.21.2) | local CA / certificates | pulled by the chart | In use; Apache-2.0; digest pinning to add with T-010 |
| `docker.io/library/rabbitmq:4.3.6-alpine` | message broker | `sha256:6931816af1a943f471c038b278835d36692d55dec769232739296bb91b7de0f5` (pulled 2026-10-19) | In use; MPL-2.0 for RabbitMQ itself; scanned clean 2026-10-19 (T-010) |
| `docker.io/traefik:v3.7.14` (Helm chart `traefik/traefik` 42.0.0) | ingress controller | pulled by the chart | In use; licence MIT per web search 2026-10-19, confirm from LICENSE (T-009) |

## 6. Fonts, icons, images and content

| Item | Licence | Status |
|------|---------|--------|
| Geist / Geist Mono (via `next/font/google`) | SIL OFL 1.1 | Allowed (OFL fonts); build downloads the font from Google Fonts - move to self-hosted files if the build must work offline |
| Next.js/Vercel template logos and sample content | - | Removed from the scaffold (provenance, LIC-6) |
| `favicon.ico` from create-next-app | Template asset | **To replace** with an original icon (T-009) |

## 7. Attribution (NOTICE)

To be generated from the scans before any distribution (LIC-7). Data licences with attribution requirements (CC-BY) must be listed here.
