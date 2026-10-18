"""Request metrics in the Prometheus text format (constitution ZT-1, ZT-7).

The metrics are exposed only through the authenticated `GET /api/v1/metrics` (scope `ops:read`);
there is no anonymous `/metrics` endpoint. Labels are the route template, never the raw path, so
identifiers cannot leak into metric names and cardinality stays bounded.
"""

import time

from prometheus_client import CollectorRegistry, Counter, Histogram
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REGISTRY = CollectorRegistry()
REQUESTS = Counter(
    "aucoff_http_requests_total",
    "HTTP requests handled by the gateway.",
    ["method", "route", "status"],
    registry=REGISTRY,
)
LATENCY = Histogram(
    "aucoff_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route"],
    registry=REGISTRY,
)


class MetricsMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        status = 500

        async def capture(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, capture)
        finally:
            route = getattr(scope.get("route"), "path", None) or "unmatched"
            method = scope["method"]
            REQUESTS.labels(method, route, str(status)).inc()
            LATENCY.labels(method, route).observe(time.perf_counter() - started)
