"""Authentication coverage tests (constitution ZT-1, ZT-3, ZT-8, ZT-9)."""

import re
from collections.abc import Callable

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from starlette.routing import Route

from app.core.config import Settings
from app.core.security import verifier_from_settings
from tests.conftest import AUDIENCE, ISSUER

TokenFactory = Callable[..., str]


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_every_route_rejects_requests_without_a_token(app: FastAPI, client: TestClient) -> None:
    """ZT-8: enumerate every route (framework table) and assert 401 without credentials."""
    checked = 0
    for route in app.routes:
        if isinstance(route, (APIRoute, Route)):
            path = re.sub(r"\{[^}]+\}", "x", route.path)
            for method in route.methods or {"GET"}:
                response = client.request(method, path)
                assert response.status_code == 401, f"{method} {path} is not protected"
                assert response.headers["www-authenticate"].startswith("Bearer")
                checked += 1
    assert checked >= 4  # health, openapi, docs, redoc at minimum


def test_unknown_paths_also_require_authentication(client: TestClient) -> None:
    assert client.get("/does-not-exist").status_code == 401
    assert client.get("/api/v1/health/live").status_code == 401  # old anonymous probe is gone


def test_every_openapi_operation_declares_security(
    client: TestClient, make_token: TokenFactory
) -> None:
    token = make_token("docs:read")
    spec = client.get("/api/v1/openapi.json", headers=_bearer(token)).json()
    for path, operations in spec["paths"].items():
        for method, op in operations.items():
            assert op.get("security"), f"{method} {path} has no security requirement"
            assert op.get("operationId") and op.get("summary") and op.get("description")


def test_docs_require_docs_scope(client: TestClient, make_token: TokenFactory) -> None:
    for path in ("/docs", "/redoc", "/api/v1/openapi.json"):
        assert client.get(path, headers=_bearer(make_token("ops:read"))).status_code == 403
        assert client.get(path, headers=_bearer(make_token("docs:read"))).status_code == 200


def test_health_requires_ops_scope(client: TestClient, make_token: TokenFactory) -> None:
    assert client.get("/api/v1/health", headers=_bearer(make_token(""))).status_code == 403
    ok = client.get("/api/v1/health", headers=_bearer(make_token("ops:read")))
    assert ok.status_code == 200
    assert ok.json()["status"] == "ok"


def test_rejects_malformed_authorization_headers(client: TestClient) -> None:
    for header in ("", "Bearer", "Bearer ", "Basic abc", "Token abc", "bearer"):
        r = client.get("/api/v1/health", headers={"Authorization": header})
        assert r.status_code == 401, header


def test_rejects_bad_tokens(
    client: TestClient,
    make_token: TokenFactory,
    other_private_key: rsa.RSAPrivateKey,
) -> None:
    cases = {
        "wrong signing key": make_token("ops:read", key=other_private_key),
        "expired": make_token("ops:read", expires_in=-10),
        "wrong issuer": make_token("ops:read", issuer="https://evil.test"),
        "wrong audience": make_token("ops:read", audience="other-service"),
        "garbage": "not.a.jwt",
    }
    for name, token in cases.items():
        r = client.get("/api/v1/health", headers=_bearer(token))
        assert r.status_code == 401, name


def test_rejects_unsigned_and_hmac_tokens(client: TestClient) -> None:
    now = 4_000_000_000
    claims = {"sub": "u", "iss": ISSUER, "aud": AUDIENCE, "iat": 1, "exp": now, "scope": "ops:read"}
    unsigned = jwt.encode(claims, "", algorithm="none")
    hmac_token = jwt.encode(claims, "secret" * 8, algorithm="HS256")
    for token in (unsigned, hmac_token):
        assert client.get("/api/v1/health", headers=_bearer(token)).status_code == 401


def test_rejects_tokens_missing_required_claims(
    client: TestClient, private_key: rsa.RSAPrivateKey
) -> None:
    claims = {"iss": ISSUER, "aud": AUDIENCE, "scope": "ops:read"}  # no sub, exp, iat
    token = jwt.encode(claims, private_key, algorithm="RS256")
    assert client.get("/api/v1/health", headers=_bearer(token)).status_code == 401


def test_service_refuses_to_start_without_oidc_configuration() -> None:
    """ZT-9: there is no way to run unauthenticated; incomplete config fails closed."""
    with pytest.raises(RuntimeError, match="OIDC configuration is incomplete"):
        verifier_from_settings(Settings(oidc_issuer=None, oidc_audience=None, oidc_jwks_url=None))
    with pytest.raises(RuntimeError):
        verifier_from_settings(Settings(oidc_issuer=ISSUER, oidc_audience=AUDIENCE))


def test_no_authentication_bypass_setting_exists() -> None:
    fields = {name.lower() for name in Settings.model_fields}
    assert not {f for f in fields if re.search(r"(auth|security).*(disable|bypass|off|skip)", f)}
    assert not {f for f in fields if re.search(r"(disable|bypass|skip).*(auth|security)", f)}


def test_user_token_scopes_are_limited_by_the_users_roles(
    client: TestClient, make_token: TokenFactory
) -> None:
    """A web-client token has ops:read, but only an admin role may use it."""
    as_exec = make_token("ops:read", extra={"azp": "aucoff-web", "roles": ["executive"]})
    as_admin = make_token("ops:read", extra={"azp": "aucoff-web", "roles": ["admin"]})
    as_service = make_token("ops:read", extra={"azp": "svc-gateway"})
    assert client.get("/api/v1/health", headers=_bearer(as_exec)).status_code == 403
    assert client.get("/api/v1/health", headers=_bearer(as_admin)).status_code == 200
    assert client.get("/api/v1/health", headers=_bearer(as_service)).status_code == 200
