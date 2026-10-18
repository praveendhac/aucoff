# AUCoFF developer commands. v1 is local-only (kind); there are no deploy targets for any cloud.
.DEFAULT_GOAL := help
SHELL := /bin/bash
CLUSTER := aucoff
SPECTRAL := npx --yes @stoplight/spectral-cli@6

.PHONY: help doctor setup lint typecheck test openapi openapi-check spectral licences helm-lint check \
        backend-run frontend-dev cluster-up cluster-down images load ingress operators secrets postgres deploy smoke up

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

doctor: ## Check required tools
	@for t in docker kind kubectl helm uv node npm gitleaks; do \
	  if command -v $$t >/dev/null 2>&1; then printf "  ok       %s\n" $$t; else printf "  MISSING  %s\n" $$t; fi; done
	@docker info >/dev/null 2>&1 && echo "  ok       docker daemon running" || echo "  NOT RUNNING  docker daemon (e.g. run: colima start)"

setup: ## Install backend and frontend dependencies
	cd backend && uv sync
	cd frontend && npm install

lint: ## Lint and format-check backend and frontend
	cd backend && uv run ruff check . && uv run ruff format --check .
	cd frontend && npm run -s lint && npm run -s format:check

typecheck: ## Type-check backend (mypy) and frontend (tsc)
	cd backend && uv run mypy
	cd frontend && npm run -s typecheck

test: ## Run backend (pytest) and frontend (vitest) tests
	cd backend && uv run pytest -q
	cd frontend && npm run -s test

openapi: ## Regenerate backend/openapi.yaml
	cd backend && uv run python -m scripts.export_openapi

openapi-check: ## Fail if backend/openapi.yaml is stale (APIR-2)
	cd backend && uv run python -m scripts.export_openapi --check

spectral: ## Lint the OpenAPI document with Spectral (APIR-1)
	cd backend && $(SPECTRAL) lint openapi.yaml --ruleset .spectral.yaml --fail-severity=warn

licences: ## Licence gate for Python and npm dependencies (LIC-1, LIC-2, LIC-5)
	cd backend && uv run python -m scripts.check_licences
	cd frontend && npm run -s licences && npm run -s audit:prod

helm-lint: ## Lint the Helm chart and fail on anonymous HTTP probes (ZT-7, ZT-8)
	helm lint deploy/helm/aucoff -f deploy/helm/aucoff/values-local.yaml
	@if helm template aucoff deploy/helm/aucoff -f deploy/helm/aucoff/values-local.yaml | grep -n httpGet; then \
	  echo "ERROR: httpGet probes are not allowed (constitution ZT-7); use exec probes"; exit 1; fi
	@echo "no httpGet probes: ok"

check: lint typecheck test openapi-check spectral licences helm-lint ## Everything CI runs

backend-run: ## Run the API on :8000 (needs AUCOFF_OIDC_ISSUER, _AUDIENCE, _JWKS_URL; it refuses to start without them)
	cd backend && uv run uvicorn app.main:create_app --factory --reload --port 8000

frontend-dev: ## Run the web app locally on :3000
	cd frontend && npm run dev

cluster-up: ## Create the local kind cluster
	kind create cluster --config deploy/kind/kind-config.yaml

cluster-down: ## Delete the local kind cluster
	kind delete cluster --name $(CLUSTER)

images: ## Build the backend and frontend container images
	docker build -t aucoff-backend:dev backend
	docker build -t aucoff-frontend:dev frontend

load: ## Load the images into the kind cluster
	kind load docker-image aucoff-backend:dev aucoff-frontend:dev --name $(CLUSTER)

ingress: ## Install the Traefik ingress controller (ingress-nginx is retired)
	helm repo add traefik https://traefik.github.io/charts >/dev/null 2>&1 || true
	helm repo update traefik >/dev/null
	helm upgrade --install traefik traefik/traefik --version 42.0.0 -n traefik --create-namespace \
	  -f deploy/traefik/values-local.yaml --wait --timeout 3m

operators: ## Install the CloudNativePG operator (PostgreSQL)
	helm repo add cnpg https://cloudnative-pg.github.io/charts >/dev/null 2>&1 || true
	helm repo update cnpg >/dev/null
	helm upgrade --install cnpg cnpg/cloudnative-pg --version 0.29.1 -n cnpg-system --create-namespace --wait --timeout 3m

secrets: ## Generate unique per-service credentials in the cluster (idempotent; nothing is stored in git)
	scripts/make-secrets.sh

postgres: ## Create the PostgreSQL 18.6 + pgvector 0.8.6 cluster
	kubectl apply -f deploy/postgres/namespace.yaml
	kubectl apply -f deploy/postgres/cluster.yaml -f deploy/postgres/networkpolicy.yaml
	kubectl -n aucoff-data wait --for=condition=Ready cluster/aucoff-pg --timeout=300s

deploy: ## Install/upgrade the AUCoFF Helm chart into namespace aucoff
	kubectl create namespace aucoff --dry-run=client -o yaml | kubectl apply -f -
	kubectl label namespace aucoff pod-security.kubernetes.io/enforce=restricted --overwrite
	helm upgrade --install aucoff deploy/helm/aucoff -n aucoff -f deploy/helm/aucoff/values-local.yaml --wait --timeout 3m

smoke: ## Smoke test the local deployment (unauthenticated requests must be refused)
	scripts/smoke.sh

up: cluster-up ingress operators secrets postgres images load deploy smoke ## Bring the whole local stack up
