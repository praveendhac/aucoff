#!/usr/bin/env bash
# Publish the local CA's PUBLIC certificate to the aucoff namespace so services can verify the
# identity provider's TLS certificate (constitution ZT-4). The CA private key is never copied.
set -euo pipefail
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
kubectl -n cert-manager get secret aucoff-local-ca -o jsonpath='{.data.tls\.crt}' | base64 -d > "$tmp"
kubectl -n aucoff create configmap aucoff-identity-ca --from-file=ca.crt="$tmp" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
echo "configmap aucoff-identity-ca ready in namespace aucoff"
