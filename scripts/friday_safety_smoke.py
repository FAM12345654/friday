from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from friday.app.safety_smoke_runner import (  # noqa: E402
    format_safety_smoke_result,
    run_safety_smoke,
)


def main() -> int:
    result = run_safety_smoke()
    print(format_safety_smoke_result(result))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
