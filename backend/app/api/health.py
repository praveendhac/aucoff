"""Liveness and readiness probes (api-contract.md, API-2). No authentication."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(BaseModel):
    status: str = Field(description="`ok` when the check passes.", examples=["ok"])
    service: str = Field(description="Service name.", examples=["aucoff-gateway"])
    version: str = Field(description="Service version.", examples=["0.1.0"])


@router.get(
    "/live",
    operation_id="healthLive",
    summary="Liveness probe",
    description="Returns 200 while the process is running. Used by Kubernetes liveness probes.",
    response_model=HealthStatus,
)
def live() -> HealthStatus:
    from app.core.config import get_settings

    s = get_settings()
    return HealthStatus(status="ok", service=s.service_name, version=s.version)


@router.get(
    "/ready",
    operation_id="healthReady",
    summary="Readiness probe",
    description=(
        "Returns 200 when the service can accept traffic. Dependency checks (database, "
        "queue) are added as those layers are implemented."
    ),
    response_model=HealthStatus,
)
def ready() -> HealthStatus:
    from app.core.config import get_settings

    s = get_settings()
    return HealthStatus(status="ok", service=s.service_name, version=s.version)
