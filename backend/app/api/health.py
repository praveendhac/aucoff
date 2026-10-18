"""Authenticated health summary (api-contract.md API-2).

Kubernetes probes do NOT use this endpoint: they run `python -m app.healthcheck` (ZT-7).
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.security import Principal, require_scope

router = APIRouter(prefix="/health", tags=["health"])
ops_read = require_scope("ops:read")


class HealthStatus(BaseModel):
    status: str = Field(description="`ok` when the checks pass.", examples=["ok"])
    service: str = Field(description="Service name.", examples=["aucoff-gateway"])
    version: str = Field(description="Service version.", examples=["0.1.0"])


@router.get(
    "",
    operation_id="healthSummary",
    summary="Health summary",
    description=(
        "Authenticated health summary for operators and monitoring (scope `ops:read`). "
        "Dependency checks (database, queue) are added as those layers are implemented."
    ),
    response_model=HealthStatus,
)
def health(_principal: Principal = Depends(ops_read)) -> HealthStatus:
    s = get_settings()
    return HealthStatus(status="ok", service=s.service_name, version=s.version)
