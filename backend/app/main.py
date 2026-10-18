"""AUCoFF FastAPI gateway entry point.

Run with `uvicorn app.main:create_app --factory`. There is no module-level app object: building
the app requires authentication configuration, and the service refuses to start without it.
"""

from fastapi import FastAPI

from app.api import health
from app.core.config import get_settings
from app.core.security import AuthMiddleware, TokenVerifier, verifier_from_settings


def create_app(verifier: TokenVerifier | None = None) -> FastAPI:
    settings = get_settings()
    verifier = verifier or verifier_from_settings(settings)
    app = FastAPI(
        title="AUCoFF API",
        version=settings.version,
        description=(
            "AgenticAI Unified Compliance Framework for Fintechs. The OpenAPI document is the "
            "source of truth for the API contract (specs/api-contract.md). Every endpoint, "
            "including this documentation, requires a bearer token."
        ),
        contact={"name": "AUCoFF maintainers"},
        servers=[{"url": "http://aucoff.localtest.me", "description": "Local kind cluster (v1)"}],
        openapi_tags=[{"name": "health", "description": "Authenticated health summary."}],
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(health.router, prefix="/api/v1")
    app.add_middleware(AuthMiddleware, verifier=verifier)
    return app
