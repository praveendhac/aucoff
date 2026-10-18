# AUCoFF Frontend Spec (Next.js)

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.2.0 |
| Owner | Praveen Darshanam |
| Last updated | 2026-10-18 |

> Purpose: UI behaviour and structure for the Next.js (React, TypeScript) app. Entity IDs are UUID strings and the tenant comes from the session, never the URL or client input (see [database-spec.md](database-spec.md), [api-contract.md](api-contract.md)).

Related: [spec.md](spec.md) · [api-contract.md](api-contract.md) · [design.md](design.md) · [constitution.md](constitution.md) · [backend-spec.md](backend-spec.md)

## 1. Tech Choices
| Area | Choice | Notes |
|------|--------|-------|
| Framework | Next.js (App Router), React, TypeScript `strict` | Version pinned in `package.json` (TODO); COD-2 |
| UI | shadcn/ui (Radix primitives) + Tailwind CSS | Components copied into repo under `components/ui` |
| Server state | TanStack Query | Caching, retries, invalidation |
| API client | TypeScript client generated from the backend OpenAPI spec (e.g. `openapi-typescript` + `openapi-fetch`; tool TODO) | Generated on CI; never hand-edit; keeps contract in sync (DES-7) |
| Forms / validation | React Hook Form + Zod | Zod schemas mirror API schemas |
| Charts | TODO (e.g. Recharts) | Dashboards (US-8) |
| Auth | Server-side session via BFF pattern (Auth.js or equivalent - TODO) | See section 5 |
| Unit/component tests | Vitest + Testing Library | |
| E2E / a11y tests | Playwright + axe-core | |
| Lint/format | ESLint + Prettier | COD-2 |

## 2. Information Architecture
| Route | Page | Persona | Roles | Spec refs |
|-------|------|---------|-------|-----------|
| `/` | Posture dashboard (per framework / jurisdiction, trends) | PER-4, PER-5 | executive, ciso, compliance_officer | US-8, US-13, FR-11 |
| `/frameworks` | Framework and requirement catalogue | PER-1 | all (read) | US-1, FR-1 |
| `/controls` | Unified controls and mappings (review/approve) | PER-1 | compliance_officer | US-1, FR-2 |
| `/scopes` | Assessment scopes and schedules | PER-1 | compliance_officer | US-2, FR-3 |
| `/connectors` | Source connectors (cloud, k8s, repos, SaaS) | PER-3, PER-6 | engineer, admin | US-3, FR-4 |
| `/evidence` | Evidence list, document upload, evidence viewer | PER-1, PER-2 | compliance_officer, engineer, auditor | US-4, FR-5, FR-6 |
| `/assessments` | Assessment runs and live progress | PER-1 | compliance_officer | US-5, FR-3, FR-15 |
| `/assessments/[id]` | Control results with citations; review/approve | PER-1, PER-2 | compliance_officer, auditor (read) | US-5, FR-7 |
| `/findings` | Findings list and detail, ticket links | PER-3, PER-5 | engineer, compliance_officer, ciso | US-6, FR-8, FR-9 |
| `/approvals` | Pending agent-action approvals | PER-1, PER-5 | compliance_officer, ciso | US-5, FR-7 |
| `/reports` | Generate, list, download reports | PER-1, PER-2 | compliance_officer, auditor, ciso | US-9, FR-12 |
| `/audit-log` | Audit trail and integrity check | PER-2 | auditor, ciso | US-7, FR-10 |
| `/settings/users` | Users and roles | PER-6 | admin | US-10, FR-13 |
| `/settings/sso` | OIDC/SAML configuration | PER-6 | admin | US-10 |
| `/settings/integrations` | Jira, ServiceNow, Slack, Teams, email | PER-6 | admin | US-11, FR-9, FR-14 |
| `/login`, `/logout` | Auth entry points | all | - | US-10 |

## 3. Key Screens
### 3.1 Control result review (`/assessments/[id]`)
- Table of unified controls with status, confidence, framework badges, last reviewed.
- Detail panel: agent summary (AI-labelled), cited evidence passages with deep links to the evidence viewer, mapped framework requirements, run metadata (model, prompt version).
- Actions: approve, reject with comment, edit status (reason required). Each action calls the approvals API and shows the recorded approver and time.
### 3.2 Agent run timeline
- Live steps from the SSE stream (see [api-contract.md](api-contract.md)): started, tool call, evidence collected, result produced, awaiting approval, failed.
- Shows token/cost progress against budget (NFR-8).
### 3.3 Posture dashboard
- Coverage % by framework and jurisdiction, open findings by severity, trend, readiness score (definitions from [spec.md](spec.md) section 10).
### 3.4 Findings
- Filter by severity, framework, jurisdiction, status; remediation steps; "Create ticket" with Jira/ServiceNow link and status sync.
### 3.5 Reports
- Pick assessment and framework, generate, show status, download; shows included approvals.

## 4. Components
| Component | Purpose | Notes |
|-----------|---------|-------|
| `AppShell` | Navigation, tenant/user menu, role-aware items | Hides items the role cannot use (server still enforces, SEC-1) |
| `DataTable` | Sorting, cursor pagination, filters | Server-driven; keyboard accessible |
| `AiBadge` | Marks AI-generated content | AI-13 |
| `CitationList` | Source citations with links | AI-3 |
| `ConfidenceIndicator` | Shows confidence/uncertainty | AI-9; never colour-only |
| `ApprovalDialog` | Approve/reject with comment | Confirms consequences |
| `RunTimeline` | SSE-driven run progress | Reconnects with `Last-Event-ID` |
| `EvidenceViewer` | Preview documents/config snippets | Sanitised rendering only |
| `FrameworkBadge`, `SeverityBadge`, `StatusBadge` | Consistent visuals | |
| `EmptyState`, `ErrorState`, `Skeleton` | Standard states | |

## 5. Auth and Session
- Login via the external OIDC identity provider (Keycloak locally; Entra ID/Cognito later). SAML handled by the IdP.
- Next.js server (BFF) performs the code flow with PKCE, holds tokens server-side, and issues an `httpOnly`, `Secure`, `SameSite=Lax` session cookie. Tokens MUST NOT be stored in `localStorage`/`sessionStorage`.
- API calls from the browser go to Next.js route handlers or a same-site proxy that attach the access token; CSRF protection on state-changing requests.
- Role and tenant come from token claims; UI gating is cosmetic only.
- Session expiry and silent refresh handled server-side; idle timeout TODO.

## 6. Agent Interaction UX (AI-13, AI-9)
- AI-generated text carries an `AiBadge`, sources, confidence and approval status.
- Low-confidence or unverified claims are visually distinct and routed to the approvals queue.
- Agent output rendered as plain text/sanitised Markdown only; no raw HTML (XSS).
- Users can see which model/prompt version produced a result.

## 7. State and Data Fetching
- All server data via TanStack Query with the generated client; query keys include resource and filters (tenant is implicit in session).
- Optimistic updates only for safe, reversible UI actions (never approvals).
- SSE handled by a dedicated hook that updates the query cache.
- Uploads use presigned URLs from the API and show progress; client checks size/type but server is authoritative.

## 8. States and Errors
Loading (skeletons), empty (guidance + primary action), error (problem+json message and request ID), permission denied (403 page), offline/reconnecting banner, partial agent failure shown inline. Forms show field-level errors mapped from API validation errors.

## 9. Accessibility and i18n
- WCAG 2.2 AA (NFR-10, QA-10): keyboard navigation, focus management in dialogs, ARIA labels, contrast, no colour-only status, reduced-motion support; axe checks in CI.
- English first; strings externalised for later localisation (TODO library); dates/numbers formatted via `Intl`.

## 10. Security (NFR-1)
- Strict Content-Security-Policy, `X-Content-Type-Options`, frame protections, `Referrer-Policy`, HSTS (via ingress).
- No `dangerouslySetInnerHTML` with untrusted content; sanitise Markdown; validate and encode all URL params.
- Dependency audit and lockfile checks in CI (COD-7).
- No secrets in client bundles; only `NEXT_PUBLIC_*` public config.

## 11. Performance Budgets (proposal)
- LCP < 2.5 s and INP < 200 ms on dashboard on a mid-range laptop; JS budget per route TODO; tables virtualised above 200 rows.

## 12. Project Layout
```
frontend/
  app/                # routes (App Router)
  components/ui/      # shadcn/ui
  components/         # app components
  lib/api/            # generated client + wrappers
  lib/auth/
  hooks/
  tests/              # unit, e2e
```

## 13. Testing Plan
- Unit/component: Vitest + Testing Library for components and hooks.
- E2E: Playwright against the kind deployment for critical flows (login, run assessment, review and approve, create ticket, generate report).
- Accessibility: axe-core in component and E2E tests.
- Contract: generated client compiled against committed OpenAPI; build fails on drift.
- Visual regression: TODO.

## 14. Open Questions
- [ ] BFF auth library choice and session store.
- [ ] Charting library.
- [ ] i18n requirements and target locales (India/EU).
- [ ] Dark mode and branding.
