# AUCoFF Infrastructure Spec

| Field | Value |
|-------|-------|
| Status | Approved (v1 baseline, owner sign-off 2026-10-19) |
| Version | 0.9.0 |
| Owner | Praveen Darshanam |
| Last updated | 2026-10-19 |

> Purpose: how AUCoFF is packaged, deployed and operated. **v1 (MVP) is local-only:** everything is built, deployed and tested on a developer laptop on a kind cluster with one umbrella Helm chart. kind was chosen over minikube (Docker-based, lighter, faster multi-node, same tool in CI). AWS (EKS) with Terraform is post-v1 and informational only.

Related: [design.md](design.md) · [backend-spec.md](backend-spec.md) · [frontend-spec.md](frontend-spec.md) · [database-spec.md](database-spec.md) · [constitution.md](constitution.md)

## 1. Environments
| Env | Platform | Purpose | Status |
|-----|----------|---------|--------|
| local | kind cluster on laptop | Development, integration and E2E testing; synthetic data only (ENV-2) | **v1 (only target)** |
| ci | GitHub Actions runners + ephemeral kind (or run the same make targets locally) | Build, test, scan, E2E - no deployment to any hosted environment | v1 |
| aws | EKS + managed services (section 10) | Staging / production | **Post-v1, out of scope** |
Same images and chart in all environments, differing only by values (ENV-1).

## 2. Container Inventory
| Component | Image / source | Notes |
|-----------|----------------|-------|
| frontend | `frontend/` (Next.js standalone) | Port 3000 (TODO) |
| backend gateway | `backend/app` (FastAPI) | Port 8000 (TODO) |
| agent services (9) | `backend/services/*` | assessment-orchestrator, mapping-agent, cloud-scanner, k8s-scanner, repo-scanner, saas-scanner, document-analyzer, remediation-advisor, report-generator |
| PostgreSQL 18.6 + pgvector 0.8.6 | CloudNativePG operator + pgvector-enabled PostgreSQL 18.6 image (image source to verify, T-004) | [database-spec.md](database-spec.md) |
| RabbitMQ | Official chart/image | Queues per [backend-spec.md](backend-spec.md) section 5 |
| Object store | S3-compatible; **MinIO is AGPL-3.0 (community repo archived April 2026) and is NOT approved**; candidate SeaweedFS (Apache-2.0 per web search 2026-10-19) to be confirmed and tested under T-009 | Evidence/report store |
| Keycloak | Official chart/image | Local OIDC/SAML IdP |
| Observability | OpenTelemetry Collector, Prometheus; dashboards/logs/traces on permissively licensed tools (Grafana, Loki and Tempo have been AGPLv3 since 2021 and are NOT approved; candidates Perses and VictoriaLogs are Apache-2.0 per web search, Jaeger and Prometheus still unverified - confirm under T-009) | Section 8 |
| Ingress + cert-manager | Traefik ingress controller (ingress-nginx was retired after March 2026) + cert-manager | Local CA for TLS |

### Image standards
- Multi-stage builds, minimal base (distroless or slim), non-root user, read-only root filesystem where possible (SEC-8).
- Pinned base image digests; lockfile-based installs; SBOM generated; vulnerability scan (Trivy) blocks on critical/high.
- Each image ships an in-container health-check command used by `exec` liveness/readiness probes (no anonymous HTTP health endpoint, ZT-7); graceful shutdown.
- Scanner service images bundle or call the pinned open-source tools (Prowler, kubescape, Trivy, Checkov, etc.) by digest; each tool's licence is reviewed (SEC-17) and tool images are scanned and SBOM'd like our own. Scanners run with minimal egress and no cluster-admin rights.
- Images tagged with git SHA; semantic versions for releases.

## 3. Helm Chart (umbrella)
```
deploy/helm/aucoff/
  Chart.yaml
  values.yaml            # defaults
  values-local.yaml      # kind overrides
  # values-aws.yaml is post-v1 and is not created in v1
  charts/                # subcharts / vendored dependencies
  templates/
    frontend/ backend/ services/ migration-job/ networkpolicies/ ingress/ rbac/
```
- Dependencies (subcharts): PostgreSQL (or operator), RabbitMQ, object store, Keycloak, observability stack; each toggled by `<name>.enabled` so AWS can disable in-cluster versions (RDS, Amazon MQ, S3, Cognito/Entra).
- Key values: image tags/digests, replicas, resources, ingress host, feature flags, queue names, LLM provider/model, budget limits, OIDC issuer/audience, object-store endpoint.
- Migration: Helm pre-upgrade hook Job runs Alembic as `aucoff_migrator` (database-spec section 7).
- `helm lint`, `helm template | kubeconform` and policy checks run in CI.

## 4. Kubernetes Baseline
- Namespaces: `aucoff` (app), `aucoff-data` (database, broker, object store), `aucoff-observability`, `aucoff-system` (ingress, cert-manager).
- **Pod Security**: `restricted` profile; `runAsNonRoot`, drop all capabilities, `seccompProfile: RuntimeDefault`, no privileged/hostPath.
- **NetworkPolicies**: default deny ingress and egress per namespace; explicit allows:
  - ingress controller -> frontend, backend
  - frontend -> backend
  - backend and agent services -> PostgreSQL, RabbitMQ, object store, Keycloak (JWKS)
  - only agent services -> external internet (cloud/SaaS APIs, LLM provider) via egress rules/proxy
  - everything -> OpenTelemetry Collector
  - PostgreSQL reachable only from backend, agent services and the migration Job (DB-5, SEC-2)
- **RBAC**: dedicated ServiceAccounts per workload, least privilege, no cluster-admin; `automountServiceAccountToken: false` unless required.
- Resource requests/limits on every container; PodDisruptionBudgets for stateless services; HPA for scanners based on queue depth (KEDA - TODO) or CPU.
- Anti-affinity/topology spread for multi-replica services (applies to a hosted environment, post-v1).

## 5. Configuration and Secrets
- ConfigMaps for non-secret config; Kubernetes Secrets for credentials (DB, RabbitMQ, object store, OIDC client secret, LLM API key, encryption keys). Secrets never committed; local secrets generated by a bootstrap script into the cluster (SEC-3).
- Per-tenant connector credentials are NOT stored in Helm secrets; they are referenced via `config_ref` and kept in a dedicated secret store: Kubernetes Secrets under a dedicated namespace/prefix are acceptable for local development only (they do not scale to many tenants); AWS Secrets Manager (or Vault) for staging/production with per-tenant keys where supported.
- cert-manager issues TLS certificates (local CA now, ACM/Let's Encrypt later); in-cluster traffic TLS for DB and broker. Service identity is by token (OAuth2 client credentials from Keycloak, ZT-4) over TLS; mTLS between services is not required in v1 and is deferred. NetworkPolicies are defence in depth only and never replace authentication.
- **Per-service credentials (ZT-4, ZT-5, ZT-6):** `make secrets` generates a unique credential set per service: Keycloak client secret, PostgreSQL login role password, RabbitMQ user password and object-store access key. No two services share a secret. Keycloak holds a separate service realm/clients (`aucoff-<service>`) with only the scopes each service needs.
- **Probes (ZT-7):** liveness/readiness use `exec` probes running the container's health-check command; the Helm chart MUST NOT use `httpGet` probes or expose any path without authentication. Ingress routes only to services whose every endpoint is authenticated (the login flow and static shell of the frontend are the carve-outs in ZT-2).
- **Telemetry:** services push to the OpenTelemetry Collector with an authenticated identity; Prometheus scrapes only over an authenticated channel; dashboards are behind SSO.
- Secret rotation procedure TODO; Gitleaks pre-commit stays enabled.

## 5a. Laptop Profile (v1)
- **Cluster:** kind (single control-plane + 1-2 workers) created from a config in `deploy/kind/`; ingress ports mapped to the host; minikube is not supported in v1.
- **Prerequisites:** Docker (or a compatible runtime), kind, kubectl, helm, make; internet access only for pulling images and the LLM API.
- **Resources (proposal, to be measured in T-410):** about 8 CPUs and 16 GB RAM for the full stack; a minimal profile (`values-local-min.yaml`) disables observability and optional scanners for 8 GB machines.
- **Offline mode:** the LLM provider can run in recorded/mock mode so tests and demos work without network access; cloud scanners use recorded fixtures unless a read-only test account is configured.
- **Node image requirement (verified 2026-10-19 by web search):** CloudNativePG loads `pgvector` as an image-volume extension, which needs PostgreSQL 18, Kubernetes 1.35 or later and containerd 2.1 or later. The kind node image must satisfy this; pin `kindest/node` by tag and digest in `deploy/kind/kind-config.yaml` once checked with `kind` installed (T-004). If it cannot be met, fall back to a PostgreSQL image that bundles `pgvector`.
- **Data:** synthetic data only (ENV-2); persistent volumes live inside the kind cluster and are recreated with `make cluster-down` / `make cluster-up`.

## 6. Local Workflow
Prerequisites: Docker, kind, kubectl, helm, make, (optional) k9s.
```
make cluster-up     # kind create cluster with ingress ports (config in deploy/kind/)
make images         # build images
make load           # kind load docker-image ...
make secrets        # generate local secrets
make deploy         # helm upgrade --install aucoff deploy/helm/aucoff -f values-local.yaml
make seed           # load synthetic seed data and framework catalogue
make e2e            # Playwright E2E against the cluster
make logs / make down / make cluster-down
```
- Access via ingress hostnames (`aucoff.localtest.me`, wildcard DNS to 127.0.0.1; use `curl --resolve` when offline) or `kubectl port-forward`.
- Target: cold start of the full stack on a 16 GB laptop in < 10 minutes (proposal); lightweight profile (`values-local-min.yaml`) disables observability and extra scanners.
- LLM calls: real provider key optional locally; default to a recorded/mock provider for tests (QA-8).

## 7. CI/CD (GitHub Actions)
| Stage | Checks |
|-------|--------|
| PR | Lint, type check, unit tests (QA-7), OpenAPI drift and lint ([api-contract.md](api-contract.md) section 2), generated client build, Gitleaks, dependency audit, license check |
| Build | Docker build, Trivy scan, SBOM, sign images (cosign - TODO) |
| Chart | `helm lint`, kubeconform, policy checks (Kyverno/conftest - TODO) |
| Integration/E2E | Ephemeral kind: deploy chart, run migrations, API tests, Playwright, axe, DAST/API scan |
| Release | Tag, publish images to registry (GHCR now, ECR later), publish chart |
| Deploy (post-v1) | Terraform plan/apply with approval; Helm deploy to EKS - not part of v1 |
Branch protection requires all checks; required reviews per constitution.

## 8. Observability
- OpenTelemetry SDKs in all services export traces, metrics, logs to the OpenTelemetry Collector.
- Backends: Prometheus (metrics) plus permissively licensed log, trace and dashboard backends selected under T-009 (not Loki/Tempo/Grafana unless their licences are verified to pass constitution LIC-1/LIC-2).
- Standard dashboards: API latency/errors, queue depth and DLQ, agent run duration/cost/tokens, scanner errors, DB health, SLO (NFR-3).
- Alerts: SLO burn rate, DLQ growth, budget exceeded, failed migrations, certificate expiry.
- Logs contain no secrets or PII (COD-8); retention TODO.

## 9. Backup and Recovery
- Local: scripted `pg_dump` and object-store bucket export (database-spec section 11).
- Post-v1 (AWS): RDS automated backups + PITR, S3 versioning, cross-region replication per residency rules; RPO/RTO from database-spec TODO.
- Restore drills documented and executed per phase.

## 10. Post-v1: AWS Migration Notes (informational, not built in v1)
| Local | AWS equivalent | Notes |
|-------|----------------|-------|
| kind | EKS | Managed node groups; Pod Security and NetworkPolicy (VPC CNI or Cilium - TODO) |
| In-cluster PostgreSQL 18.6 + pgvector | RDS/Aurora PostgreSQL | Confirm 18.x and pgvector support ([database-spec.md](database-spec.md) section 12) |
| RabbitMQ | Amazon MQ for RabbitMQ (or self-managed) | Check engine version and DLQ setup |
| Local object store | S3 | KMS-encrypted buckets, per-region for residency |
| Keycloak | Entra ID / Cognito | OIDC issuer change only; SAML via IdP |
| K8s Secrets | Secrets Manager + External Secrets Operator | Rotation |
| cert-manager local CA | ACM + cert-manager (Let's Encrypt) | |
| NGINX ingress | ALB Ingress Controller / NLB | WAF in front (AWS WAF) |
| Local observability stack | Amazon Managed Prometheus + CloudWatch / or keep self-hosted permissive stack | Decide on cost and licence review (T-009) |
| GHCR | ECR | |
| Helm values | `values-aws.yaml` | Disable in-cluster data services |
| Manual | Terraform | Modules: network, eks, rds, mq, s3, iam (IRSA), secrets, observability; state in S3 + DynamoDB lock |
Scanners access customer accounts via customer-granted read-only roles (cross-account assume-role with external ID).

## 11. Security and Compliance
- **Platform operator access:** separate identity realm/audience, MFA, no standing access to tenant data; break-glass grants are time-limited and audited (SEC-15). Operator tooling is deployed separately from the tenant UI.
Controls referenced from constitution section 6: network policies, image scanning, non-root, RBAC least privilege, encryption in transit and at rest, audit logging of cluster changes (AWS CloudTrail/EKS audit later), no manual changes (ARC-11), dependency and SBOM tracking, regional deployment for data residency (SEC-14).

## 12. Open Questions
- [x] Ingress: Traefik (chart `traefik/traefik` 42.0.0, app v3.7.14), dashboard/API disabled; local host `aucoff.localtest.me`. ingress-nginx was the earlier choice but was retired upstream after March 2026 (no security fixes). Traefik's own `/ping` probe is a third-party platform component and is outside ZT-7, which governs AUCoFF's own components.
- [x] PostgreSQL via CloudNativePG operator; pgvector 0.8.6 (owner-confirmed with PostgreSQL 18.6). [ ] Image source/build compatible with CloudNativePG still to verify (T-004).
- [ ] Queue autoscaling approach (KEDA).
- [x] mTLS/service mesh: not needed in v1; token-based service identity over TLS (ZT-4). Revisit post-v1.
- [ ] Image registry and signing.
- [ ] (Post-v1) Observability on AWS: managed vs self-hosted.
- [ ] (Post-v1) Multi-region residency model and per-region deployments.

## Implementation status: identity and TLS (Build Session 3, 2026-10-19)

- `make certs` installs cert-manager v1.21.2 and a local CA (`ClusterIssuer aucoff-local-ca`); the CA key stays in the cluster, services get only the public certificate (ConfigMap `aucoff-identity-ca`).
- `make identity` installs chart `deploy/helm/aucoff-identity` into namespace `aucoff-identity`: Keycloak 26.8.1 pinned by digest, HTTPS only (plain HTTP and the management port are off), database `keycloak` owned by the dedicated role `aucoff_keycloak`, realm `aucoff` imported with client secrets substituted from `aucoff-keycloak-clients`.
- Realm clients: `svc-gateway` (client credentials), `aucoff-web` (authorization code + PKCE, for the BFF), and local-only `aucoff-smoke*` clients. Scopes `ops:read` and `docs:read`; audience mapper `aucoff-gateway`.
- Network policies: default deny in `aucoff-identity`; only pods labelled `aucoff.io/idp-client` in `aucoff` may reach Keycloak on 8443; Keycloak may reach DNS and PostgreSQL only. Defence in depth only; every call is also authenticated.
- `make smoke` obtains real tokens from Keycloak and asserts 200/403/401 as described in tasks T-121.

## Implementation status: messaging (Build Session 4, 2026-10-19)

- `make messaging` applies `deploy/rabbitmq/rabbitmq.yaml` into namespace `aucoff-messaging`: RabbitMQ 4.3.6 pinned by digest, AMQPS on 5671 only (certificate from the local CA), all plugins off (no management or metrics port), exec probes, read-only root filesystem, 1 GiB volume.
- Vhost `aucoff`; exchanges `aucoff.work` and `aucoff.events` (topic); one quorum inbox queue per service; users `aucoff_gateway` and `aucoff_scanner` with no configure rights, write only to the two exchanges (routing keys prefixed by the sender), and read only their own queues.
- Only pods labelled `aucoff.io/mq-client` in `aucoff` may reach the broker; defence in depth, every connection also authenticates.
