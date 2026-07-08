"""Morning briefing agent: builds a local text preview."""

from __future__ import annotations

from typing import Any, Dict

from friday.app.date_utils import resolve_today
from friday.agents.calendar_agent import CalendarAgent
from friday.agents.task_agent import TaskAgent


class MorningBriefingAgent:
    """Create a read-only local preview for the morning."""

    def __init__(self, task_agent: TaskAgent | None = None, calendar_agent: CalendarAgent | None = None) -> None:
        self.task_agent = task_agent or TaskAgent()
        self.calendar_agent = calendar_agent or CalendarAgent()

    def build_preview(self, today_iso: str | None = None) -> Dict[str, Any]:
        """Collect local sample content for a morning snapshot."""
        day = today_iso or self._effective_today()
        tasks = self.task_agent.get_tasks_for_date(day)
        calendar_items = self.calendar_agent.get_items_for_date(day)

        # Weather and music stay placeholders in this local skeleton.
        return {
            "date": day,
            "tasks": tasks,
            "calendar_items": calendar_items,
            "weather": "Wetterdienst ist in diesem Schritt deaktiviert.",
            "music": "Musikvorschlag: ruhige Hintergrundmusik (lokal geplant).",
        }

    def _effective_today(self) -> str:
        """Return Friday's effective current date."""
        return resolve_today()
