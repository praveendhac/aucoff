#!/usr/bin/env bash
# Copy the PostgreSQL server CA certificate (public, not a secret key) into every namespace whose
# services connect to the database, so they can verify its TLS certificate (constitution DB-5).
set -euo pipefail
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
kubectl -n aucoff-data get secret aucoff-pg-ca -o jsonpath='{.data.ca\.crt}' | base64 -d > "$tmp"
for ns in aucoff aucoff-identity; do
  kubectl create namespace "$ns" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
  kubectl -n "$ns" create configmap aucoff-pg-ca --from-file=ca.crt="$tmp" \
    --dry-run=client -o yaml | kubectl apply -f - >/dev/null
  echo "configmap aucoff-pg-ca ready in namespace $ns"
done
