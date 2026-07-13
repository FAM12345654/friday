"""Create a guarded, encrypted Friday backup — schedulable.

Runs the same chain a manual backup uses (safety smoke → preview → guarded
write) and then encrypts the finished backup folder at rest. The plaintext
folder is removed after successful encryption.

The passphrase comes from the FRIDAY_BACKUP_PASSPHRASE environment variable
so the script can run unattended:

    FRIDAY_BACKUP_PASSPHRASE=... python scripts/friday_encrypted_backup.py

Schedule it via cron (Linux/macOS):
    0 3 * * * cd /pfad/zu/friday && FRIDAY_BACKUP_PASSPHRASE=... python scripts/friday_encrypted_backup.py
or via Windows Task Scheduler with the same command line.
"""

from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from friday.app.backup_encryption import encrypt_backup_folder  # noqa: E402
from friday.app.backup_preview import build_backup_preview  # noqa: E402
from friday.app.backup_write_guard import BACKUP_WRITE_APPROVAL_TOKEN  # noqa: E402
from friday.app.backup_writer import write_local_backup  # noqa: E402
from friday.app.safety_smoke_runner import run_safety_smoke  # noqa: E402


def main() -> int:
    passphrase = os.getenv("FRIDAY_BACKUP_PASSPHRASE", "")
    if len(passphrase.strip()) < 8:
        print("[FAIL] FRIDAY_BACKUP_PASSPHRASE fehlt oder ist zu kurz (min. 8 Zeichen).")
        return 1

    smoke = run_safety_smoke()
    if not smoke.passed:
        print("[FAIL] Safety-Smoke fehlgeschlagen — Backup abgebrochen.")
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    preview = build_backup_preview(PROJECT_ROOT, timestamp=timestamp)
    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=PROJECT_ROOT,
    )
    if not result.persisted or result.target_path is None:
        print(f"[FAIL] Backup wurde nicht geschrieben: {result.message}")
        return 1
    print(f"[OK] Backup geschrieben: {result.target_path}")

    encrypted = encrypt_backup_folder(result.target_path, passphrase)
    if not encrypted.ok:
        print(f"[FAIL] Verschlüsselung fehlgeschlagen: {encrypted.message}")
        return 1
    print(f"[OK] {encrypted.message} → {encrypted.target_path}")

    # Remove the plaintext folder now that the encrypted archive exists.
    shutil.rmtree(result.target_path)
    print("[OK] Klartext-Backup entfernt. Nur das verschlüsselte Archiv bleibt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
