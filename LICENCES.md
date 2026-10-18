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
| PSF-2.0 | Python `typing_extensions` (required by pydantic/FastAPI) | Explicit per-package exception in `backend/scripts/check_licences.py`. Removing it is not realistic. Recommend approving. |
| MIT-0 | npm `@csstools/*` (Tailwind/PostCSS chain) | MIT without the attribution clause; recommend approving. |
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
| Prowler | Apache-2.0 | Candidate (cloud scanning) - confirm from LICENSE on adoption |
| Trivy, Checkov, kube-bench | Apache-2.0 | Candidates - confirm from LICENSE on adoption |
| kubescape | Not found in search | **Unverified** - do not adopt until confirmed |
| SeaweedFS | Apache-2.0 | Candidate replacement for MinIO (S3-compatible) - confirm and test |
| Perses | Apache-2.0 | Candidate dashboard tool replacing Grafana |
| VictoriaLogs | Apache-2.0 (single-node and cluster) | Candidate log store replacing Loki |
| Jaeger | Not found in search | **Unverified** - candidate for traces; confirm |
| Prometheus | Not checked | **Unverified** - confirm before adopting |
| RabbitMQ | Server MPL-2.0 (client libraries Apache-2.0/MPL-2.0 dual) | Allowed (MPL-2.0 unmodified) - confirm on adoption |
| Keycloak | Not found in search | **Unverified** - confirm before adopting |
| PostgreSQL, pgvector, CloudNativePG | PostgreSQL licence (PostgreSQL); pgvector uses the PostgreSQL licence; CloudNativePG Apache-2.0 - **not confirmed in this pass** | **Unverified** - confirm on adoption |

## 5. Direct dependencies in use

| Package | Ecosystem | Version | Licence | Status | Source |
|---------|-----------|---------|---------|--------|--------|
| fastapi | Python | 0.146.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| pydantic-settings | Python | 2.16.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
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
| react | npm | 19.3.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| react-dom | npm | 19.3.0 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| tailwindcss | npm | 4.3.3 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |
| typescript | npm | 5.9.3 | Apache-2.0 | Allowed | Read from installed package metadata, 2026-10-19 |
| vitest | npm | 5.0.5 | MIT | Allowed | Read from installed package metadata, 2026-10-19 |

Transitive dependencies (about 30 Python and 550 npm packages) are covered by the automated scans; see section 2 for licences outside the allow-list. Full listings: `cd backend && uv run pip-licenses` and `cd frontend && npx license-checker-rseidelsohn --summary`.

## 6. Fonts, icons, images and content

| Item | Licence | Status |
|------|---------|--------|
| Geist / Geist Mono (via `next/font/google`) | SIL OFL 1.1 | Allowed (OFL fonts); build downloads the font from Google Fonts - move to self-hosted files if the build must work offline |
| Next.js/Vercel template logos and sample content | - | Removed from the scaffold (provenance, LIC-6) |
| `favicon.ico` from create-next-app | Template asset | **To replace** with an original icon (T-009) |

## 7. Attribution (NOTICE)

To be generated from the scans before any distribution (LIC-7). Data licences with attribution requirements (CC-BY) must be listed here.
