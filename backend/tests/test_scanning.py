"""Scanner framework: rule pack, rollup, evidence store, Kubernetes checks, connector (T-203)."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from app.domain.controls import Severity, load_catalogue
from app.domain.scanning import (
    CheckResult,
    CheckStatus,
    Evidence,
    ProposedStatus,
    RawDocument,
    Scope,
    load_rule_pack,
    rollup,
    validate_rule_pack,
)
from services.common.evidence_store import FilesystemEvidenceStore, IntegrityError
from services.k8s_scanner.adapter import KubernetesAdapter
from services.k8s_scanner.client import KubeApiError
from services.k8s_scanner.connector import FORBIDDEN, READS, KubernetesConnector

ROOT = Path(__file__).resolve().parents[2]
PACK = load_rule_pack(ROOT / "data" / "checks" / "kubernetes.yaml")
NOW = datetime(2026, 10, 20, tzinfo=UTC)


def doc(name: str, items: list[dict[str, Any]]) -> tuple[RawDocument, str]:
    body = json.dumps({"kind": name, "items": items}).encode()
    return RawDocument(name, body, f"k8s:test/{name}"), f"sha-{name}"


def pod(name: str, **container: Any) -> dict[str, Any]:
    c = {"name": "app", "image": "reg/app:1", **container}
    return {
        "metadata": {"namespace": "ns", "name": name},
        "spec": {"containers": [c]},
        "status": {"phase": "Running"},
    }


def by(results: list[CheckResult], check: str) -> list[CheckResult]:
    return [r for r in results if r.check_id == check]


def run(**docs: list[dict[str, Any]]) -> list[CheckResult]:
    full: dict[str, list[dict[str, Any]]] = {
        "pods": [],
        "namespaces": [],
        "networkpolicies": [],
        "clusterroles": [],
        "clusterrolebindings": [],
    }
    full.update(docs)
    return KubernetesAdapter(PACK).normalise({n: doc(n, i) for n, i in full.items()}, NOW)


def test_rule_pack_maps_only_to_controls_that_exist() -> None:
    controls = load_catalogue(ROOT / "data" / "controls")
    assert validate_rule_pack(PACK, controls) == []
    assert PACK.licence == "MIT"


def test_pod_checks_pass_and_fail() -> None:
    good = pod(
        "good",
        image="reg/app@sha256:" + "a" * 64,
        securityContext={"runAsNonRoot": True, "readOnlyRootFilesystem": True},
        resources={"limits": {"cpu": "1", "memory": "1Gi"}},
    )
    bad = pod("bad", securityContext={"privileged": True})
    results = run(pods=[good, bad])
    for check in (
        "privileged",
        "run-as-non-root",
        "read-only-rootfs",
        "resource-limits",
        "image-digest",
    ):
        rs = {r.resource_ref.split("/")[2]: r.status for r in by(results, f"k8s.pod.{check}")}
        assert rs == {"good": CheckStatus.PASS, "bad": CheckStatus.FAIL}, check
    assert all(r.evidence_ref == "sha-pods" for r in by(results, "k8s.pod.privileged"))


def test_pod_level_non_root_counts_and_finished_pods_are_skipped() -> None:
    p = pod("p")
    p["spec"]["securityContext"] = {"runAsUser": 1000}
    done = pod("done")
    done["status"]["phase"] = "Succeeded"
    results = run(pods=[p, done])
    assert [r.status for r in by(results, "k8s.pod.run-as-non-root")] == [CheckStatus.PASS]


def test_default_deny_and_pod_security_per_namespace() -> None:
    namespaces: list[dict[str, Any]] = [
        {"metadata": {"name": "a", "labels": {"pod-security.kubernetes.io/enforce": "restricted"}}},
        {"metadata": {"name": "b"}},
    ]
    deny = {"metadata": {"namespace": "a"}, "spec": {"podSelector": {}, "policyTypes": ["Ingress"]}}
    results = run(namespaces=namespaces, networkpolicies=[deny])
    deny_r = {r.resource_ref: r.status for r in by(results, "k8s.namespace.default-deny-ingress")}
    assert deny_r == {"namespace/a": CheckStatus.PASS, "namespace/b": CheckStatus.FAIL}
    psa = {r.resource_ref: r.status for r in by(results, "k8s.namespace.pod-security-enforced")}
    assert psa == {"namespace/a": CheckStatus.PASS, "namespace/b": CheckStatus.FAIL}


def test_policy_that_allows_ingress_is_not_default_deny() -> None:
    allow = {
        "metadata": {"namespace": "a"},
        "spec": {"podSelector": {}, "policyTypes": ["Ingress"], "ingress": [{}]},
    }
    results = run(namespaces=[{"metadata": {"name": "a"}}], networkpolicies=[allow])
    assert by(results, "k8s.namespace.default-deny-ingress")[0].status is CheckStatus.FAIL


def test_rbac_wildcards_and_cluster_admin_with_builtin_exclusion() -> None:
    builtin = {
        "metadata": {
            "name": "cluster-admin",
            "labels": {"kubernetes.io/bootstrapping": "rbac-defaults"},
        },
        "rules": [{"verbs": ["*"], "resources": ["*"]}],
    }
    wild = {"metadata": {"name": "wild"}, "rules": [{"verbs": ["*"], "resources": ["pods"]}]}
    tight = {"metadata": {"name": "tight"}, "rules": [{"verbs": ["get"], "resources": ["pods"]}]}
    binding = {
        "metadata": {"name": "ops"},
        "roleRef": {"name": "cluster-admin"},
        "subjects": [{"kind": "User", "name": "alice"}],
    }
    system = {
        "metadata": {"name": "sys", "labels": {"kubernetes.io/bootstrapping": "rbac-defaults"}},
        "roleRef": {"name": "cluster-admin"},
        "subjects": [{"kind": "Group", "name": "system:masters"}],
    }
    results = run(clusterroles=[builtin, wild, tight], clusterrolebindings=[binding, system])
    roles = {r.resource_ref: r.status for r in by(results, "k8s.rbac.wildcard-rules")}
    assert roles == {
        "clusterrole/cluster-admin": CheckStatus.NOT_APPLICABLE,
        "clusterrole/wild": CheckStatus.FAIL,
        "clusterrole/tight": CheckStatus.PASS,
    }
    binds = {r.resource_ref: r.status for r in by(results, "k8s.rbac.cluster-admin-binding")}
    assert binds == {
        "clusterrolebinding/ops": CheckStatus.FAIL,
        "clusterrolebinding/sys": CheckStatus.NOT_APPLICABLE,
    }


def test_missing_document_gives_errors_never_passes() -> None:
    adapter = KubernetesAdapter(PACK)
    results = adapter.normalise({"namespaces": doc("namespaces", [])}, NOW)
    pod_checks = [r for r in results if r.check_id.startswith("k8s.pod.")]
    assert pod_checks and all(r.status is CheckStatus.ERROR for r in pod_checks)
    assert all(r.status is not CheckStatus.PASS for r in results)


def make_result(status: CheckStatus, check: str = "k8s.pod.privileged") -> CheckResult:
    return CheckResult(check, "t", "1", "1", "r", status, Severity.HIGH, NOW, "e")


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        ([CheckStatus.PASS, CheckStatus.PASS], ProposedStatus.PASS),
        ([CheckStatus.FAIL, CheckStatus.FAIL], ProposedStatus.FAIL),
        ([CheckStatus.PASS, CheckStatus.FAIL], ProposedStatus.PARTIAL),
        ([CheckStatus.PASS, CheckStatus.ERROR], ProposedStatus.UNKNOWN),
        ([CheckStatus.FAIL, CheckStatus.ERROR], ProposedStatus.FAIL),
    ],
)
def test_rollup_rules(statuses: list[CheckStatus], expected: ProposedStatus) -> None:
    proposals = rollup([make_result(s) for s in statuses], PACK)
    assert [(p.control_id, p.status) for p in proposals] == [("UC-INF-008", expected)]


def test_rollup_ignores_not_applicable_and_unknown_checks() -> None:
    assert rollup([make_result(CheckStatus.NOT_APPLICABLE)], PACK) == []
    assert rollup([make_result(CheckStatus.FAIL, "other.check")], PACK) == []


def test_evidence_store_is_content_addressed_and_detects_tampering(tmp_path: Path) -> None:
    store = FilesystemEvidenceStore(tmp_path)
    d = RawDocument("pods", b'{"items":[]}', "k8s:x")

    def put() -> Evidence:
        return store.put(
            d, source_type="k8s", collector="t", collector_version="1", collected_at=NOW
        )

    e1, e2 = put(), put()
    assert e1.sha256 == e2.sha256 and store.get(e1.sha256) == d.content
    assert len(list(tmp_path.rglob("*"))) == 2  # one directory + one file: stored once
    next(p for p in tmp_path.rglob("*") if p.is_file()).write_bytes(b"changed")
    with pytest.raises(IntegrityError):
        store.get(e1.sha256)
    with pytest.raises(ValueError):
        store.get("../etc/passwd")


class FakeApi:
    server = "https://k8s.test"

    def __init__(self, allowed: set[tuple[str, str, str]], fail: set[str] | None = None) -> None:
        self.allowed = allowed
        self.fail = fail or set()
        self.listed: list[str] = []

    def can_i(self, verb: str, group: str, resource: str) -> bool:
        return (verb, group, resource) in self.allowed

    def list_items(self, path: str) -> list[dict[str, Any]]:
        self.listed.append(path)
        if path in self.fail:
            raise KubeApiError("GET failed with status 500")
        return [
            {"metadata": {"name": "n1", "namespace": "ns"}},
            {"metadata": {"name": "n2", "namespace": "other"}},
        ]


READ_OK = {("list", g, r) for _, _, g, r in READS}


def test_connector_accepts_a_read_only_credential() -> None:
    report = KubernetesConnector(FakeApi(READ_OK)).validate()
    assert report.ok and not report.missing and not report.excessive


def test_connector_rejects_missing_reads_and_any_write_or_secret_access() -> None:
    assert KubernetesConnector(FakeApi(set())).validate().missing
    for verb, group, resource in FORBIDDEN:
        report = KubernetesConnector(FakeApi(READ_OK | {(verb, group, resource)})).validate()
        assert not report.ok and report.excessive, (verb, resource)


def test_collection_records_partial_failures_and_applies_the_namespace_scope() -> None:
    api = FakeApi(READ_OK, fail={"/api/v1/pods"})
    collection = KubernetesConnector(api).collect(Scope(namespaces=frozenset({"ns"})))
    assert collection.errors and "pods" in collection.errors[0]
    assert "pods" not in {d.name for d in collection.documents}
    nets = next(d for d in collection.documents if d.name == "networkpolicies")
    assert [i["metadata"]["name"] for i in json.loads(nets.content)["items"]] == ["n1"]


def test_client_refuses_plain_http_and_errors_never_contain_the_token() -> None:
    from services.k8s_scanner.client import KubeApi

    with pytest.raises(ValueError):
        KubeApi("http://k8s.test", "tok", "/dev/null")
    api = KubeApi("https://127.0.0.1:1", "super-secret-token", None, timeout=1)
    with pytest.raises(KubeApiError) as info:
        api.list_items("/api/v1/pods")
    assert "super-secret-token" not in str(info.value)
