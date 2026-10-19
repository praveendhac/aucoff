"""Minimal read-only Kubernetes API client (standard library only).

Only GET requests for listing objects, plus one POST that is not a change: a
SelfSubjectAccessReview, which asks the API server what the caller may do. The bearer token is held
in memory, sent only to the configured server over TLS verified against the given CA, and never
appears in exceptions or logs.
"""

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Protocol


class KubeApiError(Exception):
    """The API call failed. The message never contains the credential."""


class KubeApiLike(Protocol):
    server: str

    def list_items(self, path: str) -> list[dict[str, Any]]: ...
    def can_i(self, verb: str, group: str, resource: str) -> bool: ...


class KubeApi:
    def __init__(
        self, server: str, token: str, ca_file: str | None, *, timeout: float = 20.0
    ) -> None:
        if not server.lower().startswith("https://"):
            raise ValueError("the Kubernetes API server URL must use https (constitution ZT-4)")
        self.server = server.rstrip("/")
        self._token = token
        self._context = ssl.create_default_context(cafile=ca_file)
        self._timeout = timeout

    def _request(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(  # noqa: S310 - https enforced in __init__
            self.server + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout, context=self._context) as r:  # noqa: S310
                result: dict[str, Any] = json.load(r)
                return result
        except urllib.error.HTTPError as exc:
            raise KubeApiError(f"{method} {path} failed with status {exc.code}") from None
        except (urllib.error.URLError, OSError, ValueError) as exc:
            raise KubeApiError(f"{method} {path} failed: {type(exc).__name__}") from None

    def list_items(self, path: str) -> list[dict[str, Any]]:
        """All items of a list endpoint, following the API server's continue tokens."""
        items: list[dict[str, Any]] = []
        token = ""
        while True:
            query = {"limit": "500"}
            if token:
                query["continue"] = token
            page = self._request("GET", f"{path}?{urllib.parse.urlencode(query)}")
            items.extend(page.get("items", []))
            token = page.get("metadata", {}).get("continue", "")
            if not token:
                return items

    def can_i(self, verb: str, group: str, resource: str) -> bool:
        review = self._request(
            "POST",
            "/apis/authorization.k8s.io/v1/selfsubjectaccessreviews",
            {
                "apiVersion": "authorization.k8s.io/v1",
                "kind": "SelfSubjectAccessReview",
                "spec": {
                    "resourceAttributes": {"verb": verb, "group": group, "resource": resource}
                },
            },
        )
        return bool(review.get("status", {}).get("allowed", False))
