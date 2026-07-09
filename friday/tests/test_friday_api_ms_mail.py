"""Tests for Microsoft Graph read-only mail API endpoints."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from friday.agents.message_agent import MessageAgent
from friday.app.ms_mail_provider import MsMailProviderResult
from friday.storage.database import setup_local_database
from friday.storage.repositories import MsMailMessageRepository


def _load_api_module():
    module_path = Path(__file__).resolve().parents[2] / "friday-api" / "main.py"
    spec = importlib.util.spec_from_file_location("friday_api_main_ms_mail_test", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_ms_mail_status_is_token_free(monkeypatch) -> None:
    api = _load_api_module()
    monkeypatch.setattr(
        api,
        "ms_mail_account_status",
        lambda: {
            "connected": True,
            "username_masked": "m***@familienhelden.at",
            "read_enabled": False,
            "real_email_enabled": False,
        },
    )

    response = api.get_ms_mail_status()

    assert response["ok"] is True
    assert response["data"]["connected"] is True
    assert "token" not in response["data"]


def test_ms_mail_connect_without_callback_returns_auth_url(monkeypatch) -> None:
    api = _load_api_module()
    monkeypatch.setattr(
        api,
        "build_ms_mail_authorization_url",
        lambda **_kwargs: MsMailProviderResult(
            ok=True,
            message="ok",
            authorization_url="https://login.microsoftonline.com/auth",
        ),
    )

    response = api.connect_ms_mail_account(
        api.MsMailConnectRequest(client_id="client-1")
    )

    assert response["ok"] is True
    assert response["data"]["authorization_url"].startswith("https://login")
    assert response["data"]["read_only"] is True


def test_ms_mail_sync_is_blocked_when_flag_is_off(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    monkeypatch.setattr(api.config, "ENABLE_MS_MAIL_READ", False)

    client = TestClient(api.app)
    response = client.post("/api/accounts/ms-mail/sync", json={"top": 25})

    assert response.status_code == 403


def test_ms_mail_sync_stores_dedupes_and_processes_when_enabled(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    monkeypatch.setattr(api.config, "ENABLE_MS_MAIL_READ", True)
    monkeypatch.setattr(api, "load_ms_mail_account", lambda: object())
    monkeypatch.setattr(api, "decrypt_ms_mail_token_bundle", lambda _account: {"access_token": "token"})
    monkeypatch.setattr(
        api,
        "list_ms_mail_messages",
        lambda **_kwargs: MsMailProviderResult(
            ok=True,
            message="ok",
            messages=(
                {
                    "message_id": "graph-1",
                    "sender": "kunde@example.test",
                    "subject": "Bitte Philip Rechnung prüfen",
                    "received_at": "2026-07-09T10:00:00Z",
                    "snippet": "Bitte erledigen.",
                },
            ),
            external_call_used=True,
        ),
    )

    client = TestClient(api.app)
    response = client.post("/api/accounts/ms-mail/sync", json={"top": 25})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["stored_count"] == 1
    assert payload["read_only"] is True
    assert payload["real_email_enabled"] is False

    repo = MsMailMessageRepository(db_path)
    assert len(repo.list_messages()) == 1
    preview = client.get("/api/messages/ms-mail").json()["data"]
    assert preview["count"] == 1


def test_ms_mail_activation_endpoint_requires_gate(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    response = client.post(
        "/api/accounts/ms-mail/activation-gate",
        json={"approval_token": "ja", "scanner_smoke_passed": True},
    )

    assert response.status_code == 200
    assert response.json()["data"]["allowed"] is False
