from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_live() -> None:
    r = client.get("/api/v1/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready() -> None:
    r = client.get("/api/v1/health/ready")
    assert r.status_code == 200
    assert r.json()["service"] == "aucoff-gateway"


def test_openapi_is_served_and_documents_health() -> None:
    r = client.get("/api/v1/openapi.json")
    assert r.status_code == 200
    paths = r.json()["paths"]
    assert "/api/v1/health/live" in paths
    # APIR-1: every operation has an operationId, summary and description
    for path, ops in paths.items():
        for method, op in ops.items():
            assert op.get("operationId"), f"{method} {path} missing operationId"
            assert op.get("summary"), f"{method} {path} missing summary"
            assert op.get("description"), f"{method} {path} missing description"
