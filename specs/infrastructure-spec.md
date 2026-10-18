# AUCoFF Infrastructure Spec

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.1.0 |
| Owner | TODO |
| Last updated | TODO |

> Purpose: how AUCoFF is packaged, deployed and operated. Phase 1: local Kubernetes via Helm on a laptop. Phase 2: AWS.

Related: [design.md](design.md) · [backend-spec.md](backend-spec.md) · [frontend-spec.md](frontend-spec.md) · [database-spec.md](database-spec.md)

## 1. Environments
| Env | Platform | Purpose | Status |
|-----|----------|---------|--------|
| local | Local Kubernetes (kind / minikube / Docker Desktop - TODO) | Dev and testing | Phase 1 |
| aws | AWS (see section 7) | Staging / prod | Phase 2 |

## 2. Containers
| Image | Source | Base image | Port | Health check |
|-------|--------|------------|------|--------------|
| aucoff-frontend | `frontend/` | TODO | TODO | TODO |
| aucoff-backend | `backend/` | TODO | TODO | TODO |
| TODO (worker, db, vector store) | TODO | TODO | TODO | TODO |

## 3. Helm Chart
```
deploy/helm/aucoff/
  Chart.yaml
  values.yaml
  values-local.yaml
  templates/
```
- Single umbrella chart vs sub-charts: TODO
- Resources deployed: TODO
- Key `values.yaml` settings (image tags, replicas, resources, ingress host): TODO

## 4. Local Workflow
- Prerequisites (docker, kubectl, helm, kind/minikube): TODO
- Build and load images: TODO
- Install: `helm upgrade --install aucoff deploy/helm/aucoff -f values-local.yaml` (TODO confirm)
- Access (ingress / port-forward): TODO
- Teardown: TODO

## 5. Configuration and Secrets
Config maps, secrets (LLM API keys, DB creds) in local k8s: TODO

## 6. Data Services
- PostgreSQL 18.6 with pgvector: in-cluster for local (StatefulSet or operator, PVC, NetworkPolicy allowing only backend/worker pods, TLS, credentials from Kubernetes Secrets); managed RDS/Aurora on AWS. Details in [database-spec.md](database-spec.md).
- Migrations run as a Helm pre-upgrade hook Job using the `aucoff_migrator` role.
- Object store and queue: TODO.

## 7. AWS Migration Notes (future)
<!-- Update when moving to AWS. -->
| Local | AWS equivalent | Notes |
|-------|----------------|-------|
| kind / minikube | EKS | TODO |
| In-cluster PostgreSQL 18.6 + pgvector | RDS / Aurora PostgreSQL | Confirm 18.x and pgvector support; see [database-spec.md](database-spec.md) section 12 |
| k8s Secrets | Secrets Manager + External Secrets | TODO |
| Local registry | ECR | TODO |
| Ingress | ALB Ingress Controller | TODO |
| Logs / metrics | CloudWatch / managed Prometheus | TODO |
| IaC | Terraform (TODO confirm) | TODO |

## 8. CI/CD
Build, test, scan, publish, deploy pipeline: TODO

## 9. Observability
Logs, metrics, traces, dashboards, alerts: TODO

## 10. Security and Compliance
Network policies, image scanning, RBAC, encryption, backups: TODO
