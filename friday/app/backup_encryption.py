"""Encrypt finished local backups at rest.

Builds on the guarded backup writer: after ``write_local_backup`` has created
a backup folder, ``encrypt_backup_folder`` packs it into a tar archive and
encrypts it with a passphrase-derived key (PBKDF2-SHA256 → Fernet/AES128-CBC
+ HMAC). ``decrypt_backup_archive`` restores the folder with the same
path-safety rules the restore guards use: no absolute members, no ``..``,
no links, and never overwriting an existing target.

File format: ``FRIDAYBK`` magic + 1 version byte + 16 salt bytes + Fernet
token. Nothing leaves the machine.
"""

from __future__ import annotations

import base64
import io
import os
import tarfile
from dataclasses import dataclass
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b"FRIDAYBK"
FORMAT_VERSION = 1
SALT_LENGTH = 16
PBKDF2_ITERATIONS = 600_000
ENCRYPTED_SUFFIX = ".friday-backup.enc"
MIN_PASSPHRASE_LENGTH = 8


@dataclass(frozen=True)
class BackupEncryptionResult:
    """Outcome of one encrypt/decrypt operation."""

    ok: bool
    target_path: str | None
    file_count: int
    message: str


def derive_backup_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a Fernet key from a passphrase (PBKDF2-SHA256)."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))


def _validate_passphrase(passphrase: str) -> str | None:
    if not isinstance(passphrase, str) or len(passphrase.strip()) < MIN_PASSPHRASE_LENGTH:
        return f"Passphrase muss mindestens {MIN_PASSPHRASE_LENGTH} Zeichen haben."
    return None


def _member_is_safe(member: tarfile.TarInfo) -> bool:
    name = member.name.replace("\\", "/")
    if name.startswith("/") or name.startswith("//"):
        return False
    if any(part == ".." for part in name.split("/")):
        return False
    # Only regular files and directories; no links or devices.
    return member.isreg() or member.isdir()


def encrypt_backup_folder(
    backup_root: str | Path,
    passphrase: str,
    target_file: str | Path | None = None,
) -> BackupEncryptionResult:
    """Pack one finished backup folder into an encrypted archive file."""
    error = _validate_passphrase(passphrase)
    if error:
        return BackupEncryptionResult(False, None, 0, error)

    source = Path(backup_root)
    if not source.exists() or not source.is_dir():
        return BackupEncryptionResult(False, None, 0, "Backup-Ordner wurde nicht gefunden.")

    target = (
        Path(target_file)
        if target_file is not None
        else source.parent / f"{source.name}{ENCRYPTED_SUFFIX}"
    )
    if target.exists():
        return BackupEncryptionResult(
            False, str(target), 0, "Zieldatei existiert bereits. Es wird nichts überschrieben."
        )

    buffer = io.BytesIO()
    file_count = 0
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source)
            if path.is_symlink():
                continue
            if path.is_file():
                archive.add(path, arcname=str(relative))
                file_count += 1
            elif path.is_dir():
                archive.add(path, arcname=str(relative), recursive=False)

    salt = os.urandom(SALT_LENGTH)
    token = Fernet(derive_backup_key(passphrase, salt)).encrypt(buffer.getvalue())

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as handle:
        handle.write(MAGIC)
        handle.write(bytes([FORMAT_VERSION]))
        handle.write(salt)
        handle.write(token)

    return BackupEncryptionResult(
        True,
        str(target),
        file_count,
        f"Backup verschlüsselt: {file_count} Datei(en).",
    )


def decrypt_backup_archive(
    archive_file: str | Path,
    passphrase: str,
    target_dir: str | Path,
) -> BackupEncryptionResult:
    """Restore an encrypted backup archive into a new folder."""
    error = _validate_passphrase(passphrase)
    if error:
        return BackupEncryptionResult(False, None, 0, error)

    source = Path(archive_file)
    if not source.exists() or not source.is_file():
        return BackupEncryptionResult(False, None, 0, "Archivdatei wurde nicht gefunden.")

    target = Path(target_dir)
    if target.exists():
        return BackupEncryptionResult(
            False, str(target), 0, "Zielordner existiert bereits. Es wird nichts überschrieben."
        )

    raw = source.read_bytes()
    header_length = len(MAGIC) + 1 + SALT_LENGTH
    if len(raw) <= header_length or not raw.startswith(MAGIC):
        return BackupEncryptionResult(False, None, 0, "Keine gültige Friday-Backup-Datei.")
    version = raw[len(MAGIC)]
    if version != FORMAT_VERSION:
        return BackupEncryptionResult(False, None, 0, f"Unbekannte Formatversion {version}.")
    salt = raw[len(MAGIC) + 1 : header_length]
    token = raw[header_length:]

    try:
        payload = Fernet(derive_backup_key(passphrase, salt)).decrypt(token)
    except InvalidToken:
        return BackupEncryptionResult(
            False, None, 0, "Entschlüsselung fehlgeschlagen: falsche Passphrase oder Datei beschädigt."
        )

    file_count = 0
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            if not _member_is_safe(member):
                return BackupEncryptionResult(
                    False, None, 0, f"Archiv enthält unsicheren Pfad: {member.name}"
                )
        target.mkdir(parents=True, exist_ok=False)
        for member in members:
            archive.extract(member, path=target, set_attrs=False, filter="data")
            if member.isreg():
                file_count += 1

    return BackupEncryptionResult(
        True,
        str(target),
        file_count,
        f"Backup entschlüsselt: {file_count} Datei(en).",
    )
