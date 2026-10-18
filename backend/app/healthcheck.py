"""In-container health check for Kubernetes `exec` probes (constitution ZT-7).

Runs in-process checks and exits non-zero on failure. There is intentionally no anonymous HTTP
health endpoint. It verifies the authentication configuration and that this service can
authenticate to the database with its own credential over TLS (ZT-6).

Usage: python -m app.healthcheck
"""

import asyncio
import sys

from app.core.config import get_settings
from app.db.session import create_engine, ping


async def _database_problem() -> str | None:
    engine = create_engine(get_settings())
    try:
        return None if await asyncio.wait_for(ping(engine), timeout=4) else "database ping failed"
    except Exception as exc:  # any failure to connect/authenticate means not ready
        return f"database check failed: {type(exc).__name__}"
    finally:
        await engine.dispose()


def run() -> list[str]:
    """Return a list of problems; empty means healthy."""
    problems: list[str] = []
    s = get_settings()
    for name in ("oidc_issuer", "oidc_audience", "oidc_jwks_url"):
        if not getattr(s, name):
            problems.append(f"missing configuration: {name}")
    for name in ("db_host", "db_user", "db_password"):
        if not getattr(s, name):
            problems.append(f"missing configuration: {name}")
    if not problems:
        db_problem = asyncio.run(_database_problem())
        if db_problem:
            problems.append(db_problem)
    return problems


def main() -> int:
    problems = run()
    for p in problems:
        print(p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
