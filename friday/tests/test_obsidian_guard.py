"""Tests for the Obsidian sensitive-content write guard."""

from __future__ import annotations

from friday.app.obsidian_guard import (
    OBSIDIAN_GUARD_BLOCKED_MESSAGE,
    check_obsidian_note_for_write,
)
from friday.app.obsidian_note_preview import (
    OBSIDIAN_WRITE_TOKEN,
    build_obsidian_write_dry_run,
    build_task_note_preview,
    write_obsidian_note_with_approval,
)


def test_obsidian_guard_allows_harmless_note() -> None:
    result = check_obsidian_note_for_write(body="Projekt Alpha")

    assert result.allowed is True
    assert result.blocked_fields == ()


def test_obsidian_guard_blocks_sensitive_note_body() -> None:
    result = check_obsidian_note_for_write(body="medizinische Diagnose")

    assert result.allowed is False
    assert "body" in result.blocked_fields
    assert "health" in result.blocked_categories
    assert result.message == OBSIDIAN_GUARD_BLOCKED_MESSAGE


def test_obsidian_guard_blocks_relationship_context() -> None:
    result = check_obsidian_note_for_write(relationship_context="Parteimitglied")

    assert result.allowed is False
    assert "relationship_context" in result.blocked_fields
    assert "politics" in result.blocked_categories


def test_obsidian_guard_has_safe_flags() -> None:
    result = check_obsidian_note_for_write(body="Projekt Alpha")

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_obsidian_write_blocks_sensitive_note_even_with_token(tmp_path) -> None:
    preview = build_task_note_preview(
        {"title": "Sensible Notiz", "notes": "medizinische Diagnose"}
    )

    result = write_obsidian_note_with_approval(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=preview,
        confirmation=OBSIDIAN_WRITE_TOKEN,
        write_enabled=True,
    )

    assert result.persisted is False
    assert result.reason == OBSIDIAN_GUARD_BLOCKED_MESSAGE
    assert result.target_path.exists() is False


def test_obsidian_write_allows_harmless_note_with_all_gates(tmp_path) -> None:
    preview = build_task_note_preview(
        {"title": "Harmlose Notiz", "notes": "Projekt Alpha"}
    )

    result = write_obsidian_note_with_approval(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=preview,
        confirmation=OBSIDIAN_WRITE_TOKEN,
        write_enabled=True,
    )

    assert result.persisted is True
    assert result.target_path.exists()
    assert result.target_path.read_text(encoding="utf-8") == preview.markdown


def test_obsidian_write_does_not_modify_existing_file_when_guard_blocks(tmp_path) -> None:
    harmless_preview = build_task_note_preview(
        {"title": "Bestehende Notiz", "notes": "Projekt Alpha"}
    )
    sensitive_preview = build_task_note_preview(
        {"title": "Bestehende Notiz", "notes": "medizinische Diagnose"}
    )
    first = write_obsidian_note_with_approval(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=harmless_preview,
        confirmation=OBSIDIAN_WRITE_TOKEN,
        write_enabled=True,
    )
    original_content = first.target_path.read_text(encoding="utf-8")

    blocked = write_obsidian_note_with_approval(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=sensitive_preview,
        confirmation=OBSIDIAN_WRITE_TOKEN,
        write_enabled=True,
    )

    assert blocked.persisted is False
    assert blocked.reason == OBSIDIAN_GUARD_BLOCKED_MESSAGE
    assert first.target_path.read_text(encoding="utf-8") == original_content


def test_obsidian_dry_run_does_not_write(tmp_path) -> None:
    preview = build_task_note_preview({"title": "Nur Dry Run", "notes": "Projekt Alpha"})

    dry_run = build_obsidian_write_dry_run(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=preview,
        write_enabled=True,
    )

    assert dry_run.would_write is True
    assert dry_run.persisted is False
    assert dry_run.target_path.exists() is False
