"""Tests for TaskAgent write and read operations."""

from __future__ import annotations

import pytest

from friday.agents.task_agent import TaskAgent
from friday.config import (
    ENABLE_REAL_CALENDAR,
    ENABLE_REAL_EMAIL,
    ENABLE_REAL_MUSIC,
    ENABLE_REAL_SMS,
    ENABLE_REAL_WEATHER,
    ENABLE_REAL_WHATSAPP,
    REQUIRE_USER_APPROVAL,
    USE_SQLITE_STORAGE,
)
from friday.storage.database import initialize_database


def _build_task_agent(tmp_path):
    db_file = tmp_path / "friday.db"
    initialize_database(db_file)
    return TaskAgent(db_path=db_file)


def test_task_agent_can_create_edit_and_complete_task(tmp_path) -> None:
    """TaskAgent should pass through local task create/edit/done calls."""
    agent = _build_task_agent(tmp_path)
    created = agent.create_task(
        title="Agent Aufgabe",
        category="arbeit",
        due_date="2026-07-05",
        notes="erst",
        priority="high",
    )
    assert created["title"] == "Agent Aufgabe"
    assert created["priority"] == "high"

    updated = agent.edit_task(created["id"], title="Aufgabe geändert")
    assert updated is not None
    assert updated["title"] == "Aufgabe geändert"

    done = agent.mark_task_done(created["id"])
    assert done is not None
    assert done["status"] == "done"
    assert all(task["id"] != created["id"] for task in agent.get_open_tasks())


def test_task_agent_returns_task_for_id(tmp_path) -> None:
    """TaskAgent can load one task by id."""
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Mit ID")

    found = agent.get_task_by_id(created["id"])
    assert found is not None
    assert found["title"] == "Mit ID"


def test_task_agent_rejects_invalid_priority_on_create(tmp_path) -> None:
    """TaskAgent should reject invalid priority values."""
    agent = _build_task_agent(tmp_path)

    with pytest.raises(ValueError, match="Ungültige Priorität"):
        agent.create_task("Ungültig", priority="zu hoch")


def test_task_agent_rejects_invalid_priority_on_edit(tmp_path) -> None:
    """TaskAgent should reject invalid priority in edit flow."""
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Bearbeitbar", priority="normal")

    with pytest.raises(ValueError, match="Ungültige Priorität"):
        agent.edit_task(created["id"], priority="zu hoch")


def test_task_agent_search_tasks(tmp_path) -> None:
    """TaskAgent should search in local tasks."""
    agent = _build_task_agent(tmp_path)
    agent.create_task("Testsuche", notes="Einspruch")
    agent.create_task("Nix", notes="Wichtiges Dokument")

    results = agent.search_tasks("einspruch")
    assert len(results) == 1
    assert results[0]["title"] == "Testsuche"


def test_task_agent_filter_tasks(tmp_path) -> None:
    """TaskAgent should support status and category filtering."""
    agent = _build_task_agent(tmp_path)
    agent.create_task("Filter", category="arbeit", due_date="2026-07-05")
    agent.create_task("Filter2", category="privat", due_date="2026-07-05")

    results = agent.filter_tasks(status="open", category="arbeit", due_date="2026-07-05")
    assert len(results) == 1
    assert results[0]["category"] == "arbeit"


def test_task_agent_get_tasks_for_date_works_with_priority(tmp_path) -> None:
    """TaskAgent should return tasks by date and include priority."""
    agent = _build_task_agent(tmp_path)
    created = agent.create_task(
        title="Dringend",
        due_date="2026-07-05",
        priority="urgent",
    )

    tasks = agent.get_tasks_for_date("2026-07-05")
    assert len(tasks) == 1
    assert tasks[0]["id"] == created["id"]
    assert tasks[0]["priority"] == "urgent"


def test_task_agent_archive_and_delete_task(tmp_path) -> None:
    """TaskAgent should map archive and delete to repository."""
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Archiviert werden")

    archived = agent.archive_task(created["id"])
    assert archived is not None
    assert archived["status"] == "archived"

    assert agent.delete_task(created["id"]) is True
    assert agent.get_task_by_id(created["id"]) is None


def test_task_agent_only_reads_local_when_no_external_services() -> None:
    """Make the local-only safety setup visible in tests."""
    assert USE_SQLITE_STORAGE is True
    assert ENABLE_REAL_EMAIL is False
    assert ENABLE_REAL_WHATSAPP is False
    assert ENABLE_REAL_SMS is False
    assert ENABLE_REAL_CALENDAR is False
    assert ENABLE_REAL_WEATHER is False
    assert ENABLE_REAL_MUSIC is False
    assert REQUIRE_USER_APPROVAL is True
