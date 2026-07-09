"""Local calendar view preference storage for Friday."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import re
from pathlib import Path
from typing import Any

from friday.storage.database import get_connection


VALID_RANGE_PRESETS = {"heute", "7tage", "30tage", "custom"}
DEFAULT_RANGE_PRESET = "heute"
DEFAULT_DAY_START = "00:00"
DEFAULT_DAY_END = "23:59"


@dataclass(frozen=True)
class CalendarViewPrefs:
    """Persisted local calendar view preferences."""

    range_preset: str = DEFAULT_RANGE_PRESET
    custom_from: str | None = None
    custom_to: str | None = None
    day_start: str = DEFAULT_DAY_START
    day_end: str = DEFAULT_DAY_END
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _normalize_preset(value: Any) -> str:
    preset = _clean(value).lower() or DEFAULT_RANGE_PRESET
    if preset not in VALID_RANGE_PRESETS:
        raise ValueError("Ungueltiger Kalender-Zeitraum.")
    return preset


def _normalize_date(value: Any) -> str | None:
    text = _clean(value)
    if not text:
        return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise ValueError("Datum muss im Format YYYY-MM-DD sein.")
    return text


def _normalize_time(value: Any, default: str) -> str:
    text = _clean(value) or default
    if not re.fullmatch(r"\d{2}:\d{2}", text):
        raise ValueError("Uhrzeit muss im Format HH:MM sein.")
    hour, minute = [int(part) for part in text.split(":", 1)]
    if hour > 23 or minute > 59:
        raise ValueError("Uhrzeit liegt ausserhalb des Tages.")
    return f"{hour:02d}:{minute:02d}"


def _row_to_prefs(row: Any) -> CalendarViewPrefs:
    return CalendarViewPrefs(
        range_preset=str(row["range_preset"] or DEFAULT_RANGE_PRESET),
        custom_from=row["custom_from"],
        custom_to=row["custom_to"],
        day_start=str(row["day_start"] or DEFAULT_DAY_START),
        day_end=str(row["day_end"] or DEFAULT_DAY_END),
        updated_at=row["updated_at"],
    )


def load_calendar_view_prefs(db_path: Path | str | None = None) -> CalendarViewPrefs:
    """Load the single local calendar view preference row."""
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT range_preset, custom_from, custom_to, day_start, day_end, updated_at
            FROM calendar_view_prefs
            WHERE id = 1
            """
        ).fetchone()
    if row is None:
        return CalendarViewPrefs(updated_at=None)
    return _row_to_prefs(row)


def save_calendar_view_prefs(
    *,
    range_preset: str,
    custom_from: str | None = None,
    custom_to: str | None = None,
    day_start: str | None = None,
    day_end: str | None = None,
    db_path: Path | str | None = None,
) -> CalendarViewPrefs:
    """Persist local calendar view preferences."""
    preset = _normalize_preset(range_preset)
    normalized_custom_from = _normalize_date(custom_from)
    normalized_custom_to = _normalize_date(custom_to)
    normalized_day_start = _normalize_time(day_start, DEFAULT_DAY_START)
    normalized_day_end = _normalize_time(day_end, DEFAULT_DAY_END)
    if preset == "custom" and (not normalized_custom_from or not normalized_custom_to):
        raise ValueError("Custom-Zeitraum braucht Start- und Enddatum.")
    updated_at = _now_iso()

    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO calendar_view_prefs
                (id, range_preset, custom_from, custom_to, day_start, day_end, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                range_preset = excluded.range_preset,
                custom_from = excluded.custom_from,
                custom_to = excluded.custom_to,
                day_start = excluded.day_start,
                day_end = excluded.day_end,
                updated_at = excluded.updated_at
            """,
            (
                preset,
                normalized_custom_from,
                normalized_custom_to,
                normalized_day_start,
                normalized_day_end,
                updated_at,
            ),
        )
    return load_calendar_view_prefs(db_path=db_path)
