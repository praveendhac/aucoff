"""Kubernetes scanner adapter: documents in, normalised check results out (backend-spec 4a)."""

import json
from datetime import datetime
from typing import Any

from app.domain.scanning import CheckResult, RawDocument, RulePack, ScannerInfo
from services.k8s_scanner import checks

REQUIRED = ["namespaces", "pods", "networkpolicies", "clusterroles", "clusterrolebindings"]


class KubernetesAdapter:
    def __init__(self, pack: RulePack) -> None:
        self._pack = pack

    def describe(self) -> ScannerInfo:
        return ScannerInfo(
            tool=self._pack.tool,
            tool_version=self._pack.tool_version,
            rule_pack_version=self._pack.rule_pack_version,
            licence=self._pack.licence,
            required_permissions=[f"list {name}" for name in REQUIRED],
        )

    def normalise(
        self, documents: dict[str, tuple[RawDocument, str]], observed_at: datetime
    ) -> list[CheckResult]:
        """`documents` maps a name to (document, evidence sha256). A missing document makes every
        check that needs it an `error` result: a partial collection is never read as a pass."""
        ctx = checks.Context(self._pack, observed_at, {n: ev for n, (_, ev) in documents.items()})

        def items(name: str) -> list[dict[str, Any]] | None:
            if name not in documents:
                return None
            parsed: dict[str, Any] = json.loads(documents[name][0].content)
            return list(parsed.get("items", []))

        pods, nss = items("pods"), items("namespaces")
        pols, roles, binds = (
            items("networkpolicies"),
            items("clusterroles"),
            items("clusterrolebindings"),
        )
        out: list[CheckResult] = []
        if pods is None:
            out += [
                ctx.error(c, "pods", "pods were not collected")
                for c in (
                    "k8s.pod.privileged",
                    "k8s.pod.run-as-non-root",
                    "k8s.pod.read-only-rootfs",
                    "k8s.pod.resource-limits",
                    "k8s.pod.image-digest",
                )
            ]
        else:
            out += checks.pod_checks(pods, ctx)
        if nss is None or pols is None:
            out += [
                ctx.error(c, "namespaces", "namespaces or network policies were not collected")
                for c in (
                    "k8s.namespace.default-deny-ingress",
                    "k8s.namespace.pod-security-enforced",
                )
            ]
        else:
            out += checks.namespace_checks(nss, pols, ctx)
        if roles is None or binds is None:
            out += [
                ctx.error(c, "clusterroles", "RBAC objects were not collected")
                for c in ("k8s.rbac.wildcard-rules", "k8s.rbac.cluster-admin-binding")
            ]
        else:
            out += checks.rbac_checks(roles, binds, ctx)
        return out
