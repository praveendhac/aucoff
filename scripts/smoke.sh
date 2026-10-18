#!/usr/bin/env bash
# Smoke test for the local kind deployment (T-410). First it proves the API refuses requests without
# credentials (constitution ZT-1); then it obtains REAL tokens from Keycloak with the throwaway
# smoke clients (client-credentials grant, TLS verified against the local CA) and proves the API
# accepts a valid token, refuses a token with the wrong audience or an expired one (401), and
# answers 403 when the required scope is missing.
set -euo pipefail

NS=${NS:-aucoff}
HOST=${HOST:-aucoff.localtest.me}
fail=0
CA=$(mktemp)
kubectl -n cert-manager get secret aucoff-local-ca -o jsonpath='{.data.tls\.crt}' | base64 -d > "$CA"
check() { # description expected actual
  if [ "$2" = "$3" ]; then printf '  ok    %s (%s)\n' "$1" "$3"; else printf '  FAIL  %s: expected %s, got %s\n' "$1" "$2" "$3"; fail=1; fi
}
code() { curl -s -o /dev/null -w '%{http_code}' --max-time 10 --cacert "$CA" --resolve "$HOST:443:127.0.0.1" "https://$HOST$1"; }

echo "Deployments ready:"
kubectl -n "$NS" rollout status deployment/aucoff-backend --timeout=120s
kubectl -n "$NS" rollout status deployment/aucoff-frontend --timeout=120s

# A rollout can finish before the ingress controller has picked up the new endpoints.
for _ in $(seq 1 30); do [ "$(code /login)" = 200 ] && break; sleep 1; done

echo "Through the ingress (no credentials):"
check "plain HTTP only redirects to HTTPS" 301 "$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 --resolve "$HOST:80:127.0.0.1" "http://$HOST/")"
check "web app redirects anonymous users to login" 307 "$(code /)"
check "login page is public"                200 "$(code /login)"
check "BFF proxy refuses anonymous calls"  401 "$(code /bff/health)"
check "Auth.js session endpoint is public but empty" 200 "$(code /api/auth/session)"
check "API health refuses anonymous calls"  401 "$(code /api/v1/health)"
check "old anonymous probe path is gone"    401 "$(code /api/v1/health/live)"
check "OpenAPI refuses anonymous calls"     401 "$(code /api/v1/openapi.json)"
check "backend docs are not routed outside (web app redirects to login)" 307 "$(code /docs)"

echo "Directly against the backend pod (no credentials):"
pycode() { kubectl -n "$NS" exec deploy/aucoff-backend -- python -c "
import urllib.request, urllib.error, ssl
ctx = ssl.create_default_context(cafile='/etc/aucoff/tls/ca.crt')
ctx.check_hostname = False
try:
    print(urllib.request.urlopen('https://127.0.0.1:8000$1', context=ctx).status)
except urllib.error.HTTPError as e:
    print(e.code)"; }
check "API docs refuse anonymous calls"     401 "$(pycode /docs)"
check "ReDoc refuses anonymous calls"       401 "$(pycode /redoc)"
check "unknown paths refuse anonymous calls" 401 "$(pycode /nope)"

echo "With real tokens from Keycloak (port-forward, TLS verified against the local CA):"
IDP_NS=${IDP_NS:-aucoff-identity}
IDP_HOST=aucoff-keycloak.$IDP_NS.svc
IDP_PORT=${IDP_PORT:-18443}
workdir=$(mktemp -d)
kubectl -n "$IDP_NS" port-forward svc/aucoff-keycloak "$IDP_PORT:8443" >/dev/null 2>&1 &
pf=$!
trap 'kill $pf 2>/dev/null; rm -rf "$workdir" "$CA"' EXIT
kubectl -n cert-manager get secret aucoff-local-ca -o jsonpath='{.data.tls\.crt}' | base64 -d > "$workdir/ca.crt"
for _ in $(seq 1 20); do nc -z 127.0.0.1 "$IDP_PORT" 2>/dev/null && break; sleep 0.5; done
secret() { kubectl -n "$IDP_NS" get secret aucoff-keycloak-clients -o jsonpath="{.data.$1}" | base64 -d; }
token() { # client secret-key [scope]
  curl -s --max-time 15 --cacert "$workdir/ca.crt" --resolve "$IDP_HOST:$IDP_PORT:127.0.0.1" \
    -d grant_type=client_credentials -d "client_id=$1" -d "client_secret=$(secret "$2")" ${3:+-d "scope=$3"} \
    "https://$IDP_HOST:$IDP_PORT/realms/aucoff/protocol/openid-connect/token" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])"
}
authcode() { curl -s -o /dev/null -w '%{http_code}' --max-time 10 --cacert "$CA" --resolve "$HOST:443:127.0.0.1" -H "Authorization: Bearer $1" "https://$HOST$2"; }

good=$(token aucoff-smoke SMOKE_SECRET ops:read)
check "valid token (ops:read) is accepted"         200 "$(authcode "$good" /api/v1/health)"
check "metrics endpoint accepts a monitoring token (ops:read)" 200 "$(authcode "$good" /api/v1/metrics)"
check "metrics endpoint refuses anonymous calls" 401 "$(code /api/v1/metrics)"
check "valid token without docs:read is forbidden on OpenAPI" 403 "$(authcode "$good" /api/v1/openapi.json)"
noscope=$(token aucoff-smoke SMOKE_SECRET)
check "valid token without ops:read is forbidden"  403 "$(authcode "$noscope" /api/v1/health)"
other=$(token aucoff-smoke-otheraud SMOKE_OTHERAUD_SECRET ops:read)
check "token for a different audience is refused"  401 "$(authcode "$other" /api/v1/health)"
short=$(token aucoff-smoke-short SMOKE_SHORT_SECRET ops:read)
check "fresh short-lived token is accepted"        200 "$(authcode "$short" /api/v1/health)"
sleep 7
check "same token after it expired is refused"     401 "$(authcode "$short" /api/v1/health)"
check "garbage bearer token is refused"            401 "$(authcode not-a-jwt /api/v1/health)"
check "token signed by someone else is refused"    401 "$(authcode "${good%.*}.AAAA" /api/v1/health)"

echo "Browser-style login through Keycloak (code + PKCE) and the BFF:"
kubectl -n "$IDP_NS" port-forward svc/aucoff-keycloak 8443:8443 >/dev/null 2>&1 &
pf2=$!
trap 'kill $pf $pf2 2>/dev/null; rm -rf "$workdir" "$CA"' EXIT
for _ in $(seq 1 20); do nc -z 127.0.0.1 8443 2>/dev/null && break; sleep 0.5; done
python3 scripts/web-login-test.py "$workdir/ca.crt" dev.admin 200 || fail=1
echo "Same flow as an executive (role without ops:read must get 403 from the API):"
python3 scripts/web-login-test.py "$workdir/ca.crt" dev.exec 403 || fail=1

echo "Message broker permissions (in-cluster service pod):"
scripts/run-broker-test.sh 2>&1 | grep -v "error when creating transport" || fail=1

echo "Cluster hygiene:"
for ns in "$NS" "$IDP_NS" aucoff-messaging; do
  httpget=$(kubectl -n "$ns" get pods -o json | grep -c '"httpGet"' || true)
  check "no httpGet probes on pods in $ns" 0 "$httpget"
  nonroot=$(kubectl -n "$ns" get pods -o jsonpath='{range .items[*]}{.spec.securityContext.runAsNonRoot}{"\n"}{end}' | grep -vc true || true)
  check "every pod in $ns runs as non-root" 0 "$nonroot"
done

[ "$fail" = 0 ] && echo "SMOKE TEST PASSED" || { echo "SMOKE TEST FAILED"; exit 1; }
