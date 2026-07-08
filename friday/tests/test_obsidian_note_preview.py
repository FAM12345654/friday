"""Tests for local Obsidian note previews and guarded writes."""

from __future__ import annotations

import pytest

from friday.app.obsidian_note_preview import (
    OBSIDIAN_WRITE_TOKEN,
    build_contact_note_preview,
    build_obsidian_target_path,
    build_obsidian_write_dry_run,
    build_project_note_preview,
    build_task_note_preview,
    safe_obsidian_filename,
    write_obsidian_note_with_approval,
)


def test_safe_obsidian_filename_normalizes_value() -> None:
    assert safe_obsidian_filename("Müller & Söhne!") == "mueller-soehne.md"


def test_build_contact_note_preview_contains_allowed_fields() -> None:
    preview = build_contact_note_preview(
        {
            "display_name": "Max Mustermann",
            "contact_type": "kunde",
            "source_context": "nachrichten_review",
            "relationship_context": "Projekt Alpha",
            "user_approved_persistence": 1,
            "sensitivity_checked": 1,
        }
    )

    assert preview.preview_only is True
    assert preview.persisted is False
    assert preview.relative_path == "Kontakte/max-mustermann.md"
    assert "type: contact" in preview.markdown
    assert "# Max Mustermann" in preview.markdown
    assert "Kontaktart: kunde" in preview.markdown
    assert "Beziehungskontext: Projekt Alpha" in preview.markdown


def test_contact_note_preview_omits_unapproved_relationship_context() -> None:
    preview = build_contact_note_preview(
        {
            "display_name": "Max Mustermann",
            "contact_type": "kunde",
            "relationship_context": "Nur mit Freigabe",
            "user_approved_persistence": 0,
            "sensitivity_checked": 1,
        }
    )

    assert "Nur mit Freigabe" not in preview.markdown


def test_build_task_note_preview_keeps_contact_snapshot_in_notes() -> None:
    preview = build_task_note_preview(
        {
            "title": "Report prüfen",
            "status": "open",
            "notes": "Kontakt-Snapshot:\nQuelle: Chef\nKontaktart: kollege",
        }
    )

    assert preview.relative_path == "Aufgaben/report-pruefen.md"
    assert "type: task" in preview.markdown
    assert "Kontakt-Snapshot:" in preview.markdown
    assert "Quelle: Chef" in preview.markdown


def test_build_project_note_preview() -> None:
    preview = build_project_note_preview({"title": "Projekt Freitag", "status": "aktiv"})

    assert preview.relative_path == "Projekte/projekt-freitag.md"
    assert "type: project" in preview.markdown
    assert "Status: aktiv" in preview.markdown


def test_obsidian_target_path_stays_inside_allowed_subdir(tmp_path) -> None:
    preview = build_task_note_preview({"title": "../Unsicher"})
    target = build_obsidian_target_path(tmp_path, "Friday", preview)

    assert target.parent.name == "Aufgaben"
    assert "Friday" in target.parts
    assert target.suffix == ".md"


def test_obsidian_target_path_rejects_escaping_allowed_subdir(tmp_path) -> None:
    preview = build_task_note_preview({"title": "Probe"})

    with pytest.raises(ValueError):
        build_obsidian_target_path(tmp_path, "..\\outside", preview)

    with pytest.raises(ValueError):
        build_obsidian_target_path(tmp_path, str(tmp_path.parent), preview)


def test_obsidian_dry_run_does_not_write_when_disabled(tmp_path) -> None:
    preview = build_task_note_preview({"title": "Nur Preview"})
    dry_run = build_obsidian_write_dry_run(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=preview,
        write_enabled=False,
    )

    assert dry_run.would_write is False
    assert dry_run.persisted is False
    assert dry_run.target_path.exists() is False


def test_obsidian_write_rejects_wrong_token(tmp_path) -> None:
    preview = build_task_note_preview({"title": "Nicht schreiben"})
    result = write_obsidian_note_with_approval(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=preview,
        confirmation="JA",
        write_enabled=True,
    )

    assert result.persisted is False
    assert result.target_path.exists() is False
    assert result.reason == "Obsidian Write wurde abgebrochen."


def test_obsidian_write_accepts_hard_token(tmp_path) -> None:
    preview = build_task_note_preview({"title": "Schreiben erlaubt"})
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


def test_obsidian_write_does_not_overwrite_existing_file(tmp_path) -> None:
    preview = build_task_note_preview({"title": "Einmalig"})
    first = write_obsidian_note_with_approval(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=preview,
        confirmation=OBSIDIAN_WRITE_TOKEN,
        write_enabled=True,
    )
    second = write_obsidian_note_with_approval(
        vault_path=tmp_path,
        allowed_subdir="Friday",
        preview=preview,
        confirmation=OBSIDIAN_WRITE_TOKEN,
        write_enabled=True,
    )

    assert first.persisted is True
    assert second.persisted is False
    assert second.reason == "Zieldatei existiert bereits."
