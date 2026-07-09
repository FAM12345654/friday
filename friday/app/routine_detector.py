"""Local routine detection for Friday's learning questions."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
import re
from typing import Any, Callable, Iterable, Mapping

from friday.app.contact_context_preview import normalize_contact_name


RoutineAISuggester = Callable[
    [tuple[Mapping[str, Any], ...], tuple[Mapping[str, Any], ...], tuple[Mapping[str, Any], ...]],
    Iterable[Mapping[str, Any] | "RoutineCandidate"],
]

_EMAIL_RE = re.compile(r"[\w.!#$%&'*+/=?^`{|}~-]+@[\w.-]+")
_TOPIC_RE = re.compile(r"[0-9A-Za-zÄÖÜäöüß]+")
_STOPWORDS = {
    "bitte",
    "danke",
    "hallo",
    "wegen",
    "fuer",
    "für",
    "und",
    "oder",
    "der",
    "die",
    "das",
    "ein",
    "eine",
    "von",
    "zur",
    "zum",
    "mit",
    "ich",
    "du",
    "wir",
    "sie",
    "ist",
    "sind",
}


@dataclass(frozen=True)
class RoutineCandidate:
    """One local pattern Friday can turn into a user question."""

    kind: str
    subject_ref: str
    subject_label: str
    question_text: str
    options: tuple[dict[str, str], ...]
    suggestion: str
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation."""
        payload = asdict(self)
        payload["options"] = [dict(item) for item in self.options]
        payload["evidence"] = list(self.evidence)
        return payload


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _sender_email(sender: str | None) -> str:
    match = _EMAIL_RE.search(str(sender or ""))
    return match.group(0).casefold() if match else ""


def _sender_key(sender: str | None) -> str:
    email = _sender_email(sender)
    if email:
        return email
    return normalize_contact_name(str(sender or ""))


def _known_sender_keys(contacts: Iterable[Mapping[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for contact in contacts:
        for field in ("name", "email_address", "whatsapp_target"):
            value = _clean(contact.get(field))
            if value:
                keys.add(_sender_key(value))
    return {key for key in keys if key}


def _contact_options() -> tuple[dict[str, str], ...]:
    return (
        {"id": "kunde_philip", "label": "Kunde, Betreuer Philip"},
        {"id": "kunde_flo", "label": "Kunde, Betreuer Flo"},
        {"id": "kunde_alex", "label": "Kunde, Betreuer Alex"},
        {"id": "arbeit", "label": "Arbeit"},
        {"id": "privat", "label": "Privat / Freund"},
        {"id": "ignorieren", "label": "Ignorieren"},
    )


def _betreuer_options() -> tuple[dict[str, str], ...]:
    return (
        {"id": "betreuer_philip", "label": "Philip"},
        {"id": "betreuer_flo", "label": "Flo"},
        {"id": "betreuer_alex", "label": "Alex"},
        {"id": "ignorieren", "label": "Später / ignorieren"},
    )


def _task_rule_options() -> tuple[dict[str, str], ...]:
    return (
        {"id": "task_yes", "label": "Ja, künftig Aufgabe vorschlagen"},
        {"id": "task_no", "label": "Nein, nur anzeigen"},
        {"id": "ignorieren", "label": "Später"},
    )


def _calendar_category_options() -> tuple[dict[str, str], ...]:
    return (
        {"id": "category_arbeit", "label": "Arbeit"},
        {"id": "category_kunde", "label": "Kunde"},
        {"id": "category_privat", "label": "Privat"},
        {"id": "ignorieren", "label": "Später"},
    )


def _topic_key(message: Mapping[str, Any]) -> str:
    text = " ".join(
        _clean(message.get(field))
        for field in ("subject", "snippet", "text")
        if _clean(message.get(field))
    )
    tokens = [
        token.casefold()
        for token in _TOPIC_RE.findall(text)
        if len(token) >= 4 and token.casefold() not in _STOPWORDS
    ]
    if not tokens:
        return ""
    most_common = Counter(tokens).most_common(3)
    return " ".join(token for token, _count in most_common)


def _message_evidence(message: Mapping[str, Any]) -> str:
    subject = _clean(message.get("subject"))
    text = _clean(message.get("snippet") or message.get("text"))
    sender = _clean(message.get("sender")) or "Unbekannt"
    label = subject or text[:80] or "Nachricht"
    return f"{sender}: {label}"[:160]


def _calendar_title_key(item: Mapping[str, Any]) -> str:
    return normalize_contact_name(str(item.get("title") or ""))


def _has_calendar_category(item: Mapping[str, Any]) -> bool:
    for field in ("category", "contact_type", "calendar_category"):
        if _clean(item.get(field)):
            return True
    return False


def _dedupe(candidates: Iterable[RoutineCandidate]) -> tuple[RoutineCandidate, ...]:
    seen: set[tuple[str, str]] = set()
    result: list[RoutineCandidate] = []
    for candidate in candidates:
        key = (candidate.kind, candidate.subject_ref)
        if key in seen:
            continue
        seen.add(key)
        result.append(candidate)
    return tuple(result)


def detect_routine_candidates(
    *,
    messages: Iterable[Mapping[str, Any]] = (),
    contacts: Iterable[Mapping[str, Any]] = (),
    calendar_items: Iterable[Mapping[str, Any]] = (),
    ai_suggester: RoutineAISuggester | None = None,
) -> tuple[RoutineCandidate, ...]:
    """Return local routine candidates without writing anything."""
    message_items = tuple(messages)
    contact_items = tuple(contacts)
    calendar_items_tuple = tuple(calendar_items)
    known_keys = _known_sender_keys(contact_items)
    candidates: list[RoutineCandidate] = []

    messages_by_sender: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for message in message_items:
        sender = _clean(message.get("sender"))
        key = _sender_key(sender)
        if key:
            messages_by_sender[key].append(message)

    for sender_key, sender_messages in sorted(messages_by_sender.items()):
        if sender_key in known_keys or len(sender_messages) < 2:
            continue
        label = _clean(sender_messages[0].get("sender")) or sender_key
        candidates.append(
            RoutineCandidate(
                kind="frequent_unknown_sender",
                subject_ref=f"sender:{sender_key}",
                subject_label=label,
                question_text=f"Absender {label} schreibt öfter. Wer ist das?",
                options=_contact_options(),
                suggestion="Kontakt lokal einordnen, damit Friday die Zuständigkeit besser erkennt.",
                evidence=tuple(_message_evidence(item) for item in sender_messages[:3]),
            )
        )

    for contact in contact_items:
        contact_type = _clean(contact.get("contact_type") or contact.get("category")).casefold()
        betreuer = _clean(contact.get("betreuer"))
        if contact_type == "kunde" and not betreuer:
            label = _clean(contact.get("name") or contact.get("display_name")) or "Kunde"
            contact_id = _clean(contact.get("id") or contact.get("contact_id") or label)
            candidates.append(
                RoutineCandidate(
                    kind="customer_missing_betreuer",
                    subject_ref=f"contact:{contact_id}",
                    subject_label=label,
                    question_text=f"Kunde {label} hat noch keinen Betreuer. Wer ist zuständig?",
                    options=_betreuer_options(),
                    suggestion="Betreuer setzen, damit Mails und Aufgaben korrekt zugeordnet werden.",
                    evidence=(f"Kontaktart: {contact_type}",),
                )
            )

    topics_by_sender: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for message in message_items:
        sender_key = _sender_key(message.get("sender"))
        topic = _topic_key(message)
        if sender_key and topic:
            topics_by_sender[(sender_key, topic)].append(message)

    for (sender_key, topic), topic_messages in sorted(topics_by_sender.items()):
        if len(topic_messages) < 2:
            continue
        label = _clean(topic_messages[0].get("sender")) or sender_key
        candidates.append(
            RoutineCandidate(
                kind="recurring_mail_topic",
                subject_ref=f"mail-topic:{sender_key}:{topic}",
                subject_label=f"{label} / {topic}",
                question_text=f"{label} schreibt wiederholt zu '{topic}'. Soll Friday daraus künftig Aufgaben vorschlagen?",
                options=_task_rule_options(),
                suggestion="Lokale Aufgaben-Regel für wiederkehrende Mail-Themen.",
                evidence=tuple(_message_evidence(item) for item in topic_messages[:3]),
            )
        )

    calendar_by_title: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for item in calendar_items_tuple:
        title_key = _calendar_title_key(item)
        if title_key:
            calendar_by_title[title_key].append(item)

    for title_key, entries in sorted(calendar_by_title.items()):
        uncategorized = [item for item in entries if not _has_calendar_category(item)]
        if len(uncategorized) < 2:
            continue
        label = _clean(uncategorized[0].get("title")) or title_key
        evidence = tuple(
            f"{_clean(item.get('date')) or _clean(item.get('start')) or '-'}: {label}"
            for item in uncategorized[:3]
        )
        candidates.append(
            RoutineCandidate(
                kind="calendar_uncategorized",
                subject_ref=f"calendar:{title_key}",
                subject_label=label,
                question_text=f"Termin '{label}' kommt öfter vor. Welche Kategorie passt?",
                options=_calendar_category_options(),
                suggestion="Lokale Kalender-Kategorie als Regel merken.",
                evidence=evidence,
            )
        )

    if ai_suggester is not None:
        for raw_candidate in ai_suggester(message_items, contact_items, calendar_items_tuple):
            if isinstance(raw_candidate, RoutineCandidate):
                candidates.append(raw_candidate)
            elif isinstance(raw_candidate, Mapping):
                candidates.append(
                    RoutineCandidate(
                        kind=_clean(raw_candidate.get("kind")) or "ai_local_routine",
                        subject_ref=_clean(raw_candidate.get("subject_ref")) or "ai:unknown",
                        subject_label=_clean(raw_candidate.get("subject_label")) or "KI-Kandidat",
                        question_text=_clean(raw_candidate.get("question_text")) or "Soll Friday diese Routine merken?",
                        options=tuple(raw_candidate.get("options") or _task_rule_options()),  # type: ignore[arg-type]
                        suggestion=_clean(raw_candidate.get("suggestion")) or "Lokaler KI-Hinweis.",
                        evidence=tuple(str(item) for item in raw_candidate.get("evidence") or ()),
                    )
                )

    return _dedupe(candidates)
