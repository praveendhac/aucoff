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
    # CA bundle used to verify the identity provider's TLS certificate (ZT-4). Unset means the
    # system trust store, which is correct once a public CA issues the certificate.
    oidc_ca_file: str | None = None

    # This service's own identity for outbound service-to-service calls (OAuth2 client
    # credentials, ZT-5). The secret comes from a per-service Kubernetes Secret.
    oidc_token_url: str | None = None
    service_client_id: str | None = None
    service_client_secret: str | None = None

    # Directory holding the owner-authored control catalogue (data/controls in the repository).
    controls_dir: str = "data/controls"

    # Database connection (constitution ZT-6, DB-5): each service uses its OWN role and password,
    # always over TLS with the server certificate verified against the cluster CA.
    db_host: str | None = None
    db_port: int = 5432
    db_name: str = "aucoff"
    db_user: str | None = None
    db_password: str | None = None
    db_ca_file: str | None = None
    db_ssl: bool = True  # only the throwaway test database may turn this off

    # Message broker (constitution ZT-5): TLS only, this service's OWN RabbitMQ user.
    mq_host: str | None = None
    mq_port: int = 5671
    mq_vhost: str = "aucoff"
    mq_user: str | None = None
    mq_password: str | None = None
    mq_ca_file: str | None = None


def get_settings() -> Settings:
    return Settings()
