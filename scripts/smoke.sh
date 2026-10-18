#!/usr/bin/env bash
# Smoke test for the local kind deployment (T-410). Every check is anonymous-safe: the point of the
# test is that the API refuses unauthenticated requests (constitution ZT-1). Authenticated checks
# arrive with the identity provider (Session 3).
set -euo pipefail

NS=${NS:-aucoff}
HOST=${HOST:-aucoff.localtest.me}
fail=0
check() { # description expected actual
  if [ "$2" = "$3" ]; then printf '  ok    %s (%s)\n' "$1" "$3"; else printf '  FAIL  %s: expected %s, got %s\n' "$1" "$2" "$3"; fail=1; fi
}
code() { curl -s -o /dev/null -w '%{http_code}' --max-time 10 --resolve "$HOST:80:127.0.0.1" "http://$HOST$1"; }

echo "Deployments ready:"
kubectl -n "$NS" rollout status deployment/aucoff-backend --timeout=120s
kubectl -n "$NS" rollout status deployment/aucoff-frontend --timeout=120s

echo "Through the ingress (no credentials):"
check "frontend login shell is public"      200 "$(code /)"
check "API health refuses anonymous calls"  401 "$(code /api/v1/health)"
check "old anonymous probe path is gone"    401 "$(code /api/v1/health/live)"
check "OpenAPI refuses anonymous calls"     401 "$(code /api/v1/openapi.json)"
check "backend docs are not routed outside"  404 "$(code /docs)"

echo "Directly against the backend pod (no credentials):"
pycode() { kubectl -n "$NS" exec deploy/aucoff-backend -- python -c "
import urllib.request, urllib.error
try:
    print(urllib.request.urlopen('http://127.0.0.1:8000$1').status)
except urllib.error.HTTPError as e:
    print(e.code)"; }
check "API docs refuse anonymous calls"     401 "$(pycode /docs)"
check "ReDoc refuses anonymous calls"       401 "$(pycode /redoc)"
check "unknown paths refuse anonymous calls" 401 "$(pycode /nope)"

echo "Cluster hygiene:"
httpget=$(kubectl -n "$NS" get pods -o json | grep -c '"httpGet"' || true)
check "no httpGet probes on running pods" 0 "$httpget"
nonroot=$(kubectl -n "$NS" get pods -o jsonpath='{range .items[*]}{.spec.securityContext.runAsNonRoot}{"\n"}{end}' | grep -vc true || true)
check "every pod runs as non-root" 0 "$nonroot"

[ "$fail" = 0 ] && echo "SMOKE TEST PASSED" || { echo "SMOKE TEST FAILED"; exit 1; }
