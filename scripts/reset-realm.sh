#!/usr/bin/env bash
# Delete the Keycloak realm `aucoff` and restart Keycloak so the realm is imported again from the
# chart. Needed after a realm change because Keycloak only imports a realm that does not exist yet.
# Local development only: all users and sessions in the realm are lost.
set -euo pipefail
NS=aucoff-identity
H=aucoff-keycloak.$NS.svc
tmp=$(mktemp); trap 'kill $pf 2>/dev/null; rm -f "$tmp"' EXIT
kubectl -n cert-manager get secret aucoff-local-ca -o jsonpath='{.data.tls\.crt}' | base64 -d > "$tmp"
kubectl -n $NS port-forward svc/aucoff-keycloak 18444:8443 >/dev/null 2>&1 & pf=$!
for _ in $(seq 1 20); do nc -z 127.0.0.1 18444 2>/dev/null && break; sleep 0.5; done
R=(--cacert "$tmp" --resolve "$H:18444:127.0.0.1")
pw=$(kubectl -n $NS get secret aucoff-keycloak-admin -o jsonpath='{.data.password}' | base64 -d)
tok=$(curl -s "${R[@]}" -d grant_type=password -d client_id=admin-cli -d username=admin --data-urlencode "password=$pw" \
  "https://$H:18444/realms/master/protocol/openid-connect/token" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -o /dev/null -w "delete realm: %{http_code}\n" "${R[@]}" -X DELETE -H "Authorization: Bearer $tok" "https://$H:18444/admin/realms/aucoff"
kubectl -n $NS rollout restart deploy/aucoff-keycloak >/dev/null
kubectl -n $NS rollout status deploy/aucoff-keycloak --timeout=300s
