"""Guard for writing one real calendar event."""

from __future__ import annotations

from dataclasses import asdict, dataclass


CALENDAR_EVENT_SAVE_TOKEN = "TERMIN SPEICHERN"


@dataclass(frozen=True)
class CalendarEventWriteGuard:
    """Decision for one calendar event write."""

    allowed: bool
    message: str
    blocked_reasons: tuple[str, ...]
    preview_only: bool
    external_call_allowed: bool

    def to_dict(self) -> dict:
        return asdict(self)


def check_calendar_event_write_allowed(
    *,
    approval_token: str,
    real_calendar_enabled: bool,
    main_policy_ok: bool,
    connection_ok: bool,
) -> CalendarEventWriteGuard:
    """Check all hard gates before a real calendar event write."""
    blocked: list[str] = []
    if approval_token != CALENDAR_EVENT_SAVE_TOKEN:
        blocked.append("approval_token_invalid")
    if not real_calendar_enabled:
        blocked.append("real_calendar_disabled")
    if not main_policy_ok:
        blocked.append("main_policy_missing")
    if not connection_ok:
        blocked.append("calendar_connection_not_ok")
    if blocked:
        return CalendarEventWriteGuard(
            allowed=False,
            message="Kalendertermin wurde nicht erstellt.",
            blocked_reasons=tuple(blocked),
            preview_only=True,
            external_call_allowed=False,
        )
    return CalendarEventWriteGuard(
        allowed=True,
        message="Kalendertermin darf nach Nutzerfreigabe erstellt werden.",
        blocked_reasons=(),
        preview_only=False,
        external_call_allowed=True,
    )
