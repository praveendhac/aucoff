"""Test identity provider: an RSA key pair, token minting and an app wired to the test key.

This is not an authentication bypass (ZT-9): the application still validates real signed tokens;
tests simply sign them with a key the test verifier trusts.
"""

import time
from collections.abc import Callable
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.security import StaticKeyResolver, TokenVerifier
from app.main import create_app

ISSUER = "https://idp.test/realms/aucoff"
AUDIENCE = "aucoff-gateway"


@pytest.fixture(scope="session")
def private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="session")
def other_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="session")
def make_token(private_key: rsa.RSAPrivateKey) -> Callable[..., str]:
    def _make(
        scopes: str = "",
        *,
        key: rsa.RSAPrivateKey | None = None,
        issuer: str = ISSUER,
        audience: str = AUDIENCE,
        expires_in: int = 300,
        algorithm: str = "RS256",
        extra: dict[str, Any] | None = None,
    ) -> str:
        now = int(time.time())
        claims: dict[str, Any] = {
            "sub": "user-1",
            "iss": issuer,
            "aud": audience,
            "iat": now,
            "exp": now + expires_in,
            "scope": scopes,
            "tenant_id": "tenant-a",
        }
        claims.update(extra or {})
        return jwt.encode(claims, key or private_key, algorithm=algorithm, headers={"kid": "t"})

    return _make


@pytest.fixture(scope="session")
def app(private_key: rsa.RSAPrivateKey) -> FastAPI:
    verifier = TokenVerifier(StaticKeyResolver(private_key.public_key()), ISSUER, AUDIENCE)
    return create_app(verifier)


@pytest.fixture(scope="session")
def client(app: FastAPI) -> TestClient:
    return TestClient(app)
