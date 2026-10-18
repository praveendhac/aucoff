"""Authentication for every endpoint (constitution ZT-1 to ZT-9).

* `TokenVerifier` validates a bearer JWT: signature (RS256/ES256 only), issuer, audience, expiry,
  and the presence of `sub`. Unsigned and HMAC tokens are rejected.
* `AuthMiddleware` is a default-deny ASGI middleware: no request reaches any route (including the
  API documentation and the OpenAPI document) without a valid token.
* `require_scope` is the per-route authorisation dependency; it also puts a security requirement
  into the generated OpenAPI document.
* There is deliberately no switch that turns authentication off (ZT-9). Tests use a test key pair
  through `StaticKeyResolver`.
"""

import ssl
from collections.abc import Awaitable, Callable, MutableMapping
from dataclasses import dataclass, field
from typing import Any, Protocol

import jwt
from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPBearer
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import Settings
from app.core.rbac import effective_scopes

ALLOWED_ALGORITHMS = ["RS256", "ES256"]

# Scope required by the framework-provided routes that FastAPI serves outside our routers.
BUILTIN_PATH_SCOPES: dict[str, str] = {
    "/docs": "docs:read",
    "/docs/oauth2-redirect": "docs:read",
    "/redoc": "docs:read",
    "/api/v1/openapi.json": "docs:read",
}


class AuthenticationError(Exception):
    """The request carries no valid credential (HTTP 401)."""


class AuthorisationError(Exception):
    """The credential is valid but lacks a required scope (HTTP 403)."""


@dataclass(frozen=True)
class Principal:
    subject: str
    scopes: frozenset[str]
    tenant_id: str | None = None
    claims: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)

    def require(self, *needed: str) -> None:
        missing = [s for s in needed if s not in self.scopes]
        if missing:
            raise AuthorisationError(f"missing scope: {', '.join(missing)}")


class KeyResolver(Protocol):
    def signing_key(self, token: str) -> Any: ...


class StaticKeyResolver:
    """Resolves a fixed public key. Used by tests with a test key pair (not a bypass)."""

    def __init__(self, public_key: Any) -> None:
        self._key = public_key

    def signing_key(self, token: str) -> Any:
        return self._key


class JWKSKeyResolver:
    """Resolves signing keys from the identity provider's JWKS endpoint (cached)."""

    def __init__(self, jwks_url: str, ca_file: str | None = None) -> None:
        if not jwks_url.lower().startswith("https://"):
            raise ValueError("the JWKS URL must use https (constitution ZT-4)")
        context = ssl.create_default_context(cafile=ca_file)
        self._client = jwt.PyJWKClient(
            jwks_url, cache_keys=True, lifespan=300, timeout=10, ssl_context=context
        )

    def signing_key(self, token: str) -> Any:
        return self._client.get_signing_key_from_jwt(token).key


class RejectAllResolver:
    """Rejects every token. Used only to build the app for OpenAPI export, never to serve."""

    def signing_key(self, token: str) -> Any:
        raise AuthenticationError("no key available")


class TokenVerifier:
    def __init__(self, resolver: KeyResolver, issuer: str, audience: str) -> None:
        self._resolver = resolver
        self._issuer = issuer
        self._audience = audience

    def verify(self, token: str) -> Principal:
        try:
            key = self._resolver.signing_key(token)
            claims = jwt.decode(
                token,
                key,
                algorithms=ALLOWED_ALGORITHMS,
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            )
        except AuthenticationError:
            raise
        except jwt.PyJWTError as exc:
            raise AuthenticationError("invalid token") from exc
        scope_claim = claims.get("scope", claims.get("scp", ""))
        scopes = frozenset(
            scope_claim.split() if isinstance(scope_claim, str) else list(scope_claim)
        )
        roles = claims.get("roles", [])
        if not isinstance(roles, list):
            roles = []
        return Principal(
            subject=str(claims["sub"]),
            scopes=effective_scopes(scopes, [str(r) for r in roles], claims.get("azp")),
            tenant_id=claims.get("tenant_id"),
            claims=claims,
        )


def verifier_from_settings(settings: Settings) -> TokenVerifier:
    """Build the production verifier; fail closed if the configuration is incomplete."""
    if not (settings.oidc_issuer and settings.oidc_audience and settings.oidc_jwks_url):
        raise RuntimeError(
            "OIDC configuration is incomplete: set AUCOFF_OIDC_ISSUER, AUCOFF_OIDC_AUDIENCE and "
            "AUCOFF_OIDC_JWKS_URL. The service refuses to start without authentication (ZT-9)."
        )
    return TokenVerifier(
        JWKSKeyResolver(settings.oidc_jwks_url, settings.oidc_ca_file),
        settings.oidc_issuer,
        settings.oidc_audience,
    )


def _problem(status: int, title: str) -> JSONResponse:
    headers = {"WWW-Authenticate": 'Bearer realm="aucoff"'} if status == 401 else {}
    return JSONResponse(
        {"type": "about:blank", "title": title, "status": status},
        status_code=status,
        media_type="application/problem+json",
        headers=headers,
    )


class AuthMiddleware:
    """Default-deny: every HTTP request must carry a valid bearer token (ZT-1)."""

    def __init__(self, app: ASGIApp, verifier: TokenVerifier) -> None:
        self.app = app
        self.verifier = verifier

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return
        if scope["type"] == "websocket":
            # No WebSocket endpoints exist; refuse rather than serve unauthenticated.
            await send({"type": "websocket.close", "code": 1008})
            return
        request = Request(scope, receive)
        header = request.headers.get("authorization", "")
        scheme, _, token = header.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            await _problem(401, "Authentication required")(scope, receive, send)
            return
        try:
            principal = self.verifier.verify(token.strip())
        except AuthenticationError:
            await _problem(401, "Invalid or expired token")(scope, receive, send)
            return
        needed = BUILTIN_PATH_SCOPES.get(scope["path"])
        if needed and needed not in principal.scopes:
            await _problem(403, "Insufficient scope")(scope, receive, send)
            return
        state: MutableMapping[str, Any] = scope.setdefault("state", {})
        state["principal"] = principal
        await self.app(scope, receive, send)


_bearer = HTTPBearer(auto_error=False, description="OIDC access token")


def require_scope(*needed: str) -> Callable[..., Awaitable[Principal]]:
    """Route dependency: the caller must hold every scope in `needed` (else 403)."""

    async def dependency(
        request: Request,
        _credentials: Any = Security(_bearer),
    ) -> Principal:
        principal: Principal | None = request.scope.get("state", {}).get("principal")
        if principal is None:  # defence in depth: the middleware always sets it
            raise HTTPException(status_code=401, detail="Authentication required")
        try:
            principal.require(*needed)
        except AuthorisationError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        return principal

    return dependency
