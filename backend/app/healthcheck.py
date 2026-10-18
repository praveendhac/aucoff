"""In-container health check for Kubernetes `exec` probes (constitution ZT-7).

Runs in-process checks and exits non-zero on failure. There is intentionally no anonymous HTTP
health endpoint. Dependency checks (database, broker, using this service's own credentials) are
added as those layers are implemented.

Usage: python -m app.healthcheck
"""

import sys

from app.core.config import get_settings


def run() -> list[str]:
    """Return a list of problems; empty means healthy."""
    problems: list[str] = []
    s = get_settings()
    for name in ("oidc_issuer", "oidc_audience", "oidc_jwks_url"):
        if not getattr(s, name):
            problems.append(f"missing configuration: {name}")
    return problems


def main() -> int:
    problems = run()
    for p in problems:
        print(p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
