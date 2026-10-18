"""Environment-driven configuration (12-factor, ARC-8). No secrets have defaults."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUCOFF_", extra="ignore")

    environment: str = "local"
    service_name: str = "aucoff-gateway"
    version: str = "0.1.0"


def get_settings() -> Settings:
    return Settings()
