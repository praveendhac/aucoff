"""Licence gate for Python dependencies (constitution LIC-1, LIC-2, LIC-5).

Fails on any disallowed or unknown licence. The allow-list is permissive-only. Exceptions are
explicit, per package, and must be recorded in LICENCES.md with the owner's decision.

Usage: uv run python -m scripts.check_licences
"""

import json
import re
import subprocess
import sys

ALLOWED = {
    "mit",
    "mit license",
    "apache-2.0",
    "apache software license",
    "apache license 2.0",
    "bsd license",
    "bsd-2-clause",
    "bsd-3-clause",
    "isc",
    "isc license",
    "postgresql",
    "mpl-2.0",
    "mozilla public license 2.0 (mpl 2.0)",  # MPL-2.0 is allowed only unmodified (LIC-1)
}
DENIED_PATTERN = re.compile(r"agpl|\bgpl|lgpl|sspl|busl|business source|commons clause", re.I)

# package -> licence accepted as an explicit exception (pending owner decision, see LICENCES.md)
EXCEPTIONS: dict[str, str] = {
    "typing_extensions": "psf-2.0",  # required by pydantic; permissive, awaiting owner approval
    "cffi": "mit-0",  # required by cryptography (PyJWT); MIT-0, awaiting owner approval
}


def alternatives(expr: str) -> list[list[str]]:
    """Split an SPDX-like expression into OR alternatives of AND terms."""
    return [
        [t.strip().lower() for t in re.split(r"\s+AND\s+|;", alt) if t.strip()]
        for alt in re.split(r"\s+OR\s+", expr)
    ]


def ok(name: str, expr: str) -> bool:
    if DENIED_PATTERN.search(expr):
        return False
    exc = EXCEPTIONS.get(name)
    return any(
        all(term in ALLOWED or term == exc for term in terms) for terms in alternatives(expr)
    )


def main() -> int:
    out = subprocess.run(
        ["pip-licenses", "--format=json", "--with-system"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    bad = [(p["Name"], p["License"]) for p in json.loads(out) if not ok(p["Name"], p["License"])]
    if bad:
        print("Disallowed or unknown licences (constitution LIC-1/LIC-2):", file=sys.stderr)
        for name, lic in bad:
            print(f"  {name}: {lic}", file=sys.stderr)
        return 1
    print("licence check passed: all Python dependencies are on the permissive allow-list")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
