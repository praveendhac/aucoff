# AUCoFF developer commands. v1 is local-only (kind); there are no deploy targets for any cloud.
.DEFAULT_GOAL := help
SHELL := /bin/bash
CLUSTER := aucoff
SPECTRAL := npx --yes @stoplight/spectral-cli@6

.PHONY: help doctor setup lint typecheck test openapi openapi-check spectral licences helm-lint check \
        backend-run frontend-dev cluster-up cluster-down

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

helm-lint: ## Lint the Helm chart
	helm lint deploy/helm/aucoff -f deploy/helm/aucoff/values-local.yaml

check: lint typecheck test openapi-check spectral licences helm-lint ## Everything CI runs

backend-run: ## Run the API locally on :8000
	cd backend && uv run uvicorn app.main:app --reload --port 8000

frontend-dev: ## Run the web app locally on :3000
	cd frontend && npm run dev

cluster-up: ## Create the local kind cluster
	kind create cluster --config deploy/kind/kind-config.yaml

cluster-down: ## Delete the local kind cluster
	kind delete cluster --name $(CLUSTER)
