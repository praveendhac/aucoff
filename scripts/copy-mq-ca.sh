#!/usr/bin/env bash
# Publish the message broker's CA certificate (public) to the aucoff namespace (ZT-4).
set -euo pipefail
tmp=$(mktemp); trap 'rm -f "$tmp"' EXIT
kubectl -n aucoff-messaging get secret aucoff-rabbitmq-tls -o jsonpath='{.data.ca\.crt}' | base64 -d > "$tmp"
kubectl -n aucoff create configmap aucoff-mq-ca --from-file=ca.crt="$tmp" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
echo "configmap aucoff-mq-ca ready in namespace aucoff"
