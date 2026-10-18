#!/usr/bin/env bash
# Vulnerability scan and SBOM for every image the local stack runs (T-010, constitution SEC-17,
# LIC-5). Trivy (Apache-2.0) runs from a digest-pinned container. HIGH and CRITICAL findings that
# have a fix FAIL the scan; SBOMs (CycloneDX) are written to build/sbom/ (not committed).
set -euo pipefail
TRIVY=ghcr.io/aquasecurity/trivy@sha256:2416d1f74045b57274df1a340eee6b510cacd73c66a6ccb8da092b117eb7d222
IMAGES=${IMAGES:-"aucoff-backend:dev aucoff-frontend:dev
quay.io/keycloak/keycloak@sha256:79c623a22abacf3fe6c00a5fb30f5b7843d717b234033b80995891c06116d244
docker.io/library/rabbitmq@sha256:6931816af1a943f471c038b278835d36692d55dec769232739296bb91b7de0f5"}
mkdir -p build/sbom
run() { docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD/build:/work" -v "$PWD/.trivyignore:/.trivyignore:ro" -v trivy-cache:/root/.cache "$TRIVY" "$@"; }
status=0
for image in $IMAGES; do
  name=$(echo "$image" | sed 's#[/:@]#_#g' | cut -c1-60)
  docker image inspect "$image" >/dev/null 2>&1 || docker pull -q "$image" >/dev/null
  echo "== $image"
  run image --quiet --format cyclonedx --output "/work/sbom/$name.cdx.json" "$image" >/dev/null 2>&1
  if ! run image --quiet --severity HIGH,CRITICAL --ignore-unfixed --ignorefile /.trivyignore --exit-code 1 "$image" | grep -E "^Total|^$image|Legend" ; then :; fi
  run image --quiet --severity HIGH,CRITICAL --ignore-unfixed --ignorefile /.trivyignore --exit-code 1 --format json --output "/work/scan-$name.json" "$image" >/dev/null 2>&1 || status=1
  python3 - "$name" <<'PY'
import json, sys
d = json.load(open(f"build/scan-{sys.argv[1]}.json"))
n = sum(len(r.get("Vulnerabilities") or []) for r in d.get("Results", []))
print(f"   fixable HIGH/CRITICAL findings: {n}")
PY
done
[ "$status" = 0 ] && echo "IMAGE SCAN PASSED (SBOMs in build/sbom/)" || { echo "IMAGE SCAN FAILED"; exit 1; }
