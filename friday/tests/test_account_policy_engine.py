"""Tests for deterministic account-policy filtering and context."""

from __future__ import annotations

from friday.app.account_policy_engine import (
    apply_transforms,
    build_ai_context,
    filter_events,
    resolve_write_target,
)
from friday.app.account_policy_store import AccountPolicy


def _policy(
    *,
    provider: str = "outlook_graph",
    role: str = "source",
    access: str = "read",
    include_filters: dict | None = None,
    transform: dict | None = None,
    notes: str = "PH = Dienst = belegt. Alles andere ignorieren.",
    enabled: bool = True,
) -> AccountPolicy:
    return AccountPolicy(
        id=1,
        provider=provider,
        label="Arbeit Outlook PH",
        role=role,
        access=access,
        include_filters=include_filters or {},
        exclude_filters={},
        notes=notes,
        enabled=enabled,
        created_at="2026-07-09T00:00:00+00:00",
        transform=transform or {},
    )


def test_filter_events_keeps_only_title_allowlist_matches() -> None:
    policy = _policy(include_filters={"title_contains": ["PH"]})
    events = [
        {"title": "PH Dienst", "calendar_id": "work"},
        {"title": "Team Jour Fixe", "calendar_id": "work"},
        {"summary": "ph spaetdienst", "calendar_id": "work"},
    ]

    filtered = filter_events(events, policy)

    assert [item["title"] if "title" in item else item["summary"] for item in filtered] == [
        "PH Dienst",
        "ph spaetdienst",
    ]


def test_filter_events_ignores_disabled_policy() -> None:
    assert filter_events([{"title": "PH Dienst"}], _policy(enabled=False)) == []


def test_build_ai_context_uses_active_policy_notes() -> None:
    context = build_ai_context([_policy()])

    assert "Arbeit Outlook PH" in context
    assert "PH = Dienst = belegt" in context


def test_resolve_write_target_requires_exactly_one_main_read_write_policy() -> None:
    source = _policy()
    main = _policy(role="main", access="read_write")

    result = resolve_write_target([source, main])

    assert result.ok is True
    assert result.policy == main


def test_resolve_write_target_blocks_missing_main_policy() -> None:
    result = resolve_write_target([_policy()])

    assert result.ok is False
    assert result.blocked_reasons == ("main_policy_missing",)


def test_apply_transforms_sets_fixed_ph_day_window_for_outlook_ics_policy() -> None:
    policy = _policy(
        provider="outlook_ics",
        transform={"fixed_daily_window": {"start": "08:00", "end": "18:00"}},
    )
    events = [
        {
            "title": "PH Dienst",
            "start": "2026-07-15T00:00:00",
            "end": "2026-07-15T23:59:00",
        },
        {
            "title": "PH Dienst",
            "date": "2026-07-16",
        },
    ]

    transformed = apply_transforms(events, policy)

    assert transformed[0]["start"] == "2026-07-15T08:00:00"
    assert transformed[0]["end"] == "2026-07-15T18:00:00"
    assert transformed[1]["start"] == "2026-07-16T08:00:00"
    assert transformed[1]["end"] == "2026-07-16T18:00:00"
    assert transformed[0]["time_window_source"] == "policy_transform.fixed_daily_window"


def test_apply_transforms_is_per_policy_and_does_not_change_google_events() -> None:
    policy = _policy(
        provider="google_calendar",
        transform={"fixed_daily_window": {"start": "08:00", "end": "18:00"}},
    )
    event = {
        "title": "Privater Termin",
        "start": "2026-07-15T10:00:00",
        "end": "2026-07-15T11:00:00",
    }

    transformed = apply_transforms([event], policy)

    assert transformed == [event]
    assert transformed[0] is not event


def test_apply_transforms_ignores_invalid_fixed_window_without_crashing() -> None:
    policy = _policy(
        provider="outlook_ics",
        transform={"fixed_daily_window": {"start": "8 Uhr", "end": "18:00"}},
    )
    event = {"title": "PH Dienst", "start": "2026-07-15T00:00:00"}

    assert apply_transforms([event], policy) == [event]
