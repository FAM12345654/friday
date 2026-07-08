"""Task agent: reads and writes local SQLite task data."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from friday.app.date_utils import resolve_today
from friday.config import USE_SQLITE_STORAGE, get_database_path
from friday.storage.repositories import TaskRepository


class TaskAgent:
    """Work with tasks from local SQLite storage."""

    def __init__(self, db_path: Path | None = None) -> None:
        # Use the local repository when SQLite mode is enabled.
        self.db_path = db_path or get_database_path()
        self.repository = TaskRepository(self.db_path) if USE_SQLITE_STORAGE else None

    def get_open_tasks(self) -> List[Dict[str, Any]]:
        """Return tasks that are not marked as done."""
        if self.repository is None:
            return []
        return self.repository.get_open_tasks()

    def get_task_by_id(self, task_id: int) -> Dict[str, Any] | None:
        """Return one task for editing or completion."""
        if self.repository is None:
            return None
        return self.repository.get_task_by_id(task_id)

    def get_tasks_for_date(self, date_iso: str | None = None) -> List[Dict[str, Any]]:
        """Return tasks for one date string."""
        target_date = date_iso or self._effective_today()
        if self.repository is None:
            return []
        return self.repository.get_tasks_for_date(target_date)

    def get_tasks_for_dashboard(self) -> List[Dict[str, Any]]:
        """Return open tasks for the currently selected day."""
        return self.get_tasks_for_date()

    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Return tasks for a specific status."""
        if self.repository is None:
            return []
        return self.repository.get_tasks_by_status(status)

    def search_tasks(
        self,
        query: str,
        status: str | None = None,
        category: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Search local tasks by title and notes."""
        if self.repository is None:
            return []
        return self.repository.search_tasks(query=query, status=status, category=category)

    def filter_tasks(
        self,
        status: str | None = None,
        category: str | None = None,
        due_date: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Filter local tasks by simple task properties."""
        if self.repository is None:
            return []
        return self.repository.filter_tasks(status=status, category=category, due_date=due_date)

    def archive_task(self, task_id: int) -> Dict[str, Any] | None:
        """Archive one task locally by setting its status."""
        if self.repository is None:
            return None
        return self.repository.archive_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        """Delete one task locally. Returns True when a task was removed."""
        if self.repository is None:
            return False
        return self.repository.delete_task(task_id)

    def create_task(
        self,
        title: str,
        category: str | None = None,
        due_date: str | None = None,
        notes: str | None = None,
        priority: str | None = None,
        recurrence: str | None = None,
    ) -> Dict[str, Any]:
        """Create a local task and return the stored record."""
        if self.repository is None:
            raise RuntimeError("Lokale SQLite-Aufgabenverwaltung ist nicht aktiv.")
        return self.repository.create_task(
            title=title,
            category=category,
            due_date=due_date,
            notes=notes,
            status="open",
            priority=priority,
            recurrence=recurrence,
        )

    def edit_task(
        self,
        task_id: int,
        title: str | None = None,
        category: str | None = None,
        due_date: str | None = None,
        notes: str | None = None,
        priority: str | None = None,
        recurrence: str | None = None,
    ) -> Dict[str, Any] | None:
        """Update one local task and return the changed record."""
        if self.repository is None:
            return None
        return self.repository.update_task(
            task_id=task_id,
            title=title,
            category=category,
            due_date=due_date,
            notes=notes,
            priority=priority,
            recurrence=recurrence,
        )

    def mark_task_done(self, task_id: int) -> Dict[str, Any] | None:
        """Set one task status to done."""
        if self.repository is None:
            return None
        return self.repository.mark_task_done(task_id)

    def _effective_today(self) -> str:
        """Return Friday's effective current date."""
        return resolve_today()

    def detect_priority_hint(self, task: Dict[str, Any]) -> str:
        """Very simple placeholder priority detection."""
        text = f"{task.get('title', '')} {task.get('notes', '')}".lower()
        # Placeholder rule: urgent words -> high, else normal.
        keywords = {"dringend", "kritisch", "deadline", "sofort"}
        return "high" if any(word in text for word in keywords) else "normal"
