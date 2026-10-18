"""Export the generated OpenAPI document to backend/openapi.yaml.

Usage: uv run python -m scripts.export_openapi [--check]
With --check, exits non-zero if the committed file differs (CI drift check, APIR-2).
"""

import sys
from pathlib import Path

import yaml

from app.main import create_app

TARGET = Path(__file__).resolve().parent.parent / "openapi.yaml"


def render() -> str:
    spec = create_app().openapi()
    return yaml.safe_dump(spec, sort_keys=True, allow_unicode=True)


def main() -> int:
    rendered = render()
    if "--check" in sys.argv:
        current = TARGET.read_text() if TARGET.exists() else ""
        if current != rendered:
            print("openapi.yaml is out of date; run `make openapi`", file=sys.stderr)
            return 1
        print("openapi.yaml is up to date")
        return 0
    TARGET.write_text(rendered)
    print(f"wrote {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
