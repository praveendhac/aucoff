import pytest

from app import healthcheck

ENV = {
    "AUCOFF_OIDC_ISSUER": "https://idp.test/realms/aucoff",
    "AUCOFF_OIDC_AUDIENCE": "aucoff-gateway",
    "AUCOFF_OIDC_JWKS_URL": "https://idp.test/certs",
    "AUCOFF_DB_HOST": "127.0.0.1",
    "AUCOFF_DB_USER": "aucoff_gateway",
    "AUCOFF_DB_PASSWORD": "x",
}


def test_healthcheck_fails_without_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ENV:
        monkeypatch.delenv(var, raising=False)
    assert healthcheck.main() == 1


def test_healthcheck_fails_when_the_database_is_unreachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for var, value in ENV.items():
        monkeypatch.setenv(var, value)
    monkeypatch.setenv("AUCOFF_DB_PORT", "1")  # nothing listens here
    monkeypatch.setenv("AUCOFF_DB_SSL", "false")
    assert healthcheck.main() == 1
