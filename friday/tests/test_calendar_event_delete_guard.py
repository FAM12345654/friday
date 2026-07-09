"""Tests for guarded real calendar event deletion."""

from __future__ import annotations

from friday.app.calendar_event_delete_guard import (
    CALENDAR_EVENT_DELETE_TOKEN,
    check_calendar_event_delete_allowed,
)


def test_calendar_event_delete_guard_requires_exact_token() -> None:
    result = check_calendar_event_delete_allowed(
        approval_token="JA",
        real_calendar_enabled=True,
        main_policy_ok=True,
        connection_ok=True,
    )

    assert result.allowed is False
    assert "approval_token_invalid" in result.blocked_reasons
    assert result.external_call_allowed is False


def test_calendar_event_delete_guard_allows_only_when_all_gates_pass() -> None:
    result = check_calendar_event_delete_allowed(
        approval_token=CALENDAR_EVENT_DELETE_TOKEN,
        real_calendar_enabled=True,
        main_policy_ok=True,
        connection_ok=True,
    )

    assert result.allowed is True
    assert result.blocked_reasons == ()
    assert result.external_call_allowed is True
