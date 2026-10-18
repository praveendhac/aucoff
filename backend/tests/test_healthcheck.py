import pytest

from app import healthcheck


def test_healthcheck_fails_without_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("AUCOFF_OIDC_ISSUER", "AUCOFF_OIDC_AUDIENCE", "AUCOFF_OIDC_JWKS_URL"):
        monkeypatch.delenv(var, raising=False)
    assert healthcheck.main() == 1


def test_healthcheck_passes_with_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUCOFF_OIDC_ISSUER", "https://idp.test/realms/aucoff")
    monkeypatch.setenv("AUCOFF_OIDC_AUDIENCE", "aucoff-gateway")
    monkeypatch.setenv("AUCOFF_OIDC_JWKS_URL", "https://idp.test/certs")
    assert healthcheck.main() == 0
