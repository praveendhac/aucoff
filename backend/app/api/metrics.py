"""Authenticated metrics endpoint (api-contract.md, scope `ops:read`)."""

from fastapi import APIRouter, Depends, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.metrics import REGISTRY
from app.core.security import Principal, require_scope

router = APIRouter(prefix="/metrics", tags=["health"])
ops_read = require_scope("ops:read")


@router.get(
    "",
    operation_id="metricsExposition",
    summary="Request metrics",
    description=(
        "Gateway request metrics in the Prometheus text format. Requires a token with scope "
        "`ops:read`; a monitoring identity uses the client-credentials flow."
    ),
    response_class=Response,
    responses={
        200: {"content": {"text/plain": {"example": "# HELP aucoff_http_requests_total ..."}}}
    },
)
def metrics(_principal: Principal = Depends(ops_read)) -> Response:
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
