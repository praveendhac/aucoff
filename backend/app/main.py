"""AUCoFF FastAPI gateway entry point."""

from fastapi import FastAPI

from app.api import health
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="AUCoFF API",
        version=settings.version,
        description=(
            "AgenticAI Unified Compliance Framework for Fintechs. The OpenAPI document is the "
            "source of truth for the API contract (specs/api-contract.md)."
        ),
        contact={"name": "AUCoFF maintainers"},
        servers=[{"url": "http://aucoff.localtest.me", "description": "Local kind cluster (v1)"}],
        openapi_tags=[{"name": "health", "description": "Liveness and readiness probes."}],
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(health.router, prefix="/api/v1")
    return app


app = create_app()
