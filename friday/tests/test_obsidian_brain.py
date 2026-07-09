"""Tests for the local Obsidian Brain preview model."""

from __future__ import annotations

from friday import config
from friday.app.obsidian_brain import build_obsidian_brain_preview
from friday.app.obsidian_brain import build_obsidian_brain_finalization_gate
from friday.app.obsidian_note_preview import (
    OBSIDIAN_WRITE_TOKEN,
    build_obsidian_write_dry_run,
    write_obsidian_note_with_approval,
)


def test_obsidian_brain_preview_groups_local_notes() -> None:
    preview = build_obsidian_brain_preview(
        tasks=[
            {
                "id": 1,
                "title": "Rechnung prüfen",
                "status": "open",
                "priority": "high",
            }
        ],
        contacts=[
            {
                "display_name": "Max Mustermann",
                "contact_type": "kunde",
                "source_context": "test",
                "user_approved_persistence": 1,
                "sensitivity_checked": 1,
            }
        ],
        projects=[{"title": "Lokales Projekt", "status": "preview"}],
    )

    assert preview.preview_only is True
    assert preview.persisted is False
    assert preview.external_lookup_used is False
    assert len(preview.task_previews) == 1
    assert len(preview.contact_previews) == 1
    assert len(preview.project_previews) == 1
    assert len(preview.all_previews()) == 3


def test_obsidian_brain_dry_run_does_not_write_when_disabled(tmp_path) -> None:
    preview = build_obsidian_brain_preview(
        tasks=[{"id": 1, "title": "Nur Dry Run", "status": "open"}],
    )

    dry_run = build_obsidian_write_dry_run(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=preview.task_previews[0],
        write_enabled=False,
    )

    assert dry_run.preview_only is True
    assert dry_run.persisted is False
    assert dry_run.would_write is False
    assert dry_run.reason == "Obsidian Write ist deaktiviert."
    assert dry_run.target_path.exists() is False


def test_obsidian_brain_write_requires_enabled_flag_and_hard_token(tmp_path) -> None:
    preview = build_obsidian_brain_preview(
        tasks=[{"id": 1, "title": "Token Aufgabe", "status": "open"}],
    )

    disabled = write_obsidian_note_with_approval(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=preview.task_previews[0],
        confirmation=OBSIDIAN_WRITE_TOKEN,
        write_enabled=False,
    )
    wrong_token = write_obsidian_note_with_approval(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=preview.task_previews[0],
        confirmation="JA",
        write_enabled=True,
    )

    assert disabled.persisted is False
    assert disabled.reason == "Obsidian Write ist deaktiviert."
    assert wrong_token.persisted is False
    assert wrong_token.reason == "Obsidian Write wurde abgebrochen."


def test_obsidian_brain_finalization_gate_is_read_only_and_guarded() -> None:
    gate = build_obsidian_brain_finalization_gate()

    assert gate.status == "finalized_preview_ready_write_disabled"
    assert gate.preview_only is True
    assert gate.persisted is False
    assert gate.external_lookup_used is False
    assert gate.vault_path_configured is False
    assert gate.write_enabled is False
    assert gate.allowed_subdir == "Friday"
    assert gate.approval_token_required == OBSIDIAN_WRITE_TOKEN
    assert "hard_token_required_for_write" in gate.completed_checks
    assert "automatic_obsidian_write" in gate.blocked_actions
    assert "cloud_sync_or_provider_call" in gate.blocked_actions


def test_obsidian_brain_finalization_preserves_required_safety_flags() -> None:
    assert config.ENABLE_REAL_EMAIL is False
    assert config.ENABLE_REAL_WHATSAPP is False
    assert config.ENABLE_REAL_SMS is False
    assert config.ENABLE_REAL_CALENDAR is True
    assert config.ENABLE_REAL_WEATHER is False
    assert config.ENABLE_REAL_MUSIC is False
    assert config.REQUIRE_USER_APPROVAL is True
    assert config.USE_SQLITE_STORAGE is True
