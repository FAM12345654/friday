"""Message agent: reads local messages and suggests simple actions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from friday.config import DATA_DIR, USE_SQLITE_STORAGE, get_database_path
from friday.app.calendar_event_extraction import (
    extract_calendar_event_candidate,
    render_calendar_event_review_text,
)
from friday.app.todo_relevance import is_relevant_for_user
from friday.app.whatsapp_inbox_store import (
    WHATSAPP_MESSAGE_ID_OFFSET,
    WhatsAppProcessResult,
    get_unprocessed_whatsapp_messages,
    mark_whatsapp_message_processed,
    read_recent_whatsapp_messages,
)
from friday.storage.repositories import (
    ContactRepository,
    MessageRepository,
    MessageSuggestionRepository,
    MsMailMessageRepository,
    TaskSuggestionRepository,
)


MS_MAIL_MESSAGE_ID_OFFSET = 3_000_000


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
        self.ms_mail_repository = MsMailMessageRepository(self.db_path) if USE_SQLITE_STORAGE else None
        self.suggestion_repository = MessageSuggestionRepository(self.db_path) if USE_SQLITE_STORAGE else None
        self.task_suggestion_repository = (
            TaskSuggestionRepository(self.db_path) if USE_SQLITE_STORAGE else None
        )
        self.contact_agent = contact_agent

    def get_messages(self) -> List[Dict[str, Any]]:
        """Load all local messages."""
        if self.message_repository is not None:
            messages = self.message_repository.get_messages()
            return (
                messages
                + self.get_whatsapp_messages_as_local_messages()
                + self.get_ms_mail_messages_as_local_messages()
            )
        with (DATA_DIR / "sample_messages.json").open("r", encoding="utf-8") as file:
            return json.load(file)

    def get_whatsapp_messages_as_local_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Expose mirrored WhatsApp messages as local read-only message records."""
        if not USE_SQLITE_STORAGE:
            return []
        items: list[Dict[str, Any]] = []
        for item in read_recent_whatsapp_messages(limit=limit, db_path=self.db_path):
            items.append(
                {
                    "id": WHATSAPP_MESSAGE_ID_OFFSET + int(item["id"]),
                    "sender": item.get("sender_name") or "WhatsApp",
                    "text": item.get("body") or "",
                    "received_at": item.get("received_at"),
                    "contact_type": "whatsapp",
                    "source": "whatsapp",
                    "whatsapp_message_id": item.get("id"),
                    "sender_number_masked": item.get("sender_number_masked"),
                }
            )
        return items

    def get_ms_mail_messages_as_local_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Expose synced Microsoft mail previews as local read-only messages."""
        if self.ms_mail_repository is None:
            return []
        items: list[Dict[str, Any]] = []
        for item in self.ms_mail_repository.list_messages(limit=limit):
            subject = str(item.get("subject") or "").strip()
            snippet = str(item.get("snippet") or "").strip()
            text = "\n".join(part for part in (subject, snippet) if part)
            items.append(
                {
                    "id": MS_MAIL_MESSAGE_ID_OFFSET + int(item["id"]),
                    "sender": item.get("sender") or "Microsoft Mail",
                    "text": text,
                    "received_at": item.get("received_at"),
                    "contact_type": "email",
                    "source": "ms_mail",
                    "ms_mail_message_id": item.get("message_id"),
                    "ms_mail_provider_message_id": item.get("provider_message_id"),
                    "ms_mail_account_id": item.get("account_id"),
                    "account_id": item.get("account_id"),
                    "account_username": item.get("account_username"),
                    "subject": subject,
                    "snippet": snippet,
                }
            )
        return items

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

    def get_sender_contact(self, sender: str) -> dict | None:
        """Find a local contact for sender-based relevance checks."""
        if self.contact_agent and hasattr(self.contact_agent, "find_contact_for_sender"):
            return self.contact_agent.find_contact_for_sender(sender)
        if self.contact_repository is None:
            return None
        return self.contact_repository.find_contact_for_sender(sender)

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
            text = str(message.get("text", ""))
            if self.detect_intent(text) != "task":
                continue
            sender = message.get("sender", "Unbekannt")
            sender_contact = self.get_sender_contact(str(sender))
            if not is_relevant_for_user(text=text, sender_contact=sender_contact):
                continue

            title = f"Aufgabe aus Nachricht von {sender}"
            notes = text
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

    def create_calendar_event_suggestion(self, message: Dict[str, Any]) -> dict | None:
        """Create one reviewable calendar-event suggestion from a local message."""
        if self.suggestion_repository is None:
            return None
        extraction = extract_calendar_event_candidate(str(message.get("text") or ""))
        if not extraction.has_event:
            return None
        return self.suggestion_repository.create_suggestion(
            message_id=int(message["id"]),
            draft_text=render_calendar_event_review_text(extraction),
            suggestion_type="calendar_event",
            notes="Termin-Vorschlag: Datum/Zeit wurden lokal durch Python aufgeloest. Kein Kalendertermin wurde erstellt.",
        )

    def process_unprocessed_whatsapp_messages(self) -> WhatsAppProcessResult:
        """Create local review suggestions from mirrored WhatsApp messages."""
        if self.suggestion_repository is None or self.task_suggestion_repository is None:
            return WhatsAppProcessResult(
                processed_count=0,
                message_suggestions_created=0,
                task_suggestions_created=0,
            )

        processed_count = 0
        message_suggestions_created = 0
        task_suggestions_created = 0

        for item in get_unprocessed_whatsapp_messages(db_path=self.db_path):
            synthetic_message = {
                "id": WHATSAPP_MESSAGE_ID_OFFSET + int(item["id"]),
                "sender": item.get("sender_name") or "WhatsApp",
                "text": item.get("body") or "",
                "received_at": item.get("received_at"),
                "contact_type": "whatsapp",
                "source": "whatsapp",
            }
            suggestion_created = False

            reply = self.suggestion_repository.create_suggestion(
                message_id=int(synthetic_message["id"]),
                draft_text=self.create_reply_suggestion(synthetic_message),
                suggestion_type="whatsapp_reply",
                notes="Lokaler WhatsApp-Read-Bridge-Entwurf. Kein Versand.",
            )
            if reply:
                message_suggestions_created += 1
                suggestion_created = True

            synthetic_text = str(synthetic_message.get("text") or "")
            sender_contact = self.get_sender_contact(str(synthetic_message["sender"]))
            if (
                self.detect_intent(synthetic_text) == "task"
                and is_relevant_for_user(text=synthetic_text, sender_contact=sender_contact)
            ):
                task = self.task_suggestion_repository.create_task_suggestion(
                    message_id=int(synthetic_message["id"]),
                    title=f"Aufgabe aus WhatsApp von {synthetic_message['sender']}",
                    category=self.get_contact_type(str(synthetic_message["sender"])),
                    notes="Lokale Aufgabe aus WhatsApp-Read-Bridge.",
                    priority="normal",
                )
                if task:
                    task_suggestions_created += 1
                    suggestion_created = True

            mark_whatsapp_message_processed(
                message_id=int(item["id"]),
                suggestion_created=suggestion_created,
                db_path=self.db_path,
            )
            processed_count += 1

        return WhatsAppProcessResult(
            processed_count=processed_count,
            message_suggestions_created=message_suggestions_created,
            task_suggestions_created=task_suggestions_created,
        )

    def process_unprocessed_ms_mail_messages(self) -> dict[str, int]:
        """Create local review suggestions from synced Microsoft mail previews."""
        if (
            self.ms_mail_repository is None
            or self.suggestion_repository is None
            or self.task_suggestion_repository is None
        ):
            return {
                "processed_count": 0,
                "message_suggestions_created": 0,
                "task_suggestions_created": 0,
                "calendar_suggestions_created": 0,
            }

        processed_count = 0
        message_suggestions_created = 0
        task_suggestions_created = 0
        calendar_suggestions_created = 0

        for item in self.ms_mail_repository.get_unprocessed_messages():
            synthetic_message = {
                "id": MS_MAIL_MESSAGE_ID_OFFSET + int(item["id"]),
                "sender": item.get("sender") or "Microsoft Mail",
                "text": "\n".join(
                    part
                    for part in (
                        str(item.get("subject") or "").strip(),
                        str(item.get("snippet") or "").strip(),
                    )
                    if part
                ),
                "received_at": item.get("received_at"),
                "contact_type": "email",
                "source": "ms_mail",
                "ms_mail_message_id": item.get("message_id"),
                "ms_mail_provider_message_id": item.get("provider_message_id"),
                "ms_mail_account_id": item.get("account_id"),
                "account_id": item.get("account_id"),
                "account_username": item.get("account_username"),
            }
            suggestion_created = False
            text = str(synthetic_message.get("text") or "")

            if self.is_scheduling_related(text):
                reply = self.suggestion_repository.create_suggestion(
                    message_id=int(synthetic_message["id"]),
                    draft_text=self.create_reply_suggestion(synthetic_message),
                    suggestion_type="ms_mail_reply",
                    notes="Lokaler Microsoft-Mail-Read-Only-Entwurf. Kein Versand.",
                )
                if reply:
                    message_suggestions_created += 1
                    suggestion_created = True

            calendar_suggestion = self.create_calendar_event_suggestion(synthetic_message)
            if calendar_suggestion:
                calendar_suggestions_created += 1
                suggestion_created = True

            sender = str(synthetic_message.get("sender") or "")
            sender_contact = self.get_sender_contact(sender)
            if self.detect_intent(text) == "task" and is_relevant_for_user(
                text=text,
                sender_contact=sender_contact,
            ):
                task = self.task_suggestion_repository.create_task_suggestion(
                    message_id=int(synthetic_message["id"]),
                    title=f"Aufgabe aus E-Mail von {sender}",
                    category=self.get_contact_type(sender),
                    notes=text,
                    priority="normal",
                )
                if task:
                    task_suggestions_created += 1
                    suggestion_created = True

            self.ms_mail_repository.mark_processed(
                int(item["id"]),
                suggestion_created=suggestion_created,
            )
            processed_count += 1

        return {
            "processed_count": processed_count,
            "message_suggestions_created": message_suggestions_created,
            "task_suggestions_created": task_suggestions_created,
            "calendar_suggestions_created": calendar_suggestions_created,
        }

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
