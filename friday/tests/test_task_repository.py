"""Tests for writable task repository operations."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from friday.storage.database import initialize_database
from friday.storage.repositories import TaskRepository, calculate_next_recurrence_due_date


def _build_task_repo(tmp_path):
    db_file = tmp_path / "friday.db"
    initialize_database(db_file)
    return TaskRepository(db_file)


def test_create_task_and_defaults(tmp_path) -> None:
    """Create must require a title and apply safe defaults."""
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Neue Aufgabe")

    assert created["id"] > 0
    assert created["title"] == "Neue Aufgabe"
    assert created["category"] == "other"
    assert created["status"] == "open"
    assert created["notes"] == ""
    assert created["priority"] == "normal"
    assert created["recurrence"] is None


def test_create_task_rejects_empty_title(tmp_path) -> None:
    """Empty task title must not be accepted."""
    repo = _build_task_repo(tmp_path)
    with pytest.raises(ValueError):
        repo.create_task("   ")


def test_create_task_rejects_invalid_priority(tmp_path) -> None:
    """Invalid priorities must raise a German error."""
    repo = _build_task_repo(tmp_path)
    with pytest.raises(ValueError, match="Ungültige Priorität"):
        repo.create_task("Ungültig", priority="zu hoch")


def test_create_task_accepts_recurrence(tmp_path) -> None:
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Wiederkehrend", recurrence="woechentlich")

    assert created["recurrence"] == "woechentlich"


def test_create_task_rejects_invalid_recurrence(tmp_path) -> None:
    repo = _build_task_repo(tmp_path)

    with pytest.raises(ValueError, match="Ungültige Wiederholung"):
        repo.create_task("Ungültig", recurrence="immer")


def test_create_task_defaults_priority_to_normal(tmp_path) -> None:
    """Create should store normal when no priority is passed."""
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Standard")
    assert created["priority"] == "normal"


def test_create_task_none_priority_defaults_to_normal(tmp_path) -> None:
    """Explicit None priority should still result in normal for created tasks."""
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Standard None", priority=None)
    assert created["priority"] == "normal"


def test_get_task_by_id_returns_task(tmp_path) -> None:
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Zum Suchen")
    found = repo.get_task_by_id(created["id"])

    assert found is not None
    assert found["id"] == created["id"]
    assert found["title"] == "Zum Suchen"


def test_get_open_tasks_excludes_done_and_archived(tmp_path) -> None:
    """Open list must not include done or archived tasks."""
    repo = _build_task_repo(tmp_path)
    open_task = repo.create_task("Offen")
    repo.create_task("Erledigt", status="done")
    archived = repo.create_task("Archiviert", status="archived")

    open_tasks = repo.get_open_tasks()
    open_titles = {task["title"] for task in open_tasks}
    assert open_task["title"] in open_titles
    assert "Erledigt" not in open_titles
    assert archived["title"] not in open_titles


def test_get_open_tasks_sorted_by_due_date_priority_and_id(tmp_path) -> None:
    """Open tasks should be sorted by due date, priority (desc), then id."""
    repo = _build_task_repo(tmp_path)
    repo.create_task("Heute low", due_date="2026-07-06", priority="low")
    repo.create_task("Heute urgent", due_date="2026-07-06", priority="urgent")
    repo.create_task("Morgen normal", due_date="2026-07-05", priority="normal")
    repo.create_task("Heute normal", due_date="2026-07-06", priority="normal")
    repo.create_task("Heute ohne priorität", due_date="2026-07-06")
    repo.create_task("Ohne Datum", priority="high")

    open_tasks = repo.get_open_tasks()
    titles = [task["title"] for task in open_tasks]
    assert titles == [
        "Morgen normal",
        "Heute urgent",
        "Heute normal",
        "Heute ohne priorität",
        "Heute low",
        "Ohne Datum",
    ]


def test_get_tasks_for_date_returns_tasks_without_sql_error(tmp_path) -> None:
    """Querying tasks by date should work and include stored priority."""
    repo = _build_task_repo(tmp_path)
    repo.create_task("Heute wichtig", due_date="2026-07-05", priority="high")
    repo.create_task("Morgen wichtig", due_date="2026-07-06", priority="urgent")

    tasks = repo.get_tasks_for_date("2026-07-05")
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Heute wichtig"
    assert tasks[0]["priority"] == "high"


def test_get_tasks_for_date_excludes_done_and_archived(tmp_path) -> None:
    """Date-based open-task lookup must not return done or archived tasks."""
    repo = _build_task_repo(tmp_path)
    open_task = repo.create_task("Offen", due_date="2026-07-05", priority="low")
    repo.create_task("Erledigt", due_date="2026-07-05", status="done", priority="urgent")
    repo.create_task("Archiviert", due_date="2026-07-05", status="archived", priority="high")

    tasks = repo.get_tasks_for_date("2026-07-05")
    titles = [task["title"] for task in tasks]
    assert len(tasks) == 1
    assert open_task["title"] in titles
    assert "Erledigt" not in titles
    assert "Archiviert" not in titles


def test_get_tasks_for_date_sorts_by_priority(tmp_path) -> None:
    """Date-based open-task lookup should sort high urgency first."""
    repo = _build_task_repo(tmp_path)
    repo.create_task("Niedrig", due_date="2026-07-05", priority="low")
    repo.create_task("Urgent", due_date="2026-07-05", priority="urgent")
    repo.create_task("Normal", due_date="2026-07-05", priority="normal")
    repo.create_task("Hoch", due_date="2026-07-05", priority="high")

    tasks = repo.get_tasks_for_date("2026-07-05")
    titles = [task["title"] for task in tasks]
    assert titles == ["Urgent", "Hoch", "Normal", "Niedrig"]


def test_update_task_changes_only_provided_fields(tmp_path) -> None:
    """Only given fields should be changed."""
    repo = _build_task_repo(tmp_path)
    created = repo.create_task(
        "Start",
        category="arbeit",
        due_date="2026-07-05",
        notes="Erstnotiz",
    )

    updated = repo.update_task(created["id"], title="Neu", notes="Neue Notiz")

    assert updated is not None
    assert updated["title"] == "Neu"
    assert updated["notes"] == "Neue Notiz"
    assert updated["category"] == "arbeit"
    assert updated["due_date"] == "2026-07-05"


def test_update_task_rejects_invalid_priority(tmp_path) -> None:
    """Updating to an invalid priority should be rejected."""
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Original", priority="normal")

    with pytest.raises(ValueError, match="Ungültige Priorität"):
        repo.update_task(created["id"], priority="zu hoch")


def test_update_task_rejects_empty_title(tmp_path) -> None:
    """Blank task titles are not allowed during updates."""
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Original")

    with pytest.raises(ValueError, match="Eine Aufgabe braucht einen Titel."):
        repo.update_task(created["id"], title="   ")

    unchanged = repo.get_task_by_id(created["id"])
    assert unchanged is not None
    assert unchanged["title"] == "Original"


def test_search_tasks_finds_title_and_notes(tmp_path) -> None:
    """Search should find matches in title or notes."""
    repo = _build_task_repo(tmp_path)
    repo.create_task("Einkaufen", notes="Butter und Brot")
    repo.create_task("Meeting", notes="Bitte Unterlagen vorbereiten")

    results = repo.search_tasks("bro")
    assert len(results) == 1
    assert results[0]["title"] == "Einkaufen"

    results_by_note = repo.search_tasks("unterlagen")
    assert len(results_by_note) == 1
    assert results_by_note[0]["title"] == "Meeting"


def test_search_tasks_empty_query_returns_none(tmp_path) -> None:
    """Empty query must not run a broad search."""
    repo = _build_task_repo(tmp_path)
    repo.create_task("Einkaufen", notes="Butter")

    assert repo.search_tasks("   ") == []


def test_search_tasks_can_filter_by_status_and_category(tmp_path) -> None:
    """Search query can combine status and category filters."""
    repo = _build_task_repo(tmp_path)
    repo.create_task("Test-Auftrag", category="arbeit")
    repo.create_task("Test-Auftrag", category="arbeit", status="done")
    repo.create_task("Kein Treffer", category="privat")

    results = repo.search_tasks("test", status="done", category="arbeit")
    assert len(results) == 1
    assert results[0]["status"] == "done"
    assert results[0]["category"] == "arbeit"


def test_filter_tasks_by_status_category_and_due_date(tmp_path) -> None:
    """Filter should handle optional filters."""
    repo = _build_task_repo(tmp_path)
    repo.create_task("Auftrag", category="arbeit", due_date="2026-07-05")
    repo.create_task("Privat", category="privat", due_date="2026-07-05")
    repo.create_task("Auftrag2", category="arbeit", due_date="2026-07-06")

    results = repo.filter_tasks(status="open", category="arbeit", due_date="2026-07-05")
    assert len(results) == 1
    assert results[0]["title"] == "Auftrag"


def test_archive_task_sets_archived_status(tmp_path) -> None:
    """Archive should set task status to archived."""
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Archivieren")

    archived = repo.archive_task(created["id"])
    assert archived is not None
    assert archived["status"] == "archived"
    assert all(task["title"] != "Archivieren" for task in repo.get_open_tasks())


def test_archive_unknown_id_returns_none(tmp_path) -> None:
    """Unknown id should return None for archive."""
    repo = _build_task_repo(tmp_path)
    assert repo.archive_task(99) is None


def test_delete_task_removes_task(tmp_path) -> None:
    """Delete must remove task row from local db."""
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Löschen")

    assert repo.delete_task(created["id"]) is True
    assert repo.get_task_by_id(created["id"]) is None


def test_delete_unknown_id_returns_false(tmp_path) -> None:
    """Unknown id should return False."""
    repo = _build_task_repo(tmp_path)
    assert repo.delete_task(99) is False


def test_mark_task_done_updates_status_and_closes_task(tmp_path) -> None:
    """Done tasks should no longer appear in open list."""
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Abhaken", category="arbeit")

    done = repo.mark_task_done(created["id"])
    assert done is not None
    assert done["status"] == "done"

    open_tasks = repo.get_open_tasks()
    assert all(task["id"] != created["id"] for task in open_tasks)


def test_mark_recurring_task_done_creates_next_daily_instance(tmp_path) -> None:
    repo = _build_task_repo(tmp_path)
    created = repo.create_task(
        "Täglich",
        due_date="2026-07-05",
        priority="high",
        recurrence="taeglich",
    )

    repo.mark_task_done(created["id"])
    open_tasks = repo.get_open_tasks()

    assert len(open_tasks) == 1
    assert open_tasks[0]["title"] == "Täglich"
    assert open_tasks[0]["due_date"] == "2026-07-06"
    assert open_tasks[0]["priority"] == "high"
    assert open_tasks[0]["recurrence"] == "taeglich"


def test_mark_already_done_recurring_task_does_not_duplicate_next_instance(tmp_path) -> None:
    repo = _build_task_repo(tmp_path)
    created = repo.create_task(
        "Täglich stabil",
        due_date="2026-07-05",
        priority="high",
        recurrence="taeglich",
    )

    repo.mark_task_done(created["id"])
    repo.mark_task_done(created["id"])
    open_tasks = repo.get_open_tasks()

    assert len(open_tasks) == 1
    assert open_tasks[0]["title"] == "Täglich stabil"
    assert open_tasks[0]["due_date"] == "2026-07-06"


def test_concurrent_done_calls_create_only_one_recurring_instance(tmp_path) -> None:
    repo = _build_task_repo(tmp_path)
    created = repo.create_task(
        "Parallel stabil",
        due_date="2026-07-05",
        priority="high",
        recurrence="taeglich",
    )
    callers = 8
    start = Barrier(callers)

    def mark_done() -> dict | None:
        start.wait()
        return repo.mark_task_done(created["id"])

    with ThreadPoolExecutor(max_workers=callers) as executor:
        results = list(executor.map(lambda _index: mark_done(), range(callers)))

    assert all(result is not None and result["status"] == "done" for result in results)
    open_tasks = repo.get_open_tasks()
    assert len(open_tasks) == 1
    assert open_tasks[0]["title"] == "Parallel stabil"
    assert open_tasks[0]["due_date"] == "2026-07-06"


def test_archive_recurring_task_does_not_create_next_instance(tmp_path) -> None:
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Archiv", due_date="2026-07-05", recurrence="woechentlich")

    repo.archive_task(created["id"])

    assert repo.get_open_tasks() == []


def test_delete_recurring_task_does_not_create_next_instance(tmp_path) -> None:
    repo = _build_task_repo(tmp_path)
    created = repo.create_task("Löschen", due_date="2026-07-05", recurrence="monatlich")

    repo.delete_task(created["id"])

    assert repo.get_open_tasks() == []


def test_calculate_next_recurrence_due_date_clamps_month_end() -> None:
    assert calculate_next_recurrence_due_date("2026-01-31", "monatlich") == "2026-02-28"


def test_calculate_next_recurrence_due_date_keeps_leap_day() -> None:
    assert calculate_next_recurrence_due_date("2024-01-31", "monatlich") == "2024-02-29"


def test_unknown_task_id_returns_none(tmp_path) -> None:
    """Unknown ids should return None for all single-item write methods."""
    repo = _build_task_repo(tmp_path)

    assert repo.get_task_by_id(999) is None
    assert repo.update_task(999, title="nichts") is None
    assert repo.mark_task_done(999) is None
