"""Built-in Kubernetes checks (AUCoFF rule pack 0.1.0). Pure functions over collected documents.

Every function returns one result per resource it evaluated. Objects that Kubernetes itself ships
(RBAC defaults labelled `kubernetes.io/bootstrapping: rbac-defaults`) are reported as
`not_applicable` with a reason, never silently skipped.
"""

from collections.abc import Iterator
from datetime import datetime
from typing import Any

from app.domain.controls import Severity
from app.domain.scanning import CheckResult, CheckStatus, RulePack

TOOL = "aucoff-k8s"


class Context:
    def __init__(
        self, pack: RulePack, observed_at: datetime, evidence_refs: dict[str, str]
    ) -> None:
        self.pack = pack
        self.observed_at = observed_at
        self.evidence_refs = evidence_refs
        self._severity = {c.tool_check_id: c.severity for c in pack.checks}

    def result(
        self, check_id: str, document: str, resource_ref: str, ok: bool | None, detail: str
    ) -> CheckResult:
        """ok=True pass, False fail, None not applicable."""
        status = (
            CheckStatus.NOT_APPLICABLE
            if ok is None
            else CheckStatus.PASS
            if ok
            else CheckStatus.FAIL
        )
        return CheckResult(
            check_id=check_id,
            tool=self.pack.tool,
            tool_version=self.pack.tool_version,
            rule_pack_version=self.pack.rule_pack_version,
            resource_ref=resource_ref,
            status=status,
            severity=self._severity.get(check_id, Severity.MEDIUM),
            observed_at=self.observed_at,
            evidence_ref=self.evidence_refs.get(document, ""),
            detail=detail,
        )

    def error(self, check_id: str, document: str, reason: str) -> CheckResult:
        return CheckResult(
            check_id=check_id,
            tool=self.pack.tool,
            tool_version=self.pack.tool_version,
            rule_pack_version=self.pack.rule_pack_version,
            resource_ref=f"document/{document}",
            status=CheckStatus.ERROR,
            severity=self._severity.get(check_id, Severity.MEDIUM),
            observed_at=self.observed_at,
            evidence_ref=self.evidence_refs.get(document, ""),
            detail=reason,
        )


def _containers(pod: dict[str, Any]) -> Iterator[dict[str, Any]]:
    spec = pod.get("spec", {})
    yield from spec.get("initContainers", []) or []
    yield from spec.get("containers", []) or []


def _pod_ref(pod: dict[str, Any], container: dict[str, Any]) -> str:
    meta = pod.get("metadata", {})
    ns, name = meta.get("namespace", ""), meta.get("name", "")
    return f"pod/{ns}/{name}/container/{container.get('name', '')}"


def pod_checks(pods: list[dict[str, Any]], ctx: Context) -> list[CheckResult]:
    out: list[CheckResult] = []
    for pod in pods:
        if pod.get("status", {}).get("phase") in ("Succeeded", "Failed"):
            continue  # finished pods are not running workload
        pod_sc = pod.get("spec", {}).get("securityContext", {}) or {}
        for c in _containers(pod):
            sc = c.get("securityContext", {}) or {}
            ref = _pod_ref(pod, c)
            privileged = bool(sc.get("privileged", False))
            out.append(
                ctx.result(
                    "k8s.pod.privileged",
                    "pods",
                    ref,
                    not privileged,
                    "runs privileged" if privileged else "not privileged",
                )
            )
            non_root = (
                sc.get("runAsNonRoot") is True
                or (isinstance(sc.get("runAsUser"), int) and sc["runAsUser"] > 0)
                or (sc.get("runAsNonRoot") is None and pod_sc.get("runAsNonRoot") is True)
                or (
                    sc.get("runAsUser") is None
                    and isinstance(pod_sc.get("runAsUser"), int)
                    and pod_sc["runAsUser"] > 0
                )
            )
            out.append(
                ctx.result(
                    "k8s.pod.run-as-non-root",
                    "pods",
                    ref,
                    non_root,
                    "non-root enforced" if non_root else "may run as root",
                )
            )
            ro = sc.get("readOnlyRootFilesystem") is True
            out.append(
                ctx.result(
                    "k8s.pod.read-only-rootfs",
                    "pods",
                    ref,
                    ro,
                    "read-only root filesystem" if ro else "writable root filesystem",
                )
            )
            limits = (c.get("resources", {}) or {}).get("limits", {}) or {}
            has_limits = "cpu" in limits and "memory" in limits
            out.append(
                ctx.result(
                    "k8s.pod.resource-limits",
                    "pods",
                    ref,
                    has_limits,
                    "cpu and memory limits set" if has_limits else "cpu or memory limit missing",
                )
            )
            digest = "@sha256:" in str(c.get("image", ""))
            out.append(
                ctx.result(
                    "k8s.pod.image-digest",
                    "pods",
                    ref,
                    digest,
                    "image pinned by digest" if digest else "image referenced by tag",
                )
            )
    return out


def namespace_checks(
    namespaces: list[dict[str, Any]], policies: list[dict[str, Any]], ctx: Context
) -> list[CheckResult]:
    out: list[CheckResult] = []
    deny_ingress: set[str] = set()
    for p in policies:
        spec = p.get("spec", {})
        if (
            not spec.get("podSelector")
            and "Ingress" in (spec.get("policyTypes") or [])
            and not spec.get("ingress")
        ):
            deny_ingress.add(p.get("metadata", {}).get("namespace", ""))
    for ns in namespaces:
        meta = ns.get("metadata", {})
        name = meta.get("name", "")
        ref = f"namespace/{name}"
        has = name in deny_ingress
        out.append(
            ctx.result(
                "k8s.namespace.default-deny-ingress",
                "networkpolicies",
                ref,
                has,
                "default-deny ingress policy present" if has else "no default-deny ingress policy",
            )
        )
        level = (meta.get("labels") or {}).get("pod-security.kubernetes.io/enforce", "")
        enforced = level in ("baseline", "restricted")
        out.append(
            ctx.result(
                "k8s.namespace.pod-security-enforced",
                "namespaces",
                ref,
                enforced,
                f"enforce level: {level}" if level else "no enforce level set",
            )
        )
    return out


def _is_builtin(obj: dict[str, Any]) -> bool:
    labels = obj.get("metadata", {}).get("labels") or {}
    return labels.get("kubernetes.io/bootstrapping") == "rbac-defaults"


def rbac_checks(
    roles: list[dict[str, Any]], bindings: list[dict[str, Any]], ctx: Context
) -> list[CheckResult]:
    out: list[CheckResult] = []
    for role in roles:
        name = role.get("metadata", {}).get("name", "")
        ref = f"clusterrole/{name}"
        if _is_builtin(role):
            out.append(
                ctx.result(
                    "k8s.rbac.wildcard-rules",
                    "clusterroles",
                    ref,
                    None,
                    "built-in role shipped by Kubernetes",
                )
            )
            continue
        wild = any(
            "*" in (r.get("verbs") or []) or "*" in (r.get("resources") or [])
            for r in role.get("rules", []) or []
        )
        out.append(
            ctx.result(
                "k8s.rbac.wildcard-rules",
                "clusterroles",
                ref,
                not wild,
                "wildcard verbs or resources" if wild else "no wildcard rules",
            )
        )
    for b in bindings:
        if b.get("roleRef", {}).get("name") != "cluster-admin":
            continue
        name = b.get("metadata", {}).get("name", "")
        ref = f"clusterrolebinding/{name}"
        if _is_builtin(b):
            out.append(
                ctx.result(
                    "k8s.rbac.cluster-admin-binding",
                    "clusterrolebindings",
                    ref,
                    None,
                    "built-in binding shipped by Kubernetes",
                )
            )
            continue
        subjects = [f"{s.get('kind')}/{s.get('name')}" for s in b.get("subjects", []) or []]
        out.append(
            ctx.result(
                "k8s.rbac.cluster-admin-binding",
                "clusterrolebindings",
                ref,
                False,
                "cluster-admin granted to: " + ", ".join(subjects),
            )
        )
    return out
