"""Service-to-service identity (constitution ZT-5, T-121).

A service obtains a short-lived, audience-scoped access token from the identity provider with the
OAuth2 client-credentials grant and sends it as a bearer token on every internal call. Tokens are
cached until shortly before they expire. The client secret comes from a per-service Kubernetes
Secret; it is never logged and never part of an exception message.
"""

import asyncio
import json
import ssl
import time
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable
from typing import Any

from app.core.config import Settings

# Refresh this many seconds before the provider's expiry so a token never expires mid-request.
REFRESH_MARGIN_SECONDS = 30

TokenFetcher = Callable[[dict[str, str]], dict[str, Any]]


class ServiceTokenError(Exception):
    """The identity provider did not issue the requested token."""


class ServiceClient:
    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        ca_file: str | None = None,
        *,
        fetch: TokenFetcher | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not token_url.lower().startswith("https://"):
            raise ValueError("the token URL must use https (constitution ZT-4)")
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._context = ssl.create_default_context(cafile=ca_file)
        self._fetch = fetch or self._post
        self._clock = clock
        self._cache: dict[frozenset[str], tuple[str, float]] = {}
        self._lock = asyncio.Lock()

    @classmethod
    def from_settings(cls, settings: Settings) -> "ServiceClient":
        token_url = settings.oidc_token_url
        client_id = settings.service_client_id
        client_secret = settings.service_client_secret
        if not (token_url and client_id and client_secret):
            raise RuntimeError(
                "service identity is not configured: set AUCOFF_OIDC_TOKEN_URL, "
                "AUCOFF_SERVICE_CLIENT_ID and AUCOFF_SERVICE_CLIENT_SECRET"
            )
        return cls(token_url, client_id, client_secret, settings.oidc_ca_file)

    def _post(self, form: dict[str, str]) -> dict[str, Any]:
        request = urllib.request.Request(  # noqa: S310 - https enforced in __init__
            self._token_url,
            data=urllib.parse.urlencode(form).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(request, timeout=10, context=self._context) as response:  # noqa: S310
            body: dict[str, Any] = json.load(response)
        return body

    async def token(self, scopes: Iterable[str]) -> str:
        wanted = frozenset(scopes)
        async with self._lock:
            cached = self._cache.get(wanted)
            if cached and cached[1] > self._clock():
                return cached[0]
            form = {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": " ".join(sorted(wanted)),
            }
            try:
                body = await asyncio.to_thread(self._fetch, form)
            except Exception as exc:  # never include the request (it holds the secret)
                raise ServiceTokenError(f"token request failed: {type(exc).__name__}") from None
            access_token = body.get("access_token")
            granted = frozenset(str(body.get("scope", "")).split())
            if not access_token or not wanted <= granted:
                raise ServiceTokenError("the identity provider did not grant the requested scopes")
            lifetime = float(body.get("expires_in", 0))
            self._cache[wanted] = (
                str(access_token),
                self._clock() + max(0.0, lifetime - REFRESH_MARGIN_SECONDS),
            )
            return str(access_token)

    async def auth_headers(self, scopes: Iterable[str]) -> dict[str, str]:
        return {"Authorization": f"Bearer {await self.token(scopes)}"}
