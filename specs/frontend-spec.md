# AUCoFF Frontend Spec (Next.js)

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.1.0 |
| Owner | TODO |
| Last updated | TODO |

> Purpose: UI behaviour and structure for the Next.js (React, TypeScript) app. Entity IDs are UUID strings and the tenant comes from the session, never the URL or client input (see [database-spec.md](database-spec.md), [api-contract.md](api-contract.md)).

Related: [spec.md](spec.md) · [api-contract.md](api-contract.md) · [design.md](design.md)

## 1. Tech Choices
- Next.js version / router (App Router?): TODO
- UI library / design system: TODO
- State and data fetching: TODO
- Forms and validation: TODO
- Testing (unit, component, e2e): TODO

## 2. Information Architecture
| Route | Page | Persona | Auth / role | Spec ref |
|-------|------|---------|-------------|----------|
| `/` | TODO | TODO | TODO | US-? |
| `/frameworks` | TODO | TODO | TODO | US-? |
| `/assessments` | TODO | TODO | TODO | US-? |
| `/approvals` | Agent action approvals | PER-1 | TODO | US-? |
| `/audit-log` | TODO | PER-2 | TODO | US-? |

## 3. Key Screens
<!-- For each: purpose, layout sketch/link, data shown, actions, states. -->
### 3.1 TODO
TODO

## 4. Components
| Component | Props | Used in | Notes |
|-----------|-------|---------|-------|
| TODO | TODO | TODO | TODO |

## 5. Auth and Session
<!-- Login flow, token storage, role-based UI gating. -->
TODO

## 6. Agent Interaction UX
<!-- Streaming responses, progress, citations, approve/reject flows, confidence display. -->
TODO

## 7. States and Errors
Loading, empty, error, offline, permission-denied: TODO

## 8. Accessibility and i18n
Target (e.g. WCAG 2.2 AA), keyboard support, locales: TODO

## 9. Performance Budgets
TODO

## 10. Testing Plan
TODO
