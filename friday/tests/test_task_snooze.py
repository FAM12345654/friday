"""Tests for task snoozing (hide until a future date)."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from friday.storage.database import initialize_database
from friday.storage.repositories import TaskRepository


def _build_repo(tmp_path) -> TaskRepository:
    db_file = tmp_path / "friday.db"
    initialize_database(db_file)
    return TaskRepository(db_file)


def _tomorrow() -> str:
    return (date.today() + timedelta(days=1)).isoformat()


def _yesterday() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def test_snooze_hides_task_from_open_list(tmp_path) -> None:
    repo = _build_repo(tmp_path)
    task = repo.create_task("Später erledigen")

    snoozed = repo.snooze_task(task["id"], _tomorrow())
    assert snoozed is not None
    assert snoozed["snoozed_until"] == _tomorrow()

    assert repo.get_open_tasks() == []
    all_tasks = repo.get_open_tasks(include_snoozed=True)
    assert [item["id"] for item in all_tasks] == [task["id"]]


def test_snooze_hides_task_from_day_view_until_date(tmp_path) -> None:
    repo = _build_repo(tmp_path)
    due = _tomorrow()
    task = repo.create_task("Morgen fällig", due_date=due)
    repo.snooze_task(task["id"], (date.today() + timedelta(days=3)).isoformat())

    assert repo.get_tasks_for_date(due) == []


def test_unsnooze_restores_task(tmp_path) -> None:
    repo = _build_repo(tmp_path)
    task = repo.create_task("Wieder da")
    repo.snooze_task(task["id"], _tomorrow())
    assert repo.get_open_tasks() == []

    restored = repo.unsnooze_task(task["id"])
    assert restored is not None
    assert restored["snoozed_until"] is None
    assert [item["id"] for item in repo.get_open_tasks()] == [task["id"]]


def test_snooze_rejects_past_and_invalid_dates(tmp_path) -> None:
    repo = _build_repo(tmp_path)
    task = repo.create_task("Aufgabe")

    with pytest.raises(ValueError):
        repo.snooze_task(task["id"], _yesterday())
    with pytest.raises(ValueError):
        repo.snooze_task(task["id"], date.today().isoformat())
    with pytest.raises(ValueError):
        repo.snooze_task(task["id"], "13.07.2026")


def test_snooze_unknown_task_returns_none(tmp_path) -> None:
    repo = _build_repo(tmp_path)
    assert repo.snooze_task(999, _tomorrow()) is None
    assert repo.unsnooze_task(999) is None


def test_recurring_task_completion_does_not_inherit_snooze(tmp_path) -> None:
    repo = _build_repo(tmp_path)
    task = repo.create_task(
        "Wöchentlicher Bericht",
        due_date=date.today().isoformat(),
        recurrence="woechentlich",
    )
    repo.snooze_task(task["id"], _tomorrow())
    repo.mark_task_done(task["id"])

    open_tasks = repo.get_open_tasks(include_snoozed=True)
    assert len(open_tasks) == 1
    follow_up = open_tasks[0]
    assert follow_up["id"] != task["id"]
    assert follow_up["snoozed_until"] is None
