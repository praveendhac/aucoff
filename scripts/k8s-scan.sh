#!/usr/bin/env bash
# Scan the current kubectl cluster with the read-only scanner identity (T-203, backend-spec 7).
# Creates a short-lived token for the aucoff-k8s-scanner service account; nothing is stored but the
# report and the hashed evidence under build/k8s-scan/ (git-ignored).
set -euo pipefail
OUT=${OUT:-build/k8s-scan}
kubectl apply -f deploy/scanner/k8s-readonly-rbac.yaml >/dev/null
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
kubectl -n aucoff-scanner create token aucoff-k8s-scanner --duration 15m > "$tmp/token"
kubectl config view --raw --minify -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d > "$tmp/ca.crt"
server=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
rm -rf "$OUT"; mkdir -p "$OUT"
(cd backend && uv run python -m services.k8s_scanner.run --server "$server" --ca "$tmp/ca.crt" \
  --token-file "$tmp/token" --rule-pack ../data/checks/kubernetes.yaml --controls ../data/controls \
  --out "../$OUT")
