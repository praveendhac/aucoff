"""CI gate for the unified control catalogue (T-006).

Usage: uv run python -m scripts.check_controls
"""

import sys
from pathlib import Path

from app.domain.controls import validate_directory

ROOT = Path(__file__).resolve().parents[2] / "data" / "controls"


def main() -> int:
    errors = validate_directory(ROOT)
    if errors:
        print("Control catalogue problems:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    count = sum(1 for _ in ROOT.glob("*.yaml"))
    print(f"control catalogue check passed ({count} file(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
