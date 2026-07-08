"""Tests for the local task markdown export service."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from friday.app.task_markdown_export import (
    build_default_tasks_export_path,
    format_tasks_as_markdown,
    export_tasks_markdown_to_default_path,
    write_tasks_markdown,
)


def test_format_tasks_as_markdown_groups_tasks_by_status() -> None:
    tasks = [
        {"id": 3, "title": "Neue Aufgabe", "status": "open", "category": "arbeit", "due_date": "2026-07-06", "priority": "high", "notes": "notiz"},
        {"id": 1, "title": "Erledigt", "status": "done", "category": "privat", "due_date": "2026-07-05", "priority": "low"},
        {"id": 2, "title": "Archiviert", "status": "archived", "category": "arbeit"},
    ]

    markdown_output = format_tasks_as_markdown(tasks)

    assert "# Friday Aufgabenexport" in markdown_output
    assert "## Offene Aufgaben" in markdown_output
    assert "## Erledigte Aufgaben" in markdown_output
    assert "## Archivierte Aufgaben" in markdown_output

    open_section_start = markdown_output.index("## Offene Aufgaben")
    done_section_start = markdown_output.index("## Erledigte Aufgaben")
    archived_section_start = markdown_output.index("## Archivierte Aufgaben")
    assert open_section_start < done_section_start < archived_section_start
    assert "- [ ] Neue Aufgabe" in markdown_output
    assert "  - ID: 3" in markdown_output
    assert "- [x] Erledigt" in markdown_output
    assert "  - ID: 1" in markdown_output
    assert "- [-] Archiviert" in markdown_output
    assert "  - ID: 2" in markdown_output


def test_format_tasks_as_markdown_keeps_contact_snapshot_in_notes() -> None:
    tasks = [
        {
            "id": 11,
            "title": "Kontaktaufgabe",
            "status": "open",
            "notes": "Bitte prüfen.\n\nKontakt-Snapshot:\nQuelle: Chef\nKontaktart: kollege",
        }
    ]

    markdown_output = format_tasks_as_markdown(tasks)

    assert "Kontakt-Snapshot:" in markdown_output
    assert "Quelle: Chef" in markdown_output
    assert "Kontaktart: kollege" in markdown_output


def test_format_tasks_as_markdown_includes_recurrence_when_present() -> None:
    tasks = [
        {
            "id": 12,
            "title": "Wiederkehrende Aufgabe",
            "status": "open",
            "recurrence": "woechentlich",
        }
    ]

    markdown_output = format_tasks_as_markdown(tasks)

    assert "- [ ] Wiederkehrende Aufgabe" in markdown_output
    assert "  - Wiederholung: woechentlich" in markdown_output


def test_format_tasks_as_markdown_uses_defaults_for_missing_fields() -> None:
    tasks = [{"id": 10, "title": "Minimale Aufgabe"}]
    markdown_output = format_tasks_as_markdown(tasks)

    assert "## Offene Aufgaben" in markdown_output
    assert "- [ ] Minimale Aufgabe" in markdown_output
    assert "  - ID: 10" in markdown_output
    assert "  - Kategorie: sonstiges" in markdown_output
    assert "  - Fällig: kein Datum" in markdown_output
    assert "  - Priorität: normal" in markdown_output


def test_format_tasks_as_markdown_handles_empty_list() -> None:
    markdown_output = format_tasks_as_markdown([])
    assert "## Offene Aufgaben" in markdown_output
    assert "## Erledigte Aufgaben" in markdown_output
    assert "## Archivierte Aufgaben" in markdown_output
    assert markdown_output.count("_Keine Aufgaben._") == 3


def test_write_tasks_markdown_writes_file_to_tmp_path(tmp_path: Path) -> None:
    tasks = [
        {"id": 5, "title": "Export Aufgabe", "status": "open"},
        {"id": 6, "title": "Erledigt Aufgabe", "status": "done"},
    ]
    output_file = tmp_path / "exports" / "friday_tasks.md"

    returned_path = write_tasks_markdown(output_file, tasks)

    assert returned_path == output_file
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "Export Aufgabe" in content
    assert "Erledigt Aufgabe" in content


def test_build_default_tasks_export_path_uses_local_exports_directory(tmp_path: Path) -> None:
    fixed_time = datetime(2026, 7, 6, 12, 30, 45)
    path = build_default_tasks_export_path(tmp_path, fixed_time)

    assert path == tmp_path / "local_data" / "exports" / "friday_tasks_20260706_123045.md"
    assert "exports" in path.parts
    assert path.suffix == ".md"


def test_write_tasks_markdown_can_use_default_export_path(tmp_path: Path) -> None:
    tasks = [{"id": 7, "title": "Geplanter Export", "status": "open"}]
    fixed_time = datetime(2026, 7, 6, 12, 30, 45)
    output_file = build_default_tasks_export_path(tmp_path, fixed_time)

    returned_path = write_tasks_markdown(output_file, tasks)

    assert returned_path == output_file
    assert output_file.exists()
    assert output_file.parent == tmp_path / "local_data" / "exports"
    content = output_file.read_text(encoding="utf-8")
    assert "# Friday Aufgabenexport" in content
    assert "Geplanter Export" in content


def test_default_export_path_uses_timestamp_name() -> None:
    first = build_default_tasks_export_path(
        Path("."),
        datetime(2026, 7, 6, 12, 30, 45),
    )
    second = build_default_tasks_export_path(
        Path("."),
        datetime(2026, 7, 6, 12, 30, 46),
    )

    assert first != second


def test_export_tasks_markdown_to_default_path_writes_under_local_exports(tmp_path: Path) -> None:
    tasks = [{"id": 8, "title": "Wrapper Aufgabe", "status": "open"}]
    fixed_time = datetime(2026, 7, 6, 12, 30, 45)
    output_path = export_tasks_markdown_to_default_path(
        base_dir=tmp_path,
        tasks=tasks,
        timestamp=fixed_time,
    )

    assert output_path.exists()
    assert output_path == tmp_path / "local_data" / "exports" / "friday_tasks_20260706_123045.md"
    assert output_path.parent == tmp_path / "local_data" / "exports"

    content = output_path.read_text(encoding="utf-8")
    assert "# Friday Aufgabenexport" in content
    assert "Wrapper Aufgabe" in content


def test_export_tasks_markdown_to_default_path_handles_empty_tasks(tmp_path: Path) -> None:
    output_path = export_tasks_markdown_to_default_path(base_dir=tmp_path, tasks=[], timestamp=None)
    content = output_path.read_text(encoding="utf-8")

    assert output_path.exists()
    assert output_path.parent == tmp_path / "local_data" / "exports"
    assert "## Offene Aufgaben" in content
    assert "_Keine Aufgaben._" in content
    assert "## Erledigte Aufgaben" in content
    assert "## Archivierte Aufgaben" in content


def test_export_tasks_markdown_to_default_path_uses_distinct_timestamps(tmp_path: Path) -> None:
    first = export_tasks_markdown_to_default_path(
        base_dir=tmp_path,
        tasks=[],
        timestamp=datetime(2026, 7, 6, 12, 30, 45),
    )
    second = export_tasks_markdown_to_default_path(
        base_dir=tmp_path,
        tasks=[],
        timestamp=datetime(2026, 7, 6, 12, 30, 46),
    )

    assert first != second
    assert first.parent == tmp_path / "local_data" / "exports"
    assert second.parent == tmp_path / "local_data" / "exports"
    assert first.exists()
    assert second.exists()
