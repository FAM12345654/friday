"""Deterministic local calendar event extraction helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta
import re
from urllib.parse import quote_plus

from friday.app.date_utils import resolve_today


WEEKDAY_INDEX: dict[str, int] = {
    "montag": 0,
    "dienstag": 1,
    "mittwoch": 2,
    "donnerstag": 3,
    "freitag": 4,
    "samstag": 5,
    "sonntag": 6,
}


@dataclass(frozen=True)
class CalendarEventExtraction:
    """One local calendar event extraction preview."""

    has_event: bool
    title: str
    location: str | None
    raw_time_text: str | None
    proposed_date: str | None
    proposed_start: str | None
    proposed_end: str | None
    confidence: str
    needs_review: bool
    notes: tuple[str, ...]
    calendar_link: str | None
    preview_only: bool
    persisted: bool
    external_action_used: bool

    def to_dict(self) -> dict:
        """Return JSON-friendly extraction data."""
        return asdict(self)


def _base_date(base_date: str | date | None = None) -> date:
    if isinstance(base_date, date):
        return base_date
    if isinstance(base_date, str) and base_date.strip():
        return date.fromisoformat(base_date.strip())
    return date.fromisoformat(resolve_today())


def _next_weekday(base: date, target_weekday: int, force_next_week: bool = False) -> date:
    days_ahead = (target_weekday - base.weekday()) % 7
    if force_next_week:
        days_ahead += 7 if days_ahead == 0 else 7
    return base + timedelta(days=days_ahead)


def _parse_date(text: str, base: date) -> tuple[date | None, str | None, list[str]]:
    lowered = text.lower()
    notes: list[str] = []

    explicit = re.search(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", lowered)
    if explicit:
        day, month, year = (int(explicit.group(1)), int(explicit.group(2)), int(explicit.group(3)))
        return date(year, month, day), explicit.group(0), notes

    iso = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", lowered)
    if iso:
        return date.fromisoformat(iso.group(0)), iso.group(0), notes

    if "uebermorgen" in lowered or "übermorgen" in lowered:
        return base + timedelta(days=2), "uebermorgen", notes
    if "morgen" in lowered:
        return base + timedelta(days=1), "morgen", notes

    force_next_week = "naechste woche" in lowered or "nächste woche" in lowered
    for weekday_name, weekday_index in WEEKDAY_INDEX.items():
        if weekday_name in lowered:
            if force_next_week:
                notes.append("Wochentag wurde relativ zu naechster Woche deterministisch aufgeloest.")
            else:
                notes.append("Wochentag wurde relativ zum heutigen Datum deterministisch aufgeloest.")
            return _next_weekday(base, weekday_index, force_next_week), weekday_name, notes

    return None, None, notes


def _to_business_hour(hour: int) -> int:
    if 1 <= hour <= 7:
        return hour + 12
    return hour


def _parse_time(text: str) -> tuple[time | None, str | None, list[str]]:
    lowered = text.lower()
    notes: list[str] = []

    explicit = re.search(r"\b(?:um\s*)?(\d{1,2})(?::(\d{2})|\.(\d{2})(?!\.\d{2,4}))\b", lowered)
    if explicit:
        hour = _to_business_hour(int(explicit.group(1)))
        minute = int(explicit.group(2) or explicit.group(3))
        return time(hour=hour, minute=minute), explicit.group(0), notes

    half = re.search(r"\bhalb\s+(\d{1,2})\b", lowered)
    if half:
        target_hour = int(half.group(1))
        hour = target_hour - 1
        if hour <= 0:
            hour += 12
        hour = _to_business_hour(hour)
        notes.append("'halb X' wurde deutsch deterministisch als X-1:30 aufgeloest.")
        return time(hour=hour, minute=30), half.group(0), notes

    clock = re.search(r"\b(?:um\s*)?(\d{1,2})\s*uhr\b", lowered)
    if clock:
        hour = _to_business_hour(int(clock.group(1)))
        return time(hour=hour, minute=0), clock.group(0), notes

    return None, None, notes


def _extract_location(text: str) -> str | None:
    match = re.search(r"\b(?:bei|in|im|am)\s+([A-Za-zÄÖÜäöüß0-9 .-]{3,40})", text)
    if not match:
        return None
    return " ".join(match.group(1).strip(" .").split()) or None


def _build_title(text: str) -> str:
    cleaned = " ".join((text or "").strip().split())
    if not cleaned:
        return "Termin"
    if len(cleaned) <= 60:
        return cleaned
    return cleaned[:57].rstrip() + "..."


def build_calendar_link(
    *,
    title: str,
    date_iso: str,
    start_time: str,
    end_time: str,
    location: str | None = None,
) -> str:
    """Build a manual Google Calendar template link without writing an event."""
    start = f"{date_iso.replace('-', '')}T{start_time.replace(':', '')}00"
    end = f"{date_iso.replace('-', '')}T{end_time.replace(':', '')}00"
    parts = [
        "https://calendar.google.com/calendar/render?action=TEMPLATE",
        f"text={quote_plus(title)}",
        f"dates={start}/{end}",
        "details=Friday%20Kalender-Vorschlag%20-%20bitte%20vor%20dem%20Speichern%20pruefen",
    ]
    if location:
        parts.append(f"location={quote_plus(location)}")
    return "&".join(parts)


def extract_calendar_event_candidate(
    text: str,
    *,
    base_date: str | date | None = None,
    duration_minutes: int = 60,
) -> CalendarEventExtraction:
    """Extract one local calendar event candidate using deterministic Python rules."""
    clean_text = text or ""
    base = _base_date(base_date)
    parsed_date, raw_date, date_notes = _parse_date(clean_text, base)
    parsed_time, raw_time, time_notes = _parse_time(clean_text)
    notes = [*date_notes, *time_notes]

    if parsed_date is None or parsed_time is None:
        return CalendarEventExtraction(
            has_event=False,
            title="",
            location=None,
            raw_time_text=raw_date or raw_time,
            proposed_date=None,
            proposed_start=None,
            proposed_end=None,
            confidence="none",
            needs_review=True,
            notes=tuple(notes or ("Kein vollstaendiger Termin mit Datum und Uhrzeit erkannt.",)),
            calendar_link=None,
            preview_only=True,
            persisted=False,
            external_action_used=False,
        )

    start_dt = datetime.combine(parsed_date, parsed_time)
    end_dt = start_dt + timedelta(minutes=max(15, min(duration_minutes, 240)))
    title = _build_title(clean_text)
    location = _extract_location(clean_text)
    date_iso = parsed_date.isoformat()
    start_text = start_dt.strftime("%H:%M")
    end_text = end_dt.strftime("%H:%M")
    confidence = "high" if re.search(r"\d{1,2}\.\d{1,2}\.\d{4}", clean_text) else "medium"

    return CalendarEventExtraction(
        has_event=True,
        title=title,
        location=location,
        raw_time_text=" ".join(part for part in (raw_date, raw_time) if part) or None,
        proposed_date=date_iso,
        proposed_start=start_text,
        proposed_end=end_text,
        confidence=confidence,
        needs_review=True,
        notes=tuple(notes or ("Termin wurde lokal deterministisch erkannt.",)),
        calendar_link=build_calendar_link(
            title=title,
            date_iso=date_iso,
            start_time=start_text,
            end_time=end_text,
            location=location,
        ),
        preview_only=True,
        persisted=False,
        external_action_used=False,
    )


def render_calendar_event_review_text(extraction: CalendarEventExtraction) -> str:
    """Render one extraction as reviewable local draft text."""
    if not extraction.has_event:
        return "Kein vollstaendiger Termin erkannt."
    lines = [
        "Kalender-Vorschlag (lokal, bitte pruefen):",
        f"Titel: {extraction.title}",
        f"Datum: {extraction.proposed_date}",
        f"Zeit: {extraction.proposed_start} bis {extraction.proposed_end}",
    ]
    if extraction.location:
        lines.append(f"Ort: {extraction.location}")
    if extraction.raw_time_text:
        lines.append(f"Roh-Zeitangabe: {extraction.raw_time_text}")
    lines.append("Es wurde kein Kalendertermin erstellt.")
    if extraction.calendar_link:
        lines.append(f"Kalender-Link: {extraction.calendar_link}")
    return "\n".join(lines)
