"""Kubernetes connector: validates read-only access, then collects raw documents (spec 7)."""

import json
from typing import Any

from app.domain.scanning import Collection, RawDocument, Scope, ValidationReport
from services.k8s_scanner.client import KubeApiError, KubeApiLike

# (document name, API path, group, resource) of everything the scanner reads
READS: list[tuple[str, str, str, str]] = [
    ("namespaces", "/api/v1/namespaces", "", "namespaces"),
    ("pods", "/api/v1/pods", "", "pods"),
    (
        "networkpolicies",
        "/apis/networking.k8s.io/v1/networkpolicies",
        "networking.k8s.io",
        "networkpolicies",
    ),
    (
        "clusterroles",
        "/apis/rbac.authorization.k8s.io/v1/clusterroles",
        "rbac.authorization.k8s.io",
        "clusterroles",
    ),
    (
        "clusterrolebindings",
        "/apis/rbac.authorization.k8s.io/v1/clusterrolebindings",
        "rbac.authorization.k8s.io",
        "clusterrolebindings",
    ),
]

# A scanner credential must NOT be able to change anything or read secrets.
FORBIDDEN: list[tuple[str, str, str]] = [
    ("get", "", "secrets"),
    ("list", "", "secrets"),
    ("create", "", "pods"),
    ("delete", "", "pods"),
    ("update", "", "configmaps"),
    ("create", "rbac.authorization.k8s.io", "clusterrolebindings"),
    ("create", "apps", "deployments"),
    ("delete", "", "namespaces"),
]


def _label(verb: str, group: str, resource: str) -> str:
    return f"{verb} {group + '/' if group else ''}{resource}"


class KubernetesConnector:
    def __init__(self, api: KubeApiLike) -> None:
        self._api = api

    def describe_permissions(self) -> list[str]:
        return [_label("list", g, r) for _, _, g, r in READS]

    def validate(self) -> ValidationReport:
        missing: list[str] = []
        excessive: list[str] = []
        for _, _, group, resource in READS:
            if not self._api.can_i("list", group, resource):
                missing.append(_label("list", group, resource))
        for verb, group, resource in FORBIDDEN:
            if self._api.can_i(verb, group, resource):
                excessive.append(_label(verb, group, resource))
        return ValidationReport(
            ok=not missing and not excessive, missing=missing, excessive=excessive
        )

    def collect(self, scope: Scope) -> Collection:
        documents: list[RawDocument] = []
        errors: list[str] = []
        for name, path, _, _ in READS:
            try:
                items = self._api.list_items(path)
            except KubeApiError as exc:
                errors.append(f"{name}: {exc}")  # recorded; the checks on it become 'error'
                continue
            if scope.namespaces is not None and name in ("pods", "networkpolicies", "namespaces"):
                items = [i for i in items if _namespace_of(name, i) in scope.namespaces]
            body = json.dumps({"kind": name, "items": items}, sort_keys=True, separators=(",", ":"))
            documents.append(
                RawDocument(
                    name=name, content=body.encode(), source_ref=f"k8s:{self._api.server}{path}"
                )
            )
        return Collection(documents=documents, errors=errors)


def _namespace_of(kind: str, item: dict[str, Any]) -> str:
    meta = item.get("metadata", {})
    return str(meta.get("name") if kind == "namespaces" else meta.get("namespace", ""))
