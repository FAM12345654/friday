"""Send due/overdue task reminders to registered devices — schedulable.

Requires ENABLE_PUSH_NOTIFICATIONS = True in friday/config.py and at least
one device registered via POST /api/push/register.

Schedule (cron example, every morning at 08:00):
    0 8 * * * cd /pfad/zu/friday && python scripts/friday_push_reminders.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from friday.app.push_notifications import (  # noqa: E402
    build_due_task_notifications,
    send_push_notifications,
)
from friday.storage.repositories import TaskRepository  # noqa: E402


def main() -> int:
    tasks = TaskRepository().filter_tasks()
    notifications = build_due_task_notifications(tasks, date.today().isoformat())
    if not notifications:
        print("[OK] Keine fälligen oder überfälligen Aufgaben — nichts zu senden.")
        return 0

    result = send_push_notifications(notifications)
    print(f"[{'OK' if result.ok else 'FAIL'}] {result.message}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
