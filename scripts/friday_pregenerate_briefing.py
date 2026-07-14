"""Pre-generate today's spoken morning briefing — schedulable.

Renders the briefing audio ahead of time (local Orpheus DE / Kokoro EN TTS
servers on localhost) and stores it under ``local_data/briefings`` so the
morning alarm can play it instantly via
``GET /api/voice/morning-briefing?prefer_pregenerated=true``.

Old files are pruned automatically (last 7 kept). If
``ENABLE_PUSH_NOTIFICATIONS = True`` and a device is registered, a
'Briefing bereit' push is sent after a successful run.

Schedule (cron example, nightly at 03:00):
    0 3 * * * cd /pfad/zu/friday && python scripts/friday_pregenerate_briefing.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from friday.app.briefing_pregeneration import pregenerate_briefing  # noqa: E402
from friday.app.push_notifications import notify_briefing_ready  # noqa: E402


def main() -> int:
    result = pregenerate_briefing(target_date=date.today())
    if not result.ok:
        print(f"[FAIL] Briefing konnte nicht vorproduziert werden: {result.error}")
        return 1

    print(f"[OK] Briefing vorproduziert: {result.audio_path}")
    push = notify_briefing_ready(result.date)
    if push.external_call_used:
        print(f"[{'OK' if push.ok else 'FAIL'}] {push.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
