"""Tests for deterministic and idempotent calendar source synchronization."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from friday.app.account_policy_store import AccountPolicy
from friday.app.calendar_provider_base import CalendarProviderEvent, CalendarProviderResult
from friday.app.calendar_source_sync import (
    build_google_sync_event_id,
    build_source_sync_plan,
)


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location("friday_api_main_for_source_sync_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source_event() -> dict:
    return {
        "id": "outlook-1",
        "provider": "outlook_ics",
        "policy_id": 7,
        "policy_label": "Arbeit",
        "title": "Dienst",
        "start": "2026-07-15T08:00:00+02:00",
        "end": "2026-07-15T18:00:00+02:00",
        "location": "Büro",
    }


def test_source_sync_event_id_is_stable_and_google_compatible() -> None:
    item = build_source_sync_plan([_source_event()], [])["create"][0]

    first = build_google_sync_event_id(item)
    second = build_google_sync_event_id(dict(item))

    assert first == second
    assert first.startswith("frd")
    assert 5 <= len(first) <= 1024
    assert set(first) <= set("0123456789abcdefghijklmnopqrstuv")


def test_existing_google_source_key_prevents_duplicate_create() -> None:
    first_plan = build_source_sync_plan([_source_event()], [])
    source_key = first_plan["create"][0]["source_key"]
    google_event = {
        "title": "Dienst",
        "start": "2026-07-15T08:00:00+02:00",
        "end": "2026-07-15T18:00:00+02:00",
        "raw": {
            "extendedProperties": {
                "private": {"fridaySourceKey": source_key},
            }
        },
    }

    second_plan = build_source_sync_plan([_source_event()], [google_event])

    assert second_plan["create"] == []
    assert second_plan["skipped"][0]["reason"] == "already_synced"


def test_source_sync_preview_approval_executes_exact_batch_once(monkeypatch) -> None:
    api = _load_api_module()
    main_policy = AccountPolicy(
        id=1,
        provider="google_calendar",
        label="Google Hauptkalender",
        role="main",
        access="read_write",
        include_filters={},
        exclude_filters={},
        notes="",
        enabled=True,
        created_at="2026-07-15T00:00:00+00:00",
    )
    source_policy = AccountPolicy(
        id=7,
        provider="outlook_ics",
        label="Arbeit",
        role="source",
        access="read",
        include_filters={},
        exclude_filters={},
        notes="",
        enabled=True,
        created_at="2026-07-15T00:00:00+00:00",
    )
    source_event = _source_event()
    created: list[CalendarProviderEvent] = []

    async def collect_sources(*_args, **_kwargs):
        return [source_event], []

    async def list_google(*_args, **_kwargs):
        return CalendarProviderResult(ok=True, events=(), message="leer")

    class _Provider:
        def create_event(self, event: CalendarProviderEvent):
            created.append(event)
            return CalendarProviderResult(
                ok=True,
                event=CalendarProviderEvent(
                    id=event.id,
                    provider="google_calendar",
                    calendar_id=event.calendar_id,
                    title=event.title,
                    start=event.start,
                    end=event.end,
                    location=event.location,
                    raw=event.raw,
                ),
                provider_event_id=event.id,
                message="erstellt",
                external_call_used=True,
            )

    monkeypatch.setattr(api, "list_account_policies", lambda: [main_policy, source_policy])
    monkeypatch.setattr(api, "_collect_source_calendar_events", collect_sources)
    monkeypatch.setattr(api, "_list_google_calendar_events_cached", list_google)
    monkeypatch.setattr(
        api,
        "google_calendar_account_status",
        lambda: {
            "connected": True,
            "calendar_id": "primary",
            "last_test_ok": True,
            "real_calendar_enabled": True,
        },
    )
    monkeypatch.setattr(api, "GoogleCalendarProvider", lambda: _Provider())
    monkeypatch.setattr(api.config, "ENABLE_REAL_CALENDAR", True, raising=False)
    client = TestClient(api.app)

    preview_response = client.post(
        "/api/calendar/source-sync",
        json={"dry_run": True, "days": 30},
    )
    preview = preview_response.json()["data"]
    assert preview_response.headers["cache-control"] == "no-store"
    assert preview["planned_count"] == 1
    assert preview["created_count"] == 0
    assert preview["approval"]["one_time"] is True
    assert created == []

    request_payload = {
        "dry_run": False,
        "days": 30,
        "approval_token": "TERMIN SPEICHERN",
        "approval_id": preview["approval"]["id"],
    }
    execution = client.post("/api/calendar/source-sync", json=request_payload).json()["data"]
    replay = client.post("/api/calendar/source-sync", json=request_payload).json()["data"]

    assert execution["created_count"] == 1
    assert len(created) == 1
    assert created[0].id == build_google_sync_event_id(
        build_source_sync_plan([source_event], [])["create"][0]
    )
    assert replay["created_count"] == 0
    assert replay["guard"]["blocked_reasons"] == ["one_time_approval_invalid"]
