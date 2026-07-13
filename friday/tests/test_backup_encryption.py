"""Tests for encrypted backup archives."""

from __future__ import annotations

import io
import os
import tarfile

from friday.app.backup_encryption import (
    ENCRYPTED_SUFFIX,
    FORMAT_VERSION,
    MAGIC,
    SALT_LENGTH,
    decrypt_backup_archive,
    derive_backup_key,
    encrypt_backup_folder,
)
from cryptography.fernet import Fernet

PASSPHRASE = "sehr-geheime-passphrase"


def _make_backup(tmp_path):
    backup = tmp_path / "backup_2026_07_13"
    (backup / "exports").mkdir(parents=True)
    (backup / "friday.sqlite").write_text("db-inhalt", encoding="utf-8")
    (backup / "exports" / "tasks.md").write_text("# Aufgaben\n", encoding="utf-8")
    return backup


def test_roundtrip_encrypt_decrypt(tmp_path) -> None:
    backup = _make_backup(tmp_path)

    encrypted = encrypt_backup_folder(backup, PASSPHRASE)
    assert encrypted.ok, encrypted.message
    assert encrypted.file_count == 2
    assert encrypted.target_path.endswith(ENCRYPTED_SUFFIX)

    restored_dir = tmp_path / "restored"
    decrypted = decrypt_backup_archive(encrypted.target_path, PASSPHRASE, restored_dir)
    assert decrypted.ok, decrypted.message
    assert (restored_dir / "friday.sqlite").read_text(encoding="utf-8") == "db-inhalt"
    assert (restored_dir / "exports" / "tasks.md").read_text(encoding="utf-8") == "# Aufgaben\n"


def test_archive_is_actually_encrypted(tmp_path) -> None:
    backup = _make_backup(tmp_path)
    result = encrypt_backup_folder(backup, PASSPHRASE)
    raw = open(result.target_path, "rb").read()
    assert raw.startswith(MAGIC)
    assert b"db-inhalt" not in raw
    assert b"Aufgaben" not in raw


def test_wrong_passphrase_fails_cleanly(tmp_path) -> None:
    backup = _make_backup(tmp_path)
    encrypted = encrypt_backup_folder(backup, PASSPHRASE)

    result = decrypt_backup_archive(
        encrypted.target_path, "falsche-passphrase", tmp_path / "out"
    )
    assert not result.ok
    assert "fehlgeschlagen" in result.message
    assert not (tmp_path / "out").exists()


def test_short_passphrase_rejected(tmp_path) -> None:
    backup = _make_backup(tmp_path)
    result = encrypt_backup_folder(backup, "kurz")
    assert not result.ok


def test_no_overwrite_of_existing_target(tmp_path) -> None:
    backup = _make_backup(tmp_path)
    first = encrypt_backup_folder(backup, PASSPHRASE)
    assert first.ok
    second = encrypt_backup_folder(backup, PASSPHRASE)
    assert not second.ok
    assert "existiert bereits" in second.message


def test_decrypt_refuses_existing_target_dir(tmp_path) -> None:
    backup = _make_backup(tmp_path)
    encrypted = encrypt_backup_folder(backup, PASSPHRASE)
    existing = tmp_path / "already-there"
    existing.mkdir()
    result = decrypt_backup_archive(encrypted.target_path, PASSPHRASE, existing)
    assert not result.ok


def test_garbage_file_rejected(tmp_path) -> None:
    bogus = tmp_path / "bogus.enc"
    bogus.write_bytes(b"nicht-friday")
    result = decrypt_backup_archive(bogus, PASSPHRASE, tmp_path / "out")
    assert not result.ok
    assert "gültige" in result.message


def test_path_traversal_member_rejected(tmp_path) -> None:
    """A crafted archive with ../ members must not extract anything."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        payload = b"boese"
        info = tarfile.TarInfo(name="../escape.txt")
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))

    salt = os.urandom(SALT_LENGTH)
    token = Fernet(derive_backup_key(PASSPHRASE, salt)).encrypt(buffer.getvalue())
    crafted = tmp_path / f"crafted{ENCRYPTED_SUFFIX}"
    crafted.write_bytes(MAGIC + bytes([FORMAT_VERSION]) + salt + token)

    target = tmp_path / "out"
    result = decrypt_backup_archive(crafted, PASSPHRASE, target)
    assert not result.ok
    assert "unsicheren Pfad" in result.message
    assert not target.exists()
    assert not (tmp_path / "escape.txt").exists()
