"""Local learning question and rule storage for Friday."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Iterable

from friday.app.routine_detector import RoutineCandidate
from friday.storage.database import get_connection
from friday.storage.repositories import ContactRepository


VALID_QUESTION_STATUSES = {"open", "answered", "dismissed"}
VALID_BETREUER = {"philip", "flo", "alex"}


def _now_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _json_loads(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def _sender_key_from_subject_ref(subject_ref: str) -> str:
    if subject_ref.startswith("sender:"):
        return subject_ref.split(":", 1)[1]
    if subject_ref.startswith("mail-topic:"):
        parts = subject_ref.split(":")
        return parts[1] if len(parts) >= 2 else ""
    return subject_ref


def _topic_from_subject_ref(subject_ref: str) -> str:
    if not subject_ref.startswith("mail-topic:"):
        return ""
    parts = subject_ref.split(":", 2)
    return parts[2] if len(parts) >= 3 else ""


def _extract_email(value: str) -> str | None:
    match = re.search(r"[\w.!#$%&'*+/=?^`{|}~-]+@[\w.-]+", value)
    return match.group(0).casefold() if match else None


class LearningRepository:
    """Persist local learning questions and learned deterministic rules."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path
        self.contact_repository = ContactRepository(db_path)

    @staticmethod
    def _row_to_question(row: Any | None) -> dict | None:
        if row is None:
            return None
        item = dict(row)
        item["options"] = _json_loads(item.get("options_json"), [])
        return item

    @staticmethod
    def _row_to_rule(row: Any | None) -> dict | None:
        if row is None:
            return None
        item = dict(row)
        item["value"] = _json_loads(item.get("value_json"), {})
        item["enabled"] = bool(item.get("enabled"))
        return item

    def sync_questions_from_candidates(self, candidates: Iterable[RoutineCandidate]) -> list[dict]:
        """Create one local open question for each new candidate."""
        return [self.create_question_from_candidate(candidate) for candidate in candidates]

    def create_question_from_candidate(self, candidate: RoutineCandidate) -> dict:
        """Create a question for a routine candidate, idempotently."""
        now = _now_iso_timestamp()
        with get_connection(self.db_path) as connection:
            existing = connection.execute(
                """
                SELECT id, kind, subject_ref, question_text, options_json, status, created_at, answered_at
                FROM learning_questions
                WHERE kind = ? AND subject_ref = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (candidate.kind, candidate.subject_ref),
            ).fetchone()
            if existing is not None:
                return self._row_to_question(existing)  # type: ignore[return-value]

            cursor = connection.execute(
                """
                INSERT INTO learning_questions (
                    kind, subject_ref, question_text, options_json, status, created_at, answered_at
                )
                VALUES (?, ?, ?, ?, 'open', ?, NULL)
                """,
                (
                    candidate.kind,
                    candidate.subject_ref,
                    candidate.question_text,
                    _json_dumps(
                        {
                            "subject_label": candidate.subject_label,
                            "suggestion": candidate.suggestion,
                            "evidence": list(candidate.evidence),
                            "items": list(candidate.options),
                        }
                    ),
                    now,
                ),
            )
            row = connection.execute(
                """
                SELECT id, kind, subject_ref, question_text, options_json, status, created_at, answered_at
                FROM learning_questions
                WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_question(row)  # type: ignore[return-value]

    def list_questions(self, status: str | None = None) -> list[dict]:
        """Return local learning questions."""
        status_value = _clean(status).casefold()
        if status_value and status_value not in VALID_QUESTION_STATUSES:
            raise ValueError("Ungültiger Lernfragen-Status.")

        with get_connection(self.db_path) as connection:
            if status_value:
                rows = connection.execute(
                    """
                    SELECT id, kind, subject_ref, question_text, options_json, status, created_at, answered_at
                    FROM learning_questions
                    WHERE status = ?
                    ORDER BY id
                    """,
                    (status_value,),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT id, kind, subject_ref, question_text, options_json, status, created_at, answered_at
                    FROM learning_questions
                    ORDER BY id
                    """
                ).fetchall()
        return [self._row_to_question(row) for row in rows if row is not None]  # type: ignore[list-item]

    def list_open_questions(self) -> list[dict]:
        """Return open learning questions."""
        return self.list_questions("open")

    def get_question(self, question_id: int) -> dict | None:
        """Return one learning question."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT id, kind, subject_ref, question_text, options_json, status, created_at, answered_at
                FROM learning_questions
                WHERE id = ?
                LIMIT 1
                """,
                (int(question_id),),
            ).fetchone()
        return self._row_to_question(row)

    def list_rules(self, *, include_disabled: bool = True) -> list[dict]:
        """Return learned rules."""
        where = "" if include_disabled else "WHERE enabled = 1"
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                f"""
                SELECT id, kind, key, value_json, source_question_id, created_at, enabled
                FROM learned_rules
                {where}
                ORDER BY id
                """
            ).fetchall()
        return [self._row_to_rule(row) for row in rows if row is not None]  # type: ignore[list-item]

    def answer_question(self, question_id: int, option_id: str) -> dict:
        """Apply one selected answer, create/update a rule and close the question."""
        question = self.get_question(question_id)
        if question is None:
            raise ValueError("Lernfrage wurde nicht gefunden.")
        if question["status"] != "open":
            return {
                "question": question,
                "rule": None,
                "applied": False,
                "message": "Lernfrage ist nicht mehr offen.",
            }

        selected = self._select_option(question, option_id)
        rule = self._apply_answer(question, selected)
        now = _now_iso_timestamp()
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                UPDATE learning_questions
                SET status = 'answered',
                    answered_at = ?
                WHERE id = ?
                """,
                (now, int(question_id)),
            )
        updated_question = self.get_question(question_id)
        return {
            "question": updated_question,
            "rule": rule,
            "applied": True,
            "message": "Antwort wurde lokal als Regel gespeichert.",
        }

    def dismiss_question(self, question_id: int) -> dict:
        """Dismiss one open question without applying a rule."""
        question = self.get_question(question_id)
        if question is None:
            raise ValueError("Lernfrage wurde nicht gefunden.")
        now = _now_iso_timestamp()
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                UPDATE learning_questions
                SET status = 'dismissed',
                    answered_at = ?
                WHERE id = ?
                """,
                (now, int(question_id)),
            )
        return {
            "question": self.get_question(question_id),
            "rule": None,
            "applied": False,
            "message": "Lernfrage wurde auf später gesetzt.",
        }

    def set_rule_enabled(self, rule_id: int, enabled: bool) -> dict:
        """Enable or disable a learned rule."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM learned_rules WHERE id = ? LIMIT 1",
                (int(rule_id),),
            ).fetchone()
            if row is None:
                raise ValueError("Lernregel wurde nicht gefunden.")
            connection.execute(
                "UPDATE learned_rules SET enabled = ? WHERE id = ?",
                (1 if enabled else 0, int(rule_id)),
            )
            updated = connection.execute(
                """
                SELECT id, kind, key, value_json, source_question_id, created_at, enabled
                FROM learned_rules
                WHERE id = ?
                """,
                (int(rule_id),),
            ).fetchone()
        return self._row_to_rule(updated)  # type: ignore[return-value]

    def _select_option(self, question: dict, option_id: str) -> dict:
        options_payload = question.get("options") or {}
        options = options_payload.get("items") if isinstance(options_payload, dict) else options_payload
        for option in options or []:
            if str(option.get("id") or "") == option_id:
                return dict(option)
        raise ValueError("Antwortoption wurde nicht gefunden.")

    def _apply_answer(self, question: dict, option: dict) -> dict:
        kind = str(question["kind"])
        option_id = str(option["id"])
        if kind == "frequent_unknown_sender":
            return self._apply_sender_answer(question, option_id)
        if kind == "customer_missing_betreuer":
            return self._apply_customer_betreuer_answer(question, option_id)
        if kind == "recurring_mail_topic":
            return self._apply_mail_topic_answer(question, option_id)
        if kind == "calendar_uncategorized":
            return self._apply_calendar_category_answer(question, option_id)
        return self._upsert_rule(
            kind=f"{kind}_answer",
            key=str(question["subject_ref"]),
            value={"option_id": option_id, "label": option.get("label")},
            source_question_id=int(question["id"]),
        )

    def _apply_sender_answer(self, question: dict, option_id: str) -> dict:
        sender_key = _sender_key_from_subject_ref(str(question["subject_ref"]))
        label = self._question_subject_label(question) or sender_key
        if option_id == "ignorieren":
            return self._upsert_rule(
                kind="sender_ignore",
                key=sender_key,
                value={"sender": label, "ignored": True},
                source_question_id=int(question["id"]),
            )

        contact_type = "arbeit"
        betreuer: str | None = None
        if option_id.startswith("kunde_"):
            contact_type = "kunde"
            betreuer = option_id.split("_", 1)[1]
            if betreuer not in VALID_BETREUER:
                betreuer = None
        elif option_id == "privat":
            contact_type = "freund"
        elif option_id == "arbeit":
            contact_type = "arbeit"

        contact = self._create_or_update_contact(
            sender_key=sender_key,
            display_name=label,
            contact_type=contact_type,
            betreuer=betreuer,
        )
        if contact_type == "kunde" and betreuer == "philip":
            self._refresh_ms_mail_relevance_for_sender(sender_key, label)
        return self._upsert_rule(
            kind="sender_contact",
            key=sender_key,
            value={
                "sender": label,
                "contact_id": contact.get("id"),
                "contact_type": contact_type,
                "betreuer": betreuer,
            },
            source_question_id=int(question["id"]),
        )

    def _apply_customer_betreuer_answer(self, question: dict, option_id: str) -> dict:
        if option_id == "ignorieren":
            return self._upsert_rule(
                kind="customer_betreuer_later",
                key=str(question["subject_ref"]),
                value={"ignored": True},
                source_question_id=int(question["id"]),
            )
        betreuer = option_id.replace("betreuer_", "", 1)
        if betreuer not in VALID_BETREUER:
            raise ValueError("Ungültiger Betreuer.")
        contact_id_raw = str(question["subject_ref"]).replace("contact:", "", 1)
        if not contact_id_raw.isdigit():
            raise ValueError("Kontakt-ID kann nicht aktualisiert werden.")
        contact = self.contact_repository.update_contact(
            int(contact_id_raw),
            contact_type="kunde",
            betreuer=betreuer,
        )
        if contact is None:
            raise ValueError("Kontakt wurde nicht gefunden.")
        return self._upsert_rule(
            kind="customer_betreuer",
            key=f"contact:{contact_id_raw}",
            value={"contact_id": int(contact_id_raw), "betreuer": betreuer},
            source_question_id=int(question["id"]),
        )

    def _apply_mail_topic_answer(self, question: dict, option_id: str) -> dict:
        create_task = option_id == "task_yes"
        topic = _topic_from_subject_ref(str(question["subject_ref"]))
        sender_key = _sender_key_from_subject_ref(str(question["subject_ref"]))
        return self._upsert_rule(
            kind="mail_topic_task_rule",
            key=str(question["subject_ref"]),
            value={
                "sender_key": sender_key,
                "topic": topic,
                "create_task": create_task,
                "ignored": option_id == "ignorieren",
            },
            source_question_id=int(question["id"]),
        )

    def _apply_calendar_category_answer(self, question: dict, option_id: str) -> dict:
        category = option_id.replace("category_", "", 1) if option_id.startswith("category_") else "später"
        return self._upsert_rule(
            kind="calendar_category",
            key=str(question["subject_ref"]),
            value={"category": category, "ignored": option_id == "ignorieren"},
            source_question_id=int(question["id"]),
        )

    def _upsert_rule(
        self,
        *,
        kind: str,
        key: str,
        value: dict[str, Any],
        source_question_id: int,
    ) -> dict:
        now = _now_iso_timestamp()
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO learned_rules (kind, key, value_json, source_question_id, created_at, enabled)
                VALUES (?, ?, ?, ?, ?, 1)
                ON CONFLICT(kind, key) DO UPDATE SET
                    value_json = excluded.value_json,
                    source_question_id = excluded.source_question_id,
                    enabled = 1
                """,
                (kind, key, _json_dumps(value), source_question_id, now),
            )
            row = connection.execute(
                """
                SELECT id, kind, key, value_json, source_question_id, created_at, enabled
                FROM learned_rules
                WHERE kind = ? AND key = ?
                LIMIT 1
                """,
                (kind, key),
            ).fetchone()
        return self._row_to_rule(row)  # type: ignore[return-value]

    def _create_or_update_contact(
        self,
        *,
        sender_key: str,
        display_name: str,
        contact_type: str,
        betreuer: str | None,
    ) -> dict:
        contact = self.contact_repository.find_contact_for_sender(display_name)
        if contact is None and sender_key != display_name:
            contact = self.contact_repository.find_contact_for_sender(sender_key)
        email_address = _extract_email(sender_key) or _extract_email(display_name)
        if contact is None:
            return self.contact_repository.create_contact(
                name=display_name,
                contact_type=contact_type,
                notes="Aus Lernen-Reiter lokal eingeordnet.",
                email_address=email_address,
                betreuer=betreuer,
            )
        return self.contact_repository.update_contact(
            int(contact["id"]),
            contact_type=contact_type,
            email_address=email_address if not contact.get("email_address") else None,
            betreuer=betreuer,
        ) or contact

    def _refresh_ms_mail_relevance_for_sender(self, sender_key: str, display_name: str) -> None:
        patterns = [sender_key.casefold()]
        email = _extract_email(display_name)
        if email:
            patterns.append(email)
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                "SELECT id, sender FROM ms_mail_messages WHERE relevant_for_user = 0"
            ).fetchall()
            matching_ids = [
                int(row["id"])
                for row in rows
                if any(pattern and pattern in str(row["sender"] or "").casefold() for pattern in patterns)
            ]
            for message_id in matching_ids:
                connection.execute(
                    """
                    UPDATE ms_mail_messages
                    SET relevant_for_user = 1,
                        relevance_reason = 'learned_sender_customer_betreuer_philip',
                        relevance_method = 'learned'
                    WHERE id = ?
                    """,
                    (message_id,),
                )

    @staticmethod
    def _question_subject_label(question: dict) -> str:
        options_payload = question.get("options") or {}
        if isinstance(options_payload, dict):
            return _clean(options_payload.get("subject_label"))
        return ""
