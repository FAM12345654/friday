"""Deterministic wake-time calculation for Friday's local morning routine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, Iterable, Mapping

from friday import config


@dataclass(frozen=True)
class WakeTimeResult:
    """One explainable wake-time decision."""

    alarm_time: time
    reason: str
    first_appointment: dict[str, Any] | None
    is_workday: bool

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["alarm_time"] = self.alarm_time.isoformat(timespec="minutes")
        return payload


def _configured_time(value: Any, *, field_name: str) -> time:
    if isinstance(value, time):
        return value.replace(tzinfo=None)
    try:
        return time.fromisoformat(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"Ungueltige Morning-Routine-Zeit in {field_name}.") from exc


def _event_start(event: Mapping[str, Any], target_date: date) -> datetime | None:
    raw_start = event.get("start") or event.get("start_time")
    if not raw_start:
        return None

    text = str(raw_start).strip()
    if not text:
        return None

    if ":" not in text:
        # Ganztagstermine besitzen keine belastbare Weckzeit.
        return None

    if "T" in text or " " in text:
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.date() != target_date:
            return None
        return parsed

    try:
        parsed_time = time.fromisoformat(text)
    except ValueError:
        return None

    event_date = str(event.get("date") or target_date.isoformat())
    if event_date != target_date.isoformat():
        return None
    return datetime.combine(target_date, parsed_time)


def compute_wake_time(
    target_date: date,
    *,
    calendar_events: Iterable[Mapping[str, Any]] = (),
    calendar_failed: bool = False,
) -> WakeTimeResult:
    """Compute one wake time from the cached calendar-day payload.

    The API adapter supplies ``calendar_events`` from Friday's existing calendar
    TTL cache. Keeping the calculation pure makes fallback and edge cases fully
    testable without provider or network access.
    """

    if calendar_failed:
        fallback = _configured_time(config.fallback_alarm, field_name="fallback_alarm")
        return WakeTimeResult(
            alarm_time=fallback,
            reason="Kalender konnte nicht gelesen werden - Sicherheitsalarm um 07:00",
            first_appointment=None,
            is_workday=False,
        )

    cutoff = _configured_time(config.workday_cutoff, field_name="workday_cutoff")
    starts: list[tuple[datetime, dict[str, Any]]] = []
    for event in calendar_events:
        start = _event_start(event, target_date)
        if start is None or start.time().replace(tzinfo=None) >= cutoff:
            continue
        starts.append((start, dict(event)))

    if not starts:
        default_time = _configured_time(config.default_wake_time, field_name="default_wake_time")
        return WakeTimeResult(
            alarm_time=default_time,
            reason="Kein Termin vor 10:00 - Standardweckzeit um 08:00",
            first_appointment=None,
            is_workday=False,
        )

    first_start, first_appointment = min(starts, key=lambda item: item[0])
    buffer_minutes = int(config.prep_buffer_minutes)
    alarm_datetime = first_start - timedelta(minutes=buffer_minutes)
    appointment_time = first_start.time().replace(tzinfo=None).isoformat(timespec="minutes")
    return WakeTimeResult(
        alarm_time=alarm_datetime.time().replace(tzinfo=None),
        reason=f"Erster Termin um {appointment_time} - {buffer_minutes}min Vorbereitung",
        first_appointment=first_appointment,
        is_workday=True,
    )
