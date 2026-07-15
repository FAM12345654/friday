"""Tests for setup status, deterministic calendar extraction and contact category API."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient
from friday.app.account_policy_store import AccountPolicy, AccountPolicyWriteResult
from friday.app.calendar_provider_base import CalendarProviderEvent, CalendarProviderResult
from friday.storage.database import setup_local_database
from friday.storage.repositories import CalendarRepository


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location(
        "friday_api_main_for_setup_calendar_contact_test",
        module_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_setup_status_endpoint_reports_local_only_safety_flags() -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    response = client.get("/api/setup/status")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["app_name"] == "Friday"
    assert payload["local_mode"] is True
    assert payload["safety_flags"]["ENABLE_REAL_EMAIL"] is False
    assert payload["safety_flags"]["ENABLE_REAL_WHATSAPP"] is False
    assert payload["safety_flags"]["ENABLE_REAL_CALENDAR"] is True
    assert payload["calendar"]["real_enabled"] is True
    assert payload["calendar"]["auto_write_enabled"] is False


def test_setup_status_aliases_and_account_summaries_are_public(monkeypatch) -> None:
    from friday.app import setup_status as status_module

    monkeypatch.setattr(
        status_module,
        "email_account_status",
        lambda: {"connected": True, "last_test_ok": True},
    )
    private_account = {
        "account_id": "masked-id",
        "username": "private@example.test",
        "tenant": "private-tenant",
        "client_id": "private-client",
        "last_test_ok": True,
    }
    monkeypatch.setattr(
        status_module,
        "ms_mail_account_status",
        lambda: {
            "connected": True,
            "account_count": 1,
            "accounts": [private_account],
            "last_test_ok": True,
        },
    )
    monkeypatch.setattr(
        status_module,
        "imap_mail_account_status",
        lambda: {
            "connected": True,
            "account_count": 1,
            "accounts": [private_account],
            "last_test_ok": True,
        },
    )
    monkeypatch.setattr(
        status_module,
        "get_whatsapp_bridge_status",
        lambda: {"read_enabled": True, "connected": True, "last_received_at": None},
    )
    monkeypatch.setattr(
        status_module,
        "google_calendar_account_status",
        lambda: {"connected": False},
    )
    monkeypatch.setattr(status_module, "list_account_policies", lambda: ())

    payload = status_module.build_setup_status()

    assert payload["email"]["configured"] is True
    assert payload["whatsapp"]["read_enabled"] is True
    for area in ("ms_mail", "imap_mail"):
        public_account = payload[area]["accounts"][0]
        assert public_account["account_id"] == "masked-id"
        assert "username" not in public_account
        assert "tenant" not in public_account
        assert "client_id" not in public_account


def test_privacy_endpoint_reflects_runtime_integration_flags(monkeypatch) -> None:
    api = _load_api_module()
    monkeypatch.setattr(api.config, "ENABLE_REAL_EMAIL", True)
    monkeypatch.setattr(api.config, "ENABLE_WHATSAPP_BRIDGE_READ", True)
    monkeypatch.setattr(api.config, "ENABLE_MAIL_ORGANIZE", True)

    payload = api.get_privacy()["data"]["external_services"]

    assert payload["email"] is True
    assert payload["whatsapp_bridge_read"] is True
    assert payload["mail_organize"] is True


def test_calendar_extract_event_endpoint_uses_review_only_preview() -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    response = client.post(
        "/api/calendar/extract-event",
        json={
            "text": "Termin am 15.07.2026 um 10:00 im Buero",
            "base_date": "2026-07-09",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["calendar_write_enabled"] is False
    assert payload["review_required"] is True
    assert payload["extraction"]["has_event"] is True
    assert payload["extraction"]["proposed_date"] == "2026-07-15"
    assert payload["extraction"]["proposed_start"] == "10:00"
    assert payload["extraction"]["external_action_used"] is False


def test_contact_category_preview_endpoint_is_local_preview_only() -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    response = client.post(
        "/api/contacts/category-preview",
        json={
            "display_name": "Max",
            "context_text": "Kollege aus dem Projekt",
            "model_raw_category": "arbeit",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["category"] == "arbeit"
    assert payload["preview_only"] is True
    assert payload["persisted"] is False
    assert payload["external_lookup_used"] is False


def test_account_policies_endpoint_returns_policy_context(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    policy = AccountPolicy(
        id=1,
        provider="outlook_graph",
        label="Arbeit Outlook PH",
        role="source",
        access="read",
        include_filters={"title_contains": ["PH"]},
        exclude_filters={},
        notes="PH = Dienst = belegt.",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )
    monkeypatch.setattr(api, "list_account_policies", lambda: [policy])

    response = client.get("/api/accounts/policies")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["count"] == 1
    assert "PH = Dienst = belegt" in payload["ai_context"]


def test_account_policy_create_endpoint_accepts_per_policy_transform(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    captured: dict = {}

    def _create_account_policy(**kwargs):
        captured.update(kwargs)
        policy = AccountPolicy(
            id=7,
            provider=kwargs["provider"],
            label=kwargs["label"],
            role=kwargs["role"],
            access=kwargs["access"],
            include_filters=kwargs["include_filters"],
            exclude_filters=kwargs["exclude_filters"],
            transform=kwargs["transform"],
            notes=kwargs["notes"],
            enabled=kwargs["enabled"],
            created_at="2026-07-09T00:00:00+00:00",
        )
        return AccountPolicyWriteResult(
            allowed=True,
            persisted=True,
            message="Policy wurde lokal gespeichert.",
            blocked_reasons=(),
            policy=policy,
        )

    monkeypatch.setattr(api, "create_account_policy", _create_account_policy)

    response = client.post(
        "/api/accounts/policies",
        json={
            "provider": "outlook_ics",
            "label": "team-hampejs PH",
            "role": "source",
            "access": "read",
            "include_filters": {"title_contains": ["PH"]},
            "exclude_filters": {},
            "transform": {"fixed_daily_window": {"start": "08:00", "end": "18:00"}},
            "notes": "PH als Tagesblock",
            "enabled": True,
            "approval_token": "POLICY SPEICHERN",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert captured["transform"] == {"fixed_daily_window": {"start": "08:00", "end": "18:00"}}
    assert payload["policy"]["transform"]["fixed_daily_window"]["start"] == "08:00"


def test_contact_patch_endpoint_updates_local_agent_notes(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    captured: dict = {}

    class _ContactAgent:
        def update_contact(self, contact_id: int, **values):
            captured["contact_id"] = contact_id
            captured["values"] = values
            return {"id": contact_id, "name": "Max", **values}

    monkeypatch.setattr(api, "contact_agent", _ContactAgent())

    response = client.patch(
        "/api/contacts/5",
        json={"notes": "Mag kurze Nachrichten.", "contact_type": "kunde", "betreuer": "philip"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert captured["contact_id"] == 5
    assert captured["values"]["notes"] == "Mag kurze Nachrichten."
    assert captured["values"]["betreuer"] == "philip"
    assert payload["notes"] == "Mag kurze Nachrichten."
    assert payload["betreuer"] == "philip"


def test_email_agent_notes_endpoint_uses_local_store(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    class _Result:
        persisted = True
        message = "E-Mail-Agent-Notiz wurde lokal gespeichert."

    monkeypatch.setattr(api, "save_email_account_agent_notes", lambda notes: _Result())
    monkeypatch.setattr(
        api,
        "email_account_status",
        lambda: {"connected": True, "agent_notes": "Kurz.", "agent_notes_configured": True},
    )

    response = client.patch(
        "/api/accounts/email/notes",
        json={"agent_notes": "Kurz."},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["saved"] is True
    assert payload["status"]["agent_notes_configured"] is True


def test_whatsapp_agent_notes_endpoint_roundtrips_local_notes(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    monkeypatch.setattr(
        api,
        "load_whatsapp_agent_notes",
        lambda: {"agent_notes": "Locker.", "agent_notes_configured": True},
    )
    monkeypatch.setattr(
        api,
        "save_whatsapp_agent_notes",
        lambda notes: {"agent_notes": notes, "agent_notes_configured": bool(notes)},
    )

    get_response = client.get("/api/whatsapp/notes")
    put_response = client.put("/api/whatsapp/notes", json={"agent_notes": "Locker."})

    assert get_response.status_code == 200
    assert get_response.json()["data"]["agent_notes"] == "Locker."
    assert put_response.status_code == 200
    assert put_response.json()["data"]["agent_notes_configured"] is True


def test_calendar_activation_gate_endpoint_blocks_without_account(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    monkeypatch.setattr(
        api,
        "google_calendar_account_status",
        lambda: {
            "connected": False,
            "calendar_id": None,
            "last_test_ok": False,
            "real_calendar_enabled": False,
        },
    )

    response = client.post(
        "/api/accounts/calendar/activation-gate",
        json={"approval_token": "KALENDER AKTIVIEREN", "scanner_smoke_passed": True},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["allowed"] is False
    assert "calendar_account_missing" in payload["blocked_reasons"]


def test_google_calendar_connect_endpoint_requires_exact_token(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    def _must_not_exchange(**_kwargs):
        raise AssertionError("OAuth exchange must not run without hard approval token.")

    monkeypatch.setattr(api, "exchange_google_oauth_authorization_response", _must_not_exchange)

    response = client.post(
        "/api/accounts/calendar/google/connect",
        json={
            "client_secrets_path": "client.json",
            "authorization_response": "http://localhost/?code=abc",
            "approval_token": "JA",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["allowed"] is False
    assert payload["persisted"] is False
    assert payload["external_call_used"] is False
    assert "approval_token_invalid" in payload["blocked_reasons"]


def test_google_calendar_connect_endpoint_does_not_return_credentials(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    class _ExchangeResult:
        ok = True
        credentials_json = '{"token": "fake-token", "client_secret": "hidden"}'
        message = "ok"
        blocked_reasons = ()
        external_call_used = True

    monkeypatch.setattr(
        api,
        "exchange_google_oauth_authorization_response",
        lambda **_kwargs: _ExchangeResult(),
    )
    canonical_path = str(Path("client.json").resolve())
    monkeypatch.setattr(
        api.oauth_transactions,
        "consume",
        lambda **kwargs: SimpleNamespace(
            state=kwargs["state"],
            context={
                "client_secrets_path": canonical_path,
                "code_verifier": "pkce-code-verifier-with-at-least-forty-three-characters-123456",
            },
        ),
    )
    monkeypatch.setattr(
        api,
        "save_google_calendar_account",
        lambda account, *, approval_token: {
            "allowed": True,
            "persisted": True,
            "message": "stored",
            "blocked_reasons": (),
        },
    )

    response = client.post(
        "/api/accounts/calendar/google/connect",
        json={
            "client_secrets_path": "client.json",
            "authorization_response": "http://localhost/?code=abc&state=secure-state-value",
            "approval_token": "KALENDER VERBINDEN",
            "calendar_id": "primary",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["allowed"] is True
    assert payload["persisted"] is True
    assert payload["connected"] is True
    assert payload["real_calendar_enabled"] is True
    assert "credentials" not in payload
    assert "fake-token" not in response.text
    assert "hidden" not in response.text


def test_google_calendar_read_preview_blocks_without_connected_account(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    monkeypatch.setattr(
        api,
        "google_calendar_account_status",
        lambda: {
            "connected": False,
            "calendar_id": None,
            "last_test_ok": False,
            "real_calendar_enabled": False,
        },
    )

    response = client.get(
        "/api/accounts/calendar/google/read-preview",
        params={
            "range_start": "2026-07-15T00:00:00+02:00",
            "range_end": "2026-07-16T00:00:00+02:00",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["ok"] is False
    assert payload["read_only"] is True
    assert payload["write_enabled"] is False
    assert payload["real_calendar_enabled"] is True
    assert payload["external_call_used"] is False
    assert "calendar_account_missing" in payload["blocked_reasons"]


def test_google_calendar_read_preview_returns_events_without_enabling_writes(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    monkeypatch.setattr(
        api,
        "google_calendar_account_status",
        lambda: {
            "connected": True,
            "calendar_id": "primary",
            "last_test_ok": True,
            "real_calendar_enabled": False,
        },
    )

    class _Result:
        ok = True
        events = (
            CalendarProviderEvent(
                id="event-1",
                provider="google_calendar",
                calendar_id="primary",
                title="PH Dienst",
                start="2026-07-15T10:00:00+02:00",
                end="2026-07-15T11:00:00+02:00",
                location="Buero",
                raw={},
            ),
        )
        message = "Google-Kalender-Events gelesen."
        blocked_reasons = ()
        external_call_used = True

    class _Provider:
        def list_events(self, *, range_start: str, range_end: str):
            assert range_start == "2026-07-15T00:00:00+02:00"
            assert range_end == "2026-07-16T00:00:00+02:00"
            return _Result()

    monkeypatch.setattr(api, "GoogleCalendarProvider", lambda: _Provider())

    response = client.get(
        "/api/accounts/calendar/google/read-preview",
        params={
            "range_start": "2026-07-15T00:00:00+02:00",
            "range_end": "2026-07-16T00:00:00+02:00",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["ok"] is True
    assert payload["read_only"] is True
    assert payload["write_enabled"] is False
    assert payload["real_calendar_enabled"] is True
    assert payload["external_call_used"] is True
    assert payload["events"][0]["title"] == "PH Dienst"


def test_calendar_event_write_guard_endpoint_creates_one_mocked_google_event_and_local_entry(
    tmp_path,
    monkeypatch,
) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path)
    api.calendar_agent.calendar_repository = CalendarRepository(db_path)
    policy = AccountPolicy(
        id=1,
        provider="google_calendar",
        label="Google Hauptkalender",
        role="main",
        access="read_write",
        include_filters={},
        exclude_filters={},
        notes="",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )
    created_events: list[CalendarProviderEvent] = []
    account_status = {
        "connected": True,
        "calendar_id": "primary",
        "account_fingerprint": "account-a",
        "last_test_ok": True,
        "real_calendar_enabled": True,
    }
    monkeypatch.setattr(api, "list_account_policies", lambda: [policy])
    monkeypatch.setattr(
        api,
        "google_calendar_account_status",
        lambda: dict(account_status),
    )

    class _CreateResult:
        ok = True
        event = CalendarProviderEvent(
            id="created-1",
            provider="google_calendar",
            calendar_id="primary",
            title="Termin",
            start="2026-07-15T10:00:00+02:00",
            end="2026-07-15T11:00:00+02:00",
            location="Buero",
            raw={},
        )
        message = "Google-Kalendertermin erstellt."
        blocked_reasons = ()
        provider_event_id = "created-1"
        external_call_used = True

    class _Provider:
        def create_event(self, event: CalendarProviderEvent):
            created_events.append(event)
            return _CreateResult()

    monkeypatch.setattr(api, "GoogleCalendarProvider", lambda: _Provider())

    request_payload = {
        "approval_token": "TERMIN SPEICHERN",
        "title": "Termin",
        "start": "2026-07-15T10:00:00+02:00",
        "end": "2026-07-15T11:00:00+02:00",
        "location": "Buero",
    }
    preview_response = client.post(
        "/api/calendar/events/write-guard",
        json=request_payload,
    )
    preview = preview_response.json()["data"]
    assert preview["guard"]["allowed"] is False
    assert preview["guard"]["blocked_reasons"] == ["one_time_approval_required"]
    assert preview["provider_event_created"] is False
    assert created_events == []

    account_status["account_fingerprint"] = "account-b"
    stale_response = client.post(
        "/api/calendar/events/write-guard",
        json={**request_payload, "approval_id": preview["approval"]["id"]},
    )
    assert stale_response.json()["data"]["guard"]["blocked_reasons"] == [
        "one_time_approval_invalid"
    ]
    assert created_events == []

    refreshed_preview = client.post(
        "/api/calendar/events/write-guard",
        json=request_payload,
    ).json()["data"]
    second_preview = client.post(
        "/api/calendar/events/write-guard",
        json=request_payload,
    ).json()["data"]
    response = client.post(
        "/api/calendar/events/write-guard",
        json={**request_payload, "approval_id": refreshed_preview["approval"]["id"]},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["guard"]["allowed"] is True
    assert payload["provider_event_created"] is True
    assert payload["provider_result"]["provider_event_id"] == "created-1"
    assert payload["calendar_entry"]["provider"] == "google_calendar"
    assert payload["calendar_entry"]["provider_event_id"] == "created-1"
    assert payload["calendar_entry"]["policy_id"] == 1
    assert len(created_events) == 1

    duplicate_execution = client.post(
        "/api/calendar/events/write-guard",
        json={**request_payload, "approval_id": second_preview["approval"]["id"]},
    ).json()["data"]
    assert duplicate_execution["guard"]["blocked_reasons"] == [
        "one_time_approval_invalid"
    ]
    assert len(created_events) == 1


def test_calendar_event_write_guard_endpoint_does_not_call_provider_when_blocked(
    monkeypatch,
) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    policy = AccountPolicy(
        id=1,
        provider="google_calendar",
        label="Google Hauptkalender",
        role="main",
        access="read_write",
        include_filters={},
        exclude_filters={},
        notes="",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )
    monkeypatch.setattr(api, "list_account_policies", lambda: [policy])
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

    class _Provider:
        def create_event(self, event: CalendarProviderEvent):
            raise AssertionError("Provider must not be called when the hard token is wrong.")

    monkeypatch.setattr(api, "GoogleCalendarProvider", lambda: _Provider())

    response = client.post(
        "/api/calendar/events/write-guard",
        json={
            "approval_token": "JA",
            "title": "Termin",
            "start": "2026-07-15T10:00:00+02:00",
            "end": "2026-07-15T11:00:00+02:00",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["guard"]["allowed"] is False
    assert payload["provider_event_created"] is False
    assert payload["provider_result"] is None
    assert "approval_token_invalid" in payload["guard"]["blocked_reasons"]


def test_outlook_ics_policy_create_stores_secret_without_returning_url(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    policy = AccountPolicy(
        id=8,
        provider="outlook_ics",
        label="Outlook PH",
        role="source",
        access="read",
        include_filters={"title_contains": ["PH"]},
        exclude_filters={},
        transform={"fixed_daily_window": {"start": "08:00", "end": "18:00"}},
        notes="PH nur als Quelle.",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )

    monkeypatch.setattr(
        api,
        "create_account_policy",
        lambda **_kwargs: AccountPolicyWriteResult(
            allowed=True,
            persisted=True,
            message="Policy wurde lokal gespeichert.",
            blocked_reasons=(),
            policy=policy,
        ),
    )
    monkeypatch.setattr(api, "build_outlook_ics_account", lambda **kwargs: kwargs)
    monkeypatch.setattr(
        api,
        "save_outlook_ics_account",
        lambda _account, approval_token: {
            "allowed": True,
            "persisted": approval_token == "POLICY SPEICHERN",
            "message": "Outlook-ICS-Quelle wurde lokal verschluesselt gespeichert.",
            "blocked_reasons": (),
        },
    )
    monkeypatch.setattr(
        api,
        "outlook_ics_account_status",
        lambda policy_id: {
            "connected": True,
            "policy_id": policy_id,
            "provider": "outlook_ics",
        },
    )

    response = client.post(
        "/api/accounts/policies",
        json={
            "provider": "outlook_ics",
            "label": "Outlook PH",
            "role": "source",
            "access": "read",
            "include_filters": {"title_contains": ["PH"]},
            "notes": "PH nur als Quelle.",
            "approval_token": "POLICY SPEICHERN",
            "ics_url": "https://example.invalid/private.ics",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["ics_account_saved"] is True
    assert payload["ics_account_status"]["connected"] is True
    assert "example.invalid" not in str(payload)


def test_calendar_endpoint_merges_and_filters_outlook_ics_source(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    policy = AccountPolicy(
        id=8,
        provider="outlook_ics",
        label="Outlook PH",
        role="source",
        access="read",
        include_filters={"title_contains": ["PH"]},
        exclude_filters={},
        transform={"fixed_daily_window": {"start": "08:00", "end": "18:00"}},
        notes="PH nur als Quelle.",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )
    monkeypatch.setattr(api, "list_account_policies", lambda: [policy])

    class _Provider:
        def __init__(self, policy_id):
            self.policy_id = policy_id

        def list_events(self, *, range_start: str, range_end: str):
            return CalendarProviderResult(
                ok=True,
                events=(
                    CalendarProviderEvent(
                        id="ph-1",
                        provider="outlook_ics",
                        calendar_id="outlook_ics",
                        title="PH Dienst",
                        start="2026-07-15T08:00:00+00:00",
                        end="2026-07-15T12:00:00+00:00",
                    ),
                    CalendarProviderEvent(
                        id="private-1",
                        provider="outlook_ics",
                        calendar_id="outlook_ics",
                        title="Privat",
                        start="2026-07-15T13:00:00+00:00",
                        end="2026-07-15T14:00:00+00:00",
                    ),
                ),
            )

    monkeypatch.setattr(api, "OutlookIcsCalendarProvider", _Provider)

    response = client.get("/api/calendar?date=2026-07-15")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert [item["title"] for item in payload["source_events"]] == ["PH Dienst"]
    assert payload["source_events"][0]["start"] == "2026-07-15T08:00:00"
    assert payload["source_events"][0]["end"] == "2026-07-15T18:00:00"
    assert payload["source_events"][0]["time_window_source"] == "policy_transform.fixed_daily_window"
    assert payload["source_errors"] == []
    assert "PH nur als Quelle." in payload["policy_context"]


def test_calendar_endpoint_merges_google_main_and_outlook_source_over_range(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    google_policy = AccountPolicy(
        id=1,
        provider="google_calendar",
        label="Google Hauptkalender",
        role="main",
        access="read_write",
        include_filters={},
        exclude_filters={},
        transform={},
        notes="Hauptkalender.",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )
    outlook_policy = AccountPolicy(
        id=2,
        provider="outlook_ics",
        label="team-hampejs PH",
        role="source",
        access="read",
        include_filters={"title_contains": ["PH"]},
        exclude_filters={},
        transform={"fixed_daily_window": {"start": "08:00", "end": "18:00"}},
        notes="PH nur als Quelle.",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )
    monkeypatch.setattr(api, "list_account_policies", lambda: [google_policy, outlook_policy])

    class _CalendarAgent:
        def get_items_for_date(self, date_iso: str):
            return []

        def get_free_slots_for_date(self, date_iso: str):
            return [{"start": "09:00", "end": "10:00"}]

    class _GoogleProvider:
        def list_events(self, *, range_start: str, range_end: str):
            return CalendarProviderResult(
                ok=True,
                events=(
                    CalendarProviderEvent(
                        id="google-1",
                        provider="google_calendar",
                        calendar_id="primary",
                        title="Google Termin",
                        start="2026-07-15T10:00:00+02:00",
                        end="2026-07-15T11:00:00+02:00",
                    ),
                ),
            )

    class _OutlookProvider:
        def __init__(self, policy_id):
            self.policy_id = policy_id

        def list_events(self, *, range_start: str, range_end: str):
            return CalendarProviderResult(
                ok=True,
                events=(
                    CalendarProviderEvent(
                        id="ph-1",
                        provider="outlook_ics",
                        calendar_id="team-hampejs",
                        title="PH+D Dienst",
                        start="2026-07-16T00:00:00",
                        end="2026-07-16T23:59:00",
                    ),
                    CalendarProviderEvent(
                        id="philip-1",
                        provider="outlook_ics",
                        calendar_id="team-hampejs",
                        title="Philip Frei",
                        start="2026-07-16T09:00:00",
                        end="2026-07-16T10:00:00",
                    ),
                ),
            )

    monkeypatch.setattr(api, "calendar_agent", _CalendarAgent())
    monkeypatch.setattr(api, "GoogleCalendarProvider", lambda: _GoogleProvider())
    monkeypatch.setattr(api, "OutlookIcsCalendarProvider", _OutlookProvider)

    response = client.get(
        "/api/calendar",
        params={
            "range_start": "2026-07-15",
            "range_end": "2026-07-16",
            "day_start": "08:00",
            "day_end": "18:00",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    titles = [item["title"] for item in payload["merged_items"]]
    assert titles == ["Google Termin", "PH+D Dienst"]
    assert "Philip Frei" not in titles
    ph_event = next(item for item in payload["source_events"] if item["title"] == "PH+D Dienst")
    assert ph_event["policy_label"] == "team-hampejs PH"
    assert ph_event["start"] == "2026-07-16T08:00:00"
    assert payload["range_start"] == "2026-07-15"
    assert payload["range_end"] == "2026-07-16"
    assert payload["day_start"] == "08:00"
    assert payload["day_end"] == "18:00"


def test_calendar_endpoint_filters_merged_items_by_day_time_window(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    policy = AccountPolicy(
        id=1,
        provider="google_calendar",
        label="Google Hauptkalender",
        role="main",
        access="read_write",
        include_filters={},
        exclude_filters={},
        transform={},
        notes="",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )
    monkeypatch.setattr(api, "list_account_policies", lambda: [policy])

    class _CalendarAgent:
        def get_items_for_date(self, date_iso: str):
            return [
                {
                    "id": 1,
                    "title": "Lokaler Termin",
                    "start": "09:00",
                    "end": "10:00",
                    "item_type": "busy",
                    "date": date_iso,
                }
            ]

        def get_free_slots_for_date(self, date_iso: str):
            return [
                {"start": "06:00", "end": "07:00"},
                {"start": "11:00", "end": "12:00"},
            ]

    class _GoogleProvider:
        def list_events(self, *, range_start: str, range_end: str):
            return CalendarProviderResult(
                ok=True,
                events=(
                    CalendarProviderEvent(
                        id="early",
                        provider="google_calendar",
                        calendar_id="primary",
                        title="Zu frueh",
                        start="2026-07-15T05:00:00+02:00",
                        end="2026-07-15T06:00:00+02:00",
                    ),
                    CalendarProviderEvent(
                        id="inside",
                        provider="google_calendar",
                        calendar_id="primary",
                        title="Im Fenster",
                        start="2026-07-15T10:00:00+02:00",
                        end="2026-07-15T11:00:00+02:00",
                    ),
                ),
            )

    monkeypatch.setattr(api, "calendar_agent", _CalendarAgent())
    monkeypatch.setattr(api, "GoogleCalendarProvider", lambda: _GoogleProvider())

    response = client.get(
        "/api/calendar",
        params={
            "date": "2026-07-15",
            "day_start": "08:00",
            "day_end": "12:00",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert [item["title"] for item in payload["merged_items"]] == [
        "Lokaler Termin",
        "Im Fenster",
    ]
    assert payload["free_slots"] == [{"start": "11:00", "end": "12:00", "date": "2026-07-15"}]


def test_calendar_from_message_endpoint_writes_edited_suggestion_with_guard(
    tmp_path,
    monkeypatch,
) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path)
    api.calendar_agent.calendar_repository = CalendarRepository(db_path)
    policy = AccountPolicy(
        id=1,
        provider="google_calendar",
        label="Google Hauptkalender",
        role="main",
        access="read_write",
        include_filters={},
        exclude_filters={},
        notes="",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )
    created_events: list[CalendarProviderEvent] = []
    monkeypatch.setattr(api, "list_account_policies", lambda: [policy])
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

    class _Provider:
        def create_event(self, event: CalendarProviderEvent):
            created_events.append(event)
            return CalendarProviderResult(
                ok=True,
                event=CalendarProviderEvent(
                    id="created-from-message",
                    provider="google_calendar",
                    calendar_id="primary",
                    title=event.title,
                    start=event.start,
                    end=event.end,
                    location=event.location,
                ),
                message="Google-Kalendertermin erstellt.",
                provider_event_id="created-from-message",
                external_call_used=True,
            )

    monkeypatch.setattr(api, "GoogleCalendarProvider", lambda: _Provider())

    request_payload = {
        "approval_token": "TERMIN SPEICHERN",
        "text": "Termin am 15.07.2026 um 10:00 im Buero",
        "base_date": "2026-07-09",
        "title": "Editierter Termin",
        "date": "2026-07-15",
        "start": "11:30",
        "end": "12:30",
        "location": "Raum 1",
    }
    preview_response = client.post(
        "/api/calendar/events/from-message",
        json=request_payload,
    )
    preview = preview_response.json()["data"]
    assert preview["provider_event_created"] is False
    assert preview["approval"]["one_time"] is True

    response = client.post(
        "/api/calendar/events/from-message",
        json={**request_payload, "approval_id": preview["approval"]["id"]},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["provider_event_created"] is True
    assert payload["calendar_entry"]["provider_event_id"] == "created-from-message"
    assert created_events[0].title == "Editierter Termin"
    assert created_events[0].start == "2026-07-15T11:30:00+02:00"
    assert created_events[0].location == "Raum 1"


def test_calendar_delete_guard_endpoint_deletes_provider_and_local_entry(
    tmp_path,
    monkeypatch,
) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path)
    repository = CalendarRepository(db_path)
    api.calendar_agent.calendar_repository = repository
    repository.record_calendar_entry(
        provider="google_calendar",
        provider_event_id="created-1",
        policy_id=1,
        title="Termin",
        start="2026-07-15T10:00:00+02:00",
        end="2026-07-15T11:00:00+02:00",
    )
    policy = AccountPolicy(
        id=1,
        provider="google_calendar",
        label="Google Hauptkalender",
        role="main",
        access="read_write",
        include_filters={},
        exclude_filters={},
        notes="",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )
    deleted: list[str] = []
    monkeypatch.setattr(api, "list_account_policies", lambda: [policy])
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

    revision = ['"revision-1"']

    class _Provider:
        def get_event(self, *, event_id: str, calendar_id: str):
            return CalendarProviderResult(
                ok=True,
                event=CalendarProviderEvent(
                    id=event_id,
                    provider="google_calendar",
                    calendar_id=calendar_id,
                    title="Termin",
                    start="2026-07-15T10:00:00+02:00",
                    end="2026-07-15T11:00:00+02:00",
                    raw={"etag": revision[0]},
                ),
                message="Google-Kalendertermin gelesen.",
                provider_event_id=event_id,
                external_call_used=True,
            )

        def delete_event(self, *, event_id: str, calendar_id: str):
            deleted.append(f"{calendar_id}:{event_id}")
            return CalendarProviderResult(
                ok=True,
                message="Google-Kalendertermin geloescht.",
                provider_event_id=event_id,
                external_call_used=True,
            )

    monkeypatch.setattr(api, "GoogleCalendarProvider", lambda: _Provider())

    foreign_target_response = client.post(
        "/api/calendar/events/delete-guard",
        json={
            "approval_token": "TERMIN LOESCHEN",
            "provider_event_id": "created-1",
            "calendar_id": "secondary-calendar",
        },
    )
    assert foreign_target_response.json()["data"]["guard"]["blocked_reasons"] == [
        "calendar_target_not_main"
    ]

    request_payload = {
        "approval_token": "TERMIN LOESCHEN",
        "provider_event_id": "created-1",
        "calendar_id": "primary",
    }
    preview_response = client.post(
        "/api/calendar/events/delete-guard",
        json=request_payload,
    )
    preview = preview_response.json()["data"]
    assert preview["provider_event_deleted"] is False
    assert preview["approval"]["payload_bound"] is True
    assert preview["event_preview"]["etag"] == '"revision-1"'
    assert deleted == []

    revision[0] = '"revision-2"'
    stale_response = client.post(
        "/api/calendar/events/delete-guard",
        json={**request_payload, "approval_id": preview["approval"]["id"]},
    )
    assert stale_response.json()["data"]["guard"]["blocked_reasons"] == [
        "one_time_approval_invalid"
    ]
    assert deleted == []

    refreshed_preview = client.post(
        "/api/calendar/events/delete-guard",
        json=request_payload,
    ).json()["data"]
    response = client.post(
        "/api/calendar/events/delete-guard",
        json={**request_payload, "approval_id": refreshed_preview["approval"]["id"]},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["guard"]["allowed"] is True
    assert payload["provider_event_deleted"] is True
    assert payload["calendar_entry_deleted"]["provider_event_id"] == "created-1"
    assert repository.get_calendar_entry_by_provider_event_id(
        provider="google_calendar",
        provider_event_id="created-1",
    ) is None
    assert deleted == ["primary:created-1"]


def test_calendar_delete_guard_endpoint_does_not_call_provider_when_blocked(
    monkeypatch,
) -> None:
    api = _load_api_module()
    client = TestClient(api.app)
    policy = AccountPolicy(
        id=1,
        provider="google_calendar",
        label="Google Hauptkalender",
        role="main",
        access="read_write",
        include_filters={},
        exclude_filters={},
        notes="",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
    )
    monkeypatch.setattr(api, "list_account_policies", lambda: [policy])
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

    class _Provider:
        def delete_event(self, *, event_id: str, calendar_id: str):
            raise AssertionError("Provider must not be called when the hard token is wrong.")

    monkeypatch.setattr(api, "GoogleCalendarProvider", lambda: _Provider())

    response = client.post(
        "/api/calendar/events/delete-guard",
        json={
            "approval_token": "JA",
            "provider_event_id": "created-1",
            "calendar_id": "primary",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["guard"]["allowed"] is False
    assert payload["provider_event_deleted"] is False
    assert payload["provider_result"] is None
    assert "approval_token_invalid" in payload["guard"]["blocked_reasons"]
