"""Service-to-service identity: token acquisition, caching, scope check, secret hygiene (T-121)."""

import pytest

from app.core.config import Settings
from app.core.service_client import ServiceClient, ServiceTokenError

URL = "https://idp.example.test/token"


class Fetcher:
    def __init__(self, responses: list[dict[str, object]]) -> None:
        self.responses = responses
        self.calls: list[dict[str, str]] = []

    def __call__(self, form: dict[str, str]) -> dict[str, object]:
        self.calls.append(form)
        return self.responses.pop(0)


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def make(fetcher: Fetcher, clock: Clock) -> ServiceClient:
    return ServiceClient(URL, "svc-a", "s3cret", fetch=fetcher, clock=clock)


async def test_token_is_cached_until_shortly_before_expiry() -> None:
    clock = Clock()
    fetch = Fetcher(
        [
            {"access_token": "t1", "scope": "ops:read", "expires_in": 300},
            {"access_token": "t2", "scope": "ops:read", "expires_in": 300},
        ]
    )
    client = make(fetch, clock)
    assert await client.token(["ops:read"]) == "t1"
    clock.now += 200
    assert await client.token(["ops:read"]) == "t1"
    assert len(fetch.calls) == 1
    clock.now += 80  # inside the 30 s refresh margin
    assert await client.token(["ops:read"]) == "t2"
    assert len(fetch.calls) == 2


async def test_request_carries_client_credentials_and_scopes() -> None:
    fetch = Fetcher([{"access_token": "t", "scope": "docs:read ops:read", "expires_in": 60}])
    await make(fetch, Clock()).token(["ops:read", "docs:read"])
    assert fetch.calls[0] == {
        "grant_type": "client_credentials",
        "client_id": "svc-a",
        "client_secret": "s3cret",
        "scope": "docs:read ops:read",
    }


async def test_different_scope_sets_are_cached_separately() -> None:
    fetch = Fetcher(
        [
            {"access_token": "a", "scope": "ops:read", "expires_in": 300},
            {"access_token": "b", "scope": "docs:read", "expires_in": 300},
        ]
    )
    client = make(fetch, Clock())
    assert await client.token(["ops:read"]) == "a"
    assert await client.token(["docs:read"]) == "b"


async def test_missing_scope_in_grant_is_refused() -> None:
    fetch = Fetcher([{"access_token": "t", "scope": "", "expires_in": 60}])
    with pytest.raises(ServiceTokenError):
        await make(fetch, Clock()).token(["ops:read"])


async def test_failure_message_never_contains_the_secret() -> None:
    def boom(form: dict[str, str]) -> dict[str, object]:
        raise OSError(f"connection refused while sending {form['client_secret']}")

    client = ServiceClient(URL, "svc-a", "s3cret", fetch=boom, clock=Clock())
    with pytest.raises(ServiceTokenError) as info:
        await client.token(["ops:read"])
    assert "s3cret" not in str(info.value)
    assert info.value.__cause__ is None


async def test_auth_headers_are_bearer() -> None:
    fetch = Fetcher([{"access_token": "abc", "scope": "ops:read", "expires_in": 60}])
    headers = await make(fetch, Clock()).auth_headers(["ops:read"])
    assert headers == {"Authorization": "Bearer abc"}


def test_plain_http_token_url_is_refused() -> None:
    with pytest.raises(ValueError):
        ServiceClient("http://idp/token", "a", "b")


def test_from_settings_fails_closed_when_incomplete() -> None:
    with pytest.raises(RuntimeError):
        ServiceClient.from_settings(Settings(oidc_token_url=URL))
