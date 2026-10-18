"""List endpoints: scopes, pagination, filters, labelling (API-22, API-37, API-47)."""

from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from tests.test_controls import GOOD


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    ("path", "scope"),
    [
        ("/api/v1/unified-controls", "catalog:read"),
        ("/api/v1/findings", "finding:write"),
        ("/api/v1/evidence", "evidence:read"),
    ],
)
def test_scopes_are_enforced(
    client: TestClient, make_token: Callable[..., str], path: str, scope: str
) -> None:
    assert client.get(path).status_code == 401
    assert client.get(path, headers=_bearer(make_token("ops:read"))).status_code == 403
    assert client.get(path, headers=_bearer(make_token(scope))).status_code == 200


def test_findings_are_labelled_synthetic_and_paginate(
    client: TestClient, make_token: Callable[..., str]
) -> None:
    h = _bearer(make_token("finding:write"))
    first = client.get("/api/v1/findings?limit=15", headers=h).json()
    assert first["data_source"] == "synthetic"
    assert len(first["items"]) == 15 and first["next_cursor"]
    seen = {f["id"] for f in first["items"]}
    cursor = first["next_cursor"]
    while cursor:
        page = client.get(f"/api/v1/findings?limit=15&cursor={cursor}", headers=h).json()
        assert not seen & {f["id"] for f in page["items"]}
        seen |= {f["id"] for f in page["items"]}
        cursor = page["next_cursor"]
    assert len(seen) == 40


def test_findings_filters(client: TestClient, make_token: Callable[..., str]) -> None:
    h = _bearer(make_token("finding:write"))
    body = client.get("/api/v1/findings?severity=critical&status=open&limit=100", headers=h).json()
    assert body["items"]
    assert all(f["severity"] == "critical" and f["status"] == "open" for f in body["items"])


def test_evidence_filter_and_bad_input(client: TestClient, make_token: Callable[..., str]) -> None:
    h = _bearer(make_token("evidence:read"))
    items = client.get("/api/v1/evidence?source=aws&limit=100", headers=h).json()["items"]
    assert items and all(e["source"] == "aws" for e in items)
    assert client.get("/api/v1/evidence?cursor=%%%", headers=h).status_code == 400
    assert client.get("/api/v1/evidence?limit=0", headers=h).status_code == 422
    assert client.get("/api/v1/evidence?limit=101", headers=h).status_code == 422
    assert client.get("/api/v1/evidence?source=bogus", headers=h).status_code == 422


def test_controls_come_from_the_real_catalogue(
    client: TestClient,
    make_token: Callable[..., str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = _bearer(make_token("catalog:read"))
    (tmp_path / "iam.yaml").write_text(GOOD, encoding="utf-8")
    monkeypatch.setattr("app.api.lists.get_settings", lambda: Settings(controls_dir=str(tmp_path)))
    body = client.get("/api/v1/unified-controls", headers=h).json()
    assert body["data_source"] == "catalogue"
    assert [c["id"] for c in body["items"]] == ["UC-IAM-001"]
    assert client.get("/api/v1/unified-controls?framework=pci-dss-4.0.1", headers=h).json()["items"]
    assert not client.get(
        "/api/v1/unified-controls?framework=soc2-2017&domain=x", headers=h
    ).json()["items"]


def test_an_empty_or_invalid_catalogue(
    client: TestClient,
    make_token: Callable[..., str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = _bearer(make_token("catalog:read"))
    monkeypatch.setattr("app.api.lists.get_settings", lambda: Settings(controls_dir=str(tmp_path)))
    assert client.get("/api/v1/unified-controls", headers=h).json()["items"] == []
    (tmp_path / "bad.yaml").write_text("catalogue_version: x\ncontrols: []\n", encoding="utf-8")
    assert client.get("/api/v1/unified-controls", headers=h).status_code == 503
