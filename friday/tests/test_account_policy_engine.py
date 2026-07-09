"""Tests for deterministic account-policy filtering and context."""

from __future__ import annotations

from friday.app.account_policy_engine import (
    build_ai_context,
    filter_events,
    resolve_write_target,
)
from friday.app.account_policy_store import AccountPolicy


def _policy(
    *,
    role: str = "source",
    access: str = "read",
    include_filters: dict | None = None,
    notes: str = "PH = Dienst = belegt. Alles andere ignorieren.",
    enabled: bool = True,
) -> AccountPolicy:
    return AccountPolicy(
        id=1,
        provider="outlook_graph",
        label="Arbeit Outlook PH",
        role=role,
        access=access,
        include_filters=include_filters or {},
        exclude_filters={},
        notes=notes,
        enabled=enabled,
        created_at="2026-07-09T00:00:00+00:00",
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

