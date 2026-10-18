#!/usr/bin/env bash
# Copy the PostgreSQL server CA certificate (public, not a secret key) into the aucoff namespace so
# services can verify the database's TLS certificate (constitution DB-5).
set -euo pipefail
kubectl -n aucoff-data get secret aucoff-pg-ca -o jsonpath='{.data.ca\.crt}' | base64 -d > /tmp/aucoff-pg-ca.crt
kubectl -n aucoff create configmap aucoff-pg-ca --from-file=ca.crt=/tmp/aucoff-pg-ca.crt \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
rm -f /tmp/aucoff-pg-ca.crt
echo "configmap aucoff-pg-ca ready in namespace aucoff"
