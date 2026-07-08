"""Calendar agent: local availability and free-slot suggestions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from friday.app.date_utils import resolve_today
from friday.config import DATA_DIR, USE_SQLITE_STORAGE, get_database_path
from friday.storage.repositories import CalendarRepository, CalendarSuggestionRepository


class CalendarAgent:
    """Use local sample calendar data only."""

    def __init__(self, db_path: Path | None = None) -> None:
        # Keep everything local in this first phase.
        self.db_path = db_path or get_database_path()
        self.calendar_repository = CalendarRepository(self.db_path) if USE_SQLITE_STORAGE else None
        self.calendar_suggestion_repository = (
            CalendarSuggestionRepository(self.db_path) if USE_SQLITE_STORAGE else None
        )

    def load_calendar(self) -> List[Dict[str, Any]]:
        """Load local calendar blocks."""
        if self.calendar_repository is None:
            with (DATA_DIR / "sample_calendar.json").open("r", encoding="utf-8") as file:
                return json.load(file)
        return self.calendar_repository.get_items_for_date(self._effective_today())

    def get_items_for_date(self, date_iso: str) -> List[Dict[str, Any]]:
        """Return all events for one date."""
        if self.calendar_repository is None:
            return [item for item in self.load_calendar() if item.get("date") == date_iso]
        return self.calendar_repository.get_items_for_date(date_iso)

    def get_free_slots_for_date(self, date_iso: str, duration_minutes: int = 60) -> List[Dict[str, str]]:
        """Find fake free slots from sample busy blocks.

        Workday is fixed for now: 09:00 - 18:00.
        """
        if self.calendar_repository is None:
            return self._fallback_free_slots_for_date(date_iso, duration_minutes)
        return self.calendar_repository.get_free_slots_for_date(date_iso, duration_minutes)

    def generate_calendar_suggestions_for_message(
        self,
        message_id: int,
        date_iso: str | None = None,
        duration_minutes: int = 60,
    ) -> list[Dict[str, Any]]:
        """Create (or return existing) local calendar suggestions for one message."""
        if self.calendar_suggestion_repository is None:
            return []

        target_date = date_iso or self._effective_today()
        slots = self.get_free_slots_for_date(target_date, duration_minutes)
        suggestions: list[Dict[str, Any]] = []
        for slot in slots:
            suggestion = self.calendar_suggestion_repository.create_calendar_suggestion(
                message_id=message_id,
                slot_date=target_date,
                start=slot["start"],
                end=slot["end"],
            )
            suggestions.append(suggestion)
        return suggestions

    def get_calendar_suggestions_for_message(self, message_id: int) -> list[Dict[str, Any]]:
        """Return all local calendar suggestions for one message."""
        if self.calendar_suggestion_repository is None:
            return []
        return self.calendar_suggestion_repository.get_calendar_suggestions_for_message(message_id)

    def get_pending_calendar_suggestions_for_message(self, message_id: int) -> list[Dict[str, Any]]:
        """Return pending local calendar suggestions for one message."""
        if self.calendar_suggestion_repository is None:
            return []
        return self.calendar_suggestion_repository.get_pending_calendar_suggestions_for_message(message_id)

    def get_calendar_suggestion_by_id(self, suggestion_id: int) -> dict | None:
        """Return one local calendar suggestion by id."""
        if self.calendar_suggestion_repository is None:
            return None
        return self.calendar_suggestion_repository.get_calendar_suggestion_by_id(suggestion_id)

    def select_calendar_suggestion(self, suggestion_id: int) -> dict | None:
        """Mark one local calendar suggestion as selected."""
        if self.calendar_suggestion_repository is None:
            return None
        return self.calendar_suggestion_repository.select_calendar_suggestion(suggestion_id)

    def reject_calendar_suggestion(self, suggestion_id: int) -> dict | None:
        """Mark one local calendar suggestion as rejected."""
        if self.calendar_suggestion_repository is None:
            return None
        return self.calendar_suggestion_repository.reject_calendar_suggestion(suggestion_id)

    def _fallback_free_slots_for_date(self, date_iso: str, duration_minutes: int) -> List[Dict[str, str]]:
        """Create slots from fallback JSON data when repositories are not used."""
        busy = []
        for item in self.get_items_for_date(date_iso):
            busy.append((self._to_minutes(item["start"]), self._to_minutes(item["end"])))
        busy.sort()

        start = 9 * 60
        end = 18 * 60
        free_slots: List[Dict[str, str]] = []
        slot_start = start
        while slot_start + duration_minutes <= end:
            slot_end = slot_start + duration_minutes
            overlap = any(not (slot_end <= b_start or slot_start >= b_end) for b_start, b_end in busy)
            if not overlap:
                free_slots.append({
                    "start": self._to_time_string(slot_start),
                    "end": self._to_time_string(slot_end),
                })
            slot_start += 60
        return free_slots

    @staticmethod
    def _to_minutes(time_iso: str) -> int:
        """Convert HH:MM to minutes for simple free-slot math."""
        if ":" not in time_iso:
            return 0
        hours, minutes = map(int, time_iso.split(":"))
        return hours * 60 + minutes

    @staticmethod
    def _to_time_string(minutes: int) -> str:
        """Convert minutes back to HH:MM."""
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    def _effective_today(self) -> str:
        """Return Friday's effective current date."""
        return resolve_today()

    def get_free_slots_today(self, duration_minutes: int = 60) -> List[Dict[str, str]]:
        """Shortcut for suggestions on today's local date."""
        return self.get_free_slots_for_date(self._effective_today(), duration_minutes)

    # Placeholder for later when real calendar APIs are available.
    def sync_real_calendar(self) -> str:
        """Keep this as a clear placeholder for future read/write integrations."""
        return "Real calendar integration is disabled in this skeleton."
