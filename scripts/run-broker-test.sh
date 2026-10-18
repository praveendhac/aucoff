#!/usr/bin/env bash
# Run scripts/broker-test.py inside the cluster as a throwaway service pod (backend image) and
# print its result. The pod is labelled as a broker client and removed afterwards.
set -euo pipefail
NS=aucoff
gw=$(kubectl -n $NS get secret aucoff-mq-gateway -o jsonpath='{.data.password}' | base64 -d)
sc=$(kubectl -n $NS get secret aucoff-mq-scanner -o jsonpath='{.data.password}' | base64 -d)
overrides='{"spec":{"automountServiceAccountToken":false,"securityContext":{"runAsNonRoot":true,"runAsUser":10001,"seccompProfile":{"type":"RuntimeDefault"}},
"volumes":[{"name":"ca","configMap":{"name":"aucoff-mq-ca"}}],
"containers":[{"name":"mqtest","image":"aucoff-backend:dev","imagePullPolicy":"IfNotPresent","stdin":true,"stdinOnce":true,
"command":["python","-"],"volumeMounts":[{"name":"ca","mountPath":"/etc/mqca"}],
"env":[{"name":"MQ_HOST","value":"aucoff-rabbitmq.aucoff-messaging.svc"},{"name":"MQ_CA","value":"/etc/mqca/ca.crt"},
{"name":"GW_PASSWORD","value":"'"$gw"'"},{"name":"SC_PASSWORD","value":"'"$sc"'"}],
"securityContext":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]}}}]}}'
kubectl -n $NS delete pod mqtest --ignore-not-found >/dev/null
kubectl -n $NS run mqtest --rm -i --restart=Never --quiet --image=aucoff-backend:dev \
  --labels=app.kubernetes.io/part-of=aucoff,aucoff.io/mq-client=true --overrides="$overrides" < scripts/broker-test.py
