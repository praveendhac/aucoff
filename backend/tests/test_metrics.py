"""The metrics endpoint is authenticated and counts requests by route template."""

from collections.abc import Callable

from fastapi.testclient import TestClient


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_metrics_refuse_anonymous_and_wrong_scope(
    client: TestClient, make_token: Callable[..., str]
) -> None:
    assert client.get("/api/v1/metrics").status_code == 401
    assert (
        client.get("/api/v1/metrics", headers=_bearer(make_token("docs:read"))).status_code == 403
    )


def test_metrics_expose_counts_for_authenticated_monitoring(
    client: TestClient, make_token: Callable[..., str]
) -> None:
    client.get("/api/v1/health")  # refused before routing: counted as "unmatched", never by path
    client.get("/api/v1/health", headers=_bearer(make_token("ops:read")))
    response = client.get("/api/v1/metrics", headers=_bearer(make_token("ops:read")))
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    body = response.text
    assert "aucoff_http_requests_total" in body
    assert 'route="/health"' in body and 'status="200"' in body
    assert 'route="unmatched"' in body and 'status="401"' in body
    assert "/api/v1/health" not in body  # raw paths never become labels
