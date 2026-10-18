#!/usr/bin/env bash
# Generate unique per-service credentials for the local cluster (constitution ZT-4, ZT-6).
# Idempotent: existing secrets are kept. Nothing is written to disk or git; values only live in
# Kubernetes Secrets. Local-only (a managed secret store is post-v1).
set -euo pipefail

rand() { openssl rand -base64 36 | tr -d '/+=\n' | cut -c1-40; }

ensure_basic_auth() { # name user (creates in both namespaces with the same generated password)
  local name=$1 user=$2 pw
  if kubectl -n aucoff-data get secret "$name" >/dev/null 2>&1; then
    pw=$(kubectl -n aucoff-data get secret "$name" -o jsonpath='{.data.password}' | base64 -d)
  else
    pw=$(rand)
  fi
  for ns in aucoff-data aucoff; do
    kubectl -n "$ns" create secret generic "$name" --type=kubernetes.io/basic-auth \
      --from-literal=username="$user" --from-literal=password="$pw" \
      --dry-run=client -o yaml | kubectl -n "$ns" apply -f - >/dev/null
  done
  kubectl -n aucoff-data label secret "$name" cnpg.io/reload=true --overwrite >/dev/null
  echo "secret $name ready (user $user)"
}

kubectl create namespace aucoff --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl apply -f deploy/postgres/namespace.yaml >/dev/null
ensure_basic_auth aucoff-pg-migrator aucoff_migrator
ensure_basic_auth aucoff-pg-gateway aucoff_gateway
