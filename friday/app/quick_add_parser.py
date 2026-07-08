"""Parse one-line local task quick-add input."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from friday.app.date_utils import resolve_today


PRIORITY_MARKERS = {
    "!niedrig": "low",
    "!mittel": "normal",
    "!hoch": "high",
    "!dringend": "urgent",
}

RECURRENCE_MARKERS = {
    "#taeglich": "taeglich",
    "#täglich": "taeglich",
    "#woechentlich": "woechentlich",
    "#wöchentlich": "woechentlich",
    "#monatlich": "monatlich",
}


@dataclass(frozen=True)
class QuickAddParseResult:
    """Structured result for a quick-add task line."""

    title: str
    priority: str
    due_date: str | None
    recurrence: str | None
    error: str | None = None

    @property
    def valid(self) -> bool:
        return self.error is None


def _parse_due_date(marker: str, today: str) -> str | None:
    raw_value = marker[1:].strip().lower()
    if raw_value == "heute":
        return today
    if raw_value == "morgen":
        return (date.fromisoformat(today) + timedelta(days=1)).isoformat()
    try:
        return date.fromisoformat(raw_value).isoformat()
    except ValueError:
        return None


def parse_quick_add_task(raw_text: str, today: str | None = None) -> QuickAddParseResult:
    """Parse quick-add text into task fields without side effects."""
    effective_today = today or resolve_today()
    tokens = (raw_text or "").split()
    if not tokens:
        return QuickAddParseResult(
            title="",
            priority="normal",
            due_date=None,
            recurrence=None,
            error="Eine Aufgabe braucht mindestens einen Titel.",
        )

    priority: str | None = None
    due_date: str | None = None
    recurrence: str | None = None
    title_tokens: list[str] = []

    for token in tokens:
        lowered = token.lower()
        if lowered.startswith("!"):
            if priority is not None:
                return QuickAddParseResult("", "normal", None, None, "Priorität wurde mehrfach angegeben.")
            if lowered not in PRIORITY_MARKERS:
                return QuickAddParseResult("", "normal", None, None, f"Unbekannte Priorität: {token}")
            priority = PRIORITY_MARKERS[lowered]
            continue

        if lowered.startswith("@"):
            if due_date is not None:
                return QuickAddParseResult("", "normal", None, None, "Fälligkeitsdatum wurde mehrfach angegeben.")
            parsed_due_date = _parse_due_date(lowered, effective_today)
            if parsed_due_date is None:
                return QuickAddParseResult("", "normal", None, None, f"Ungültiges Fälligkeitsdatum: {token}")
            due_date = parsed_due_date
            continue

        if lowered.startswith("#"):
            if recurrence is not None:
                return QuickAddParseResult("", "normal", None, None, "Wiederholung wurde mehrfach angegeben.")
            if lowered not in RECURRENCE_MARKERS:
                return QuickAddParseResult("", "normal", None, None, f"Unbekannte Wiederholung: {token}")
            recurrence = RECURRENCE_MARKERS[lowered]
            continue

        title_tokens.append(token)

    title = " ".join(title_tokens).strip()
    if not title:
        return QuickAddParseResult(
            title="",
            priority="normal",
            due_date=None,
            recurrence=None,
            error="Eine Aufgabe braucht mindestens einen Titel.",
        )

    return QuickAddParseResult(
        title=title,
        priority=priority or "normal",
        due_date=due_date,
        recurrence=recurrence,
        error=None,
    )
