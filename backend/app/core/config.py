"""Environment-driven configuration (12-factor, ARC-8). No secrets have defaults."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUCOFF_", extra="ignore")

    environment: str = "local"
    service_name: str = "aucoff-gateway"
    version: str = "0.1.0"

    # OIDC token validation (constitution ZT-3). All three are required to start the service;
    # there is no default and no way to disable authentication (ZT-9).
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    oidc_jwks_url: str | None = None


def get_settings() -> Settings:
    return Settings()
