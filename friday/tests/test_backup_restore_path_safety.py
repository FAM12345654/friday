"""Tests for shared Backup/Restore forbidden-path checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from friday.app.backup_restore_path_safety import is_forbidden_backup_restore_path


@pytest.mark.parametrize(
    "relative_path",
    (
        ".env",
        ".env.local",
        "secrets/token.txt",
        "tokens.json",
        "api_keys.json",
        "credentials.yml",
        "private_key.pem",
        "passwords.txt",
        "Obsidian Vault/note.md",
        "obsidian_vault/note.md",
        "ObsidianVault/note.md",
        ".obsidian/workspace.json",
    ),
)
def test_forbidden_backup_restore_path_blocks_sensitive_names(
    tmp_path,
    relative_path: str,
) -> None:
    candidate = tmp_path / "root" / relative_path
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text("test\n", encoding="utf-8")

    assert is_forbidden_backup_restore_path(candidate, root=tmp_path / "root") is True


def test_forbidden_backup_restore_path_does_not_block_harmless_tokenizer_name(
    tmp_path,
) -> None:
    root = tmp_path / "root"
    candidate = root / "exports" / "tokenizer_notes.md"
    candidate.parent.mkdir(parents=True)
    candidate.write_text("notes\n", encoding="utf-8")

    assert is_forbidden_backup_restore_path(candidate, root=root) is False


def test_forbidden_backup_restore_path_blocks_path_outside_root(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside\n", encoding="utf-8")

    assert is_forbidden_backup_restore_path(outside, root=root) is True


def test_forbidden_backup_restore_path_blocks_symlink_escape(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "allowed.md").write_text("outside\n", encoding="utf-8")
    link = root / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    assert is_forbidden_backup_restore_path(link / "allowed.md", root=root) is True
