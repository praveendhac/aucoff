#!/usr/bin/env bash
# Generate unique per-service credentials for the local cluster (constitution ZT-4, ZT-6).
# Idempotent: existing secrets are kept. Nothing is written to disk or git; values only live in
# Kubernetes Secrets. Local-only (a managed secret store is post-v1).
set -euo pipefail

rand() { openssl rand -base64 36 | tr -d '/+=\n' | cut -c1-40; }

# ensure_basic_auth name user namespace...  (same generated password in every namespace listed;
# the first namespace is the source of truth when it already exists)
ensure_basic_auth() {
  local name=$1 user=$2 pw first; shift 2
  first=$1
  if kubectl -n "$first" get secret "$name" >/dev/null 2>&1; then
    pw=$(kubectl -n "$first" get secret "$name" -o jsonpath='{.data.password}' | base64 -d)
  else
    pw=$(rand)
  fi
  for ns in "$@"; do
    kubectl -n "$ns" create secret generic "$name" --type=kubernetes.io/basic-auth \
      --from-literal=username="$user" --from-literal=password="$pw" \
      --dry-run=client -o yaml | kubectl -n "$ns" apply -f - >/dev/null
  done
  kubectl -n aucoff-data label secret "$name" cnpg.io/reload=true --overwrite >/dev/null 2>&1 || true
  echo "secret $name ready (user $user)"
}

# ensure_client_secrets secret-name KEY...  (one random value per key, kept if already present)
ensure_client_secrets() {
  local name=$1; shift
  local args=() key val
  for key in "$@"; do
    val=$(kubectl -n aucoff-identity get secret "$name" -o jsonpath="{.data.$key}" 2>/dev/null | base64 -d || true)
    [ -n "$val" ] || val=$(rand)
    args+=(--from-literal="$key=$val")
  done
  kubectl -n aucoff-identity create secret generic "$name" "${args[@]}" \
    --dry-run=client -o yaml | kubectl -n aucoff-identity apply -f - >/dev/null
  echo "secret $name ready (${#} keys)"
}

kubectl create namespace aucoff --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl apply -f deploy/postgres/namespace.yaml >/dev/null
kubectl create namespace aucoff-identity --dry-run=client -o yaml | kubectl apply -f - >/dev/null

ensure_basic_auth aucoff-pg-migrator aucoff_migrator aucoff-data aucoff
ensure_basic_auth aucoff-pg-gateway aucoff_gateway aucoff-data aucoff
ensure_basic_auth aucoff-pg-keycloak aucoff_keycloak aucoff-data aucoff-identity

# Keycloak: temporary bootstrap admin (reachable only through kubectl port-forward) and the OAuth2
# client secrets that the realm import substitutes for ${...} placeholders.
ensure_basic_auth aucoff-keycloak-admin admin aucoff-identity
ensure_client_secrets aucoff-keycloak-clients \
  SVC_GATEWAY_SECRET WEB_SECRET DEV_USER_PASSWORD SMOKE_SECRET SMOKE_OTHERAUD_SECRET SMOKE_SHORT_SECRET

# The gateway's own service-identity secret, mounted by the gateway for outbound calls (T-121).
gw=$(kubectl -n aucoff-identity get secret aucoff-keycloak-clients -o jsonpath='{.data.SVC_GATEWAY_SECRET}' | base64 -d)
kubectl -n aucoff create secret generic aucoff-svc-gateway \
  --from-literal=client_id=svc-gateway --from-literal=client_secret="$gw" \
  --dry-run=client -o yaml | kubectl -n aucoff apply -f - >/dev/null
echo "secret aucoff-svc-gateway ready"

# The web BFF (Auth.js): its OIDC client credentials and a random key that encrypts session cookies.
web=$(kubectl -n aucoff-identity get secret aucoff-keycloak-clients -o jsonpath='{.data.WEB_SECRET}' | base64 -d)
sess=$(kubectl -n aucoff get secret aucoff-web-session -o jsonpath='{.data.secret}' 2>/dev/null | base64 -d || true)
[ -n "$sess" ] || sess=$(openssl rand -base64 48 | tr -d '\n')
kubectl -n aucoff create secret generic aucoff-web-oidc \
  --from-literal=client_id=aucoff-web --from-literal=client_secret="$web" \
  --dry-run=client -o yaml | kubectl -n aucoff apply -f - >/dev/null
kubectl -n aucoff create secret generic aucoff-web-session --from-literal=secret="$sess" \
  --dry-run=client -o yaml | kubectl -n aucoff apply -f - >/dev/null
echo "secrets aucoff-web-oidc and aucoff-web-session ready"

# RabbitMQ: one user per service (ZT-5). The definitions file holds the generated passwords, so it
# lives only in a Secret. A service may configure nothing, publish only to the shared exchanges
# and read only its own queues. `aucoff_scanner` is reserved for the first scanner service.
kubectl create namespace aucoff-messaging --dry-run=client -o yaml | kubectl apply -f - >/dev/null
ensure_basic_auth aucoff-mq-gateway aucoff_gateway aucoff-messaging aucoff
ensure_basic_auth aucoff-mq-scanner aucoff_scanner aucoff-messaging aucoff
gw_pw=$(kubectl -n aucoff-messaging get secret aucoff-mq-gateway -o jsonpath='{.data.password}' | base64 -d)
sc_pw=$(kubectl -n aucoff-messaging get secret aucoff-mq-scanner -o jsonpath='{.data.password}' | base64 -d)
GW_PW="$gw_pw" SC_PW="$sc_pw" python3 - <<'PY' > /dev/stdout | kubectl -n aucoff-messaging create secret generic aucoff-rabbitmq-definitions --from-file=definitions.json=/dev/stdin --dry-run=client -o yaml | kubectl apply -f - >/dev/null
import json, os
services = {"aucoff_gateway": os.environ["GW_PW"], "aucoff_scanner": os.environ["SC_PW"]}
V = "aucoff"
defs = {
    "users": [{"name": u, "password": p, "tags": ""} for u, p in services.items()],
    "vhosts": [{"name": V}],
    "permissions": [
        # configure: nothing (no declaring/deleting); write: the shared exchanges only;
        # read: the service's own queues only.
        {"user": u, "vhost": V, "configure": "^$", "write": "^aucoff\\.(work|events)$",
         "read": "^aucoff\\." + u.split("_", 1)[1] + "\\..*"}
        for u in services
    ],
    "topic_permissions": [
        # Routing keys start with the sender: work.<sender>.<recipient>.<type>, events.<sender>.<type>.
        {"user": u, "vhost": V, "exchange": "aucoff.work", "write": "^work\\." + u.split("_", 1)[1] + "\\..*", "read": "^$"}
        for u in services
    ] + [
        {"user": u, "vhost": V, "exchange": "aucoff.events", "write": "^events\\." + u.split("_", 1)[1] + "\\..*", "read": "^events\\..*"}
        for u in services
    ],
    "exchanges": [
        {"name": "aucoff.work", "vhost": V, "type": "topic", "durable": True, "auto_delete": False, "internal": False, "arguments": {}},
        {"name": "aucoff.events", "vhost": V, "type": "topic", "durable": True, "auto_delete": False, "internal": False, "arguments": {}},
    ],
    "queues": [
        {"name": f"aucoff.{u.split('_', 1)[1]}.inbox", "vhost": V, "durable": True, "auto_delete": False, "arguments": {"x-queue-type": "quorum"}}
        for u in services
    ],
    "bindings": [
        {"source": "aucoff.work", "vhost": V, "destination": f"aucoff.{u.split('_', 1)[1]}.inbox", "destination_type": "queue", "routing_key": f"work.*.{u.split('_', 1)[1]}.#", "arguments": {}}
        for u in services
    ],
}
print(json.dumps(defs))
PY
echo "secret aucoff-rabbitmq-definitions ready"
