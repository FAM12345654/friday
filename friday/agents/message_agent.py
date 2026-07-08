"""Message agent: reads local messages and suggests simple actions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from friday.config import DATA_DIR, USE_SQLITE_STORAGE, get_database_path
from friday.storage.repositories import (
    ContactRepository,
    MessageRepository,
    MessageSuggestionRepository,
    TaskSuggestionRepository,
)


class MessageAgent:
    """Handle local sample messages only."""

    SCHEDULING_KEYWORDS = (
        "zeit",
        "treffen",
        "meeting",
        "nächste woche",
        "morgen",
        "übermorgen",
        "uhr",
        "verfügbar",
    )
    TASK_KEYWORDS = (
        "bitte erledigen",
        "kannst du",
        "mach bitte",
        "prüfe",
        "absenden",
        "eintragen",
        "fertig",
        "bestätigen",
        "brauche",
        "todo",
        "aufgabe",
        "erledigen",
        "schicken",
        "vorbereiten",
        "prüfen",
    )
    QUESTION_PREFIXES = (
        "wer ",
        "was ",
        "wann ",
        "wo ",
        "wie ",
        "warum ",
        "kannst du mir sagen",
    )
    QUESTION_SUFFIX = "?"
    INFO_KEYWORDS = (
        "zur info",
        "nur zur kenntnis",
        "update",
        "status",
        "fyi",
        "ich wollte dir sagen",
    )

    def __init__(self, db_path: Path | None = None, contact_agent: Any | None = None) -> None:
        # Message handling stays offline; no API calls are made here.
        self.db_path = db_path or get_database_path()
        self.message_repository = MessageRepository(self.db_path) if USE_SQLITE_STORAGE else None
        self.contact_repository = ContactRepository(self.db_path) if USE_SQLITE_STORAGE else None
        self.suggestion_repository = MessageSuggestionRepository(self.db_path) if USE_SQLITE_STORAGE else None
        self.task_suggestion_repository = (
            TaskSuggestionRepository(self.db_path) if USE_SQLITE_STORAGE else None
        )
        self.contact_agent = contact_agent

    def get_messages(self) -> List[Dict[str, Any]]:
        """Load all local messages."""
        if self.message_repository is not None:
            return self.message_repository.get_messages()
        with (DATA_DIR / "sample_messages.json").open("r", encoding="utf-8") as file:
            return json.load(file)

    def detect_intent(self, text: str) -> str:
        """Classify local text into a tiny, rule-based intent."""
        lowered = text.strip().lower()
        if any(keyword in lowered for keyword in self.SCHEDULING_KEYWORDS):
            return "scheduling"
        if any(keyword in lowered for keyword in self.TASK_KEYWORDS):
            return "task"
        if self.QUESTION_SUFFIX in lowered or lowered.startswith(self.QUESTION_PREFIXES):
            return "question"
        if any(keyword in lowered for keyword in self.INFO_KEYWORDS):
            return "info"
        return "unclear"

    def is_scheduling_related(self, text: str) -> bool:
        """Detect simple scheduling intent by keyword match."""
        return self.detect_intent(text) == "scheduling"

    def create_reply_suggestion(self, message: Dict[str, Any]) -> str:
        """Return a safe placeholder reply suggestion."""
        sender = message.get("sender", "Unbekannt")
        # This is a local draft only. No messages are sent in this step.
        if self.detect_intent(message.get("text", "")) == "scheduling":
            return f"[Platzhalter] Hallo {sender}, ich prüfe den Termin und bestätige kurz die passenden Zeiten."
        if "?" in message.get("text", ""):
            return f"[Platzhalter] Hallo {sender}, danke für die Frage. Ich schaue kurz nach und antworte dann."
        return f"[Platzhalter] Hallo {sender}, verstanden — ich nehme es zur Kenntnis."

    def get_contact_type(self, sender: str) -> str:
        """Ask ContactContextAgent for a category if it was passed in."""
        if not self.contact_agent:
            if self.contact_repository is None:
                return "other"
            return self.contact_repository.get_contact_type_by_name(sender)
        return self.contact_agent.get_category_for_sender(sender)

    def generate_local_suggestions(self) -> list[Dict[str, Any]]:
        """Create local reply suggestions for scheduling-related messages.

        Duplicate suggestions for the same message and type are returned as-is.
        """
        if self.suggestion_repository is None:
            return []

        suggestions: list[Dict[str, Any]] = []
        for message in self.get_messages():
            if self.is_scheduling_related(message.get("text", "")):
                suggestion = self.create_reply_suggestion(message)
                suggestions.append(
                    self.suggestion_repository.create_suggestion(
                        message_id=int(message["id"]),
                        draft_text=suggestion,
                    )
                )
        return suggestions

    def generate_local_task_suggestions(self) -> list[Dict[str, Any]]:
        """Create local task suggestions for task-related messages."""
        if self.task_suggestion_repository is None:
            return []

        suggestions: list[Dict[str, Any]] = []
        for message in self.get_messages():
            if self.detect_intent(message.get("text", "")) != "task":
                continue

            sender = message.get("sender", "Unbekannt")
            title = f"Aufgabe aus Nachricht von {sender}"
            notes = str(message.get("text", ""))
            category = self.get_contact_type(sender)
            suggestions.append(
                self.task_suggestion_repository.create_task_suggestion(
                    message_id=int(message["id"]),
                    title=title,
                    category=category or "other",
                    notes=notes,
                    priority="normal",
                )
            )
        return suggestions

    def get_pending_suggestions(self) -> list[Dict[str, Any]]:
        """Return local scheduling suggestions still waiting for review."""
        if self.suggestion_repository is None:
            return []
        return self.suggestion_repository.get_pending_suggestions()

    def get_pending_task_suggestions(self) -> list[Dict[str, Any]]:
        """Return local task suggestions still waiting for review."""
        if self.task_suggestion_repository is None:
            return []
        return self.task_suggestion_repository.get_pending_task_suggestions()

    def approve_suggestion(self, suggestion_id: int) -> dict | None:
        """Mark a suggestion as approved without sending anything."""
        if self.suggestion_repository is None:
            return None
        return self.suggestion_repository.update_suggestion_status(suggestion_id, status="approved")

    def reject_suggestion(self, suggestion_id: int) -> dict | None:
        """Mark a suggestion as rejected without deleting it."""
        if self.suggestion_repository is None:
            return None
        return self.suggestion_repository.update_suggestion_status(suggestion_id, status="rejected")

    def edit_suggestion(self, suggestion_id: int, draft_text: str) -> dict | None:
        """Edit draft text locally and mark the record as edited."""
        if self.suggestion_repository is None:
            return None
        return self.suggestion_repository.edit_suggestion_draft(suggestion_id, draft_text=draft_text)

    def reject_task_suggestion(self, suggestion_id: int) -> dict | None:
        """Mark one task suggestion as rejected."""
        if self.task_suggestion_repository is None:
            return None
        return self.task_suggestion_repository.update_task_suggestion_status(
            suggestion_id,
            status="rejected",
        )

    def edit_task_suggestion(
        self,
        suggestion_id: int,
        title: str | None = None,
        category: str | None = None,
        due_date: str | None = None,
        notes: str | None = None,
        priority: str | None = None,
    ) -> dict | None:
        """Edit local task suggestion fields and keep review open."""
        if self.task_suggestion_repository is None:
            return None
        return self.task_suggestion_repository.edit_task_suggestion(
            suggestion_id=suggestion_id,
            title=title,
            category=category,
            due_date=due_date,
            notes=notes,
            priority=priority,
        )

    def mark_task_suggestion_converted(self, suggestion_id: int, created_task_id: int) -> dict | None:
        """Mark one task suggestion as converted into a real task."""
        if self.task_suggestion_repository is None:
            return None
        return self.task_suggestion_repository.mark_task_suggestion_converted(
            suggestion_id=suggestion_id,
            created_task_id=created_task_id,
        )

    def approve_task_suggestion(self, suggestion_id: int) -> dict | None:
        """Mark one task suggestion as approved."""
        if self.task_suggestion_repository is None:
            return None
        return self.task_suggestion_repository.update_task_suggestion_status(
            suggestion_id=suggestion_id,
            status="approved",
        )
