"""Posture dashboard: scope enforcement and the synthetic-data label (API-70)."""

from collections.abc import Callable

from fastapi.testclient import TestClient


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_requires_report_read(client: TestClient, make_token: Callable[..., str]) -> None:
    assert client.get("/api/v1/dashboards/posture").status_code == 401
    wrong = client.get("/api/v1/dashboards/posture", headers=_bearer(make_token("ops:read")))
    assert wrong.status_code == 403


def test_dashboard_is_labelled_synthetic(
    client: TestClient, make_token: Callable[..., str]
) -> None:
    response = client.get("/api/v1/dashboards/posture", headers=_bearer(make_token("report:read")))
    assert response.status_code == 200
    body = response.json()
    assert body["data_source"] == "synthetic"
    assert set(body["kpis"]) == {
        "posture_score",
        "coverage_pct",
        "open_findings",
        "pending_approvals",
        "evidence_freshness_pct",
    }
    assert {"pass", "partial", "fail", "unknown", "not_applicable"} == set(
        body["status_distribution"]
    )
    assert [s["severity"] for s in body["severity_comparison"]] == [
        "critical",
        "high",
        "medium",
        "low",
    ]
    assert len(body["frameworks"]) == 4


def test_executive_role_may_read_but_engineer_may_not(
    client: TestClient, make_token: Callable[..., str]
) -> None:
    def call(role: str) -> int:
        token = make_token("report:read", extra={"azp": "aucoff-web", "roles": [role]})
        return int(client.get("/api/v1/dashboards/posture", headers=_bearer(token)).status_code)

    assert call("executive") == 200
    assert call("auditor") == 200
    assert call("engineer") == 403
