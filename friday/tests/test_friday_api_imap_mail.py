"""Tests for Gmail/IMAP read-only unified mail API endpoints."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from friday.agents.message_agent import MessageAgent
from friday.app.imap_mail_reader import ImapMailMessage, ImapMailReadResult
from friday.storage.database import setup_local_database
from friday.storage.repositories import MsMailMessageRepository


def _load_api_module():
    module_path = Path(__file__).resolve().parents[2] / "friday-api" / "main.py"
    spec = importlib.util.spec_from_file_location("friday_api_main_imap_mail_test", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_imap_mail_status_is_password_free(monkeypatch) -> None:
    api = _load_api_module()
    monkeypatch.setattr(
        api,
        "imap_mail_account_status",
        lambda: {
            "connected": True,
            "account_count": 1,
            "accounts": [
                {
                    "account_id": "gmail_philip07102000_gmail_com",
                    "username_masked": "p***@gmail.com",
                    "last_test_ok": True,
                }
            ],
            "read_enabled": False,
            "real_email_enabled": False,
        },
    )

    response = api.get_imap_mail_status()

    assert response["ok"] is True
    assert response["data"]["connected"] is True
    assert "app_password" not in str(response["data"])
    assert "encrypted_app_password" not in str(response["data"])


def test_imap_mail_connect_saves_only_after_successful_login(monkeypatch) -> None:
    api = _load_api_module()
    saved_accounts = []
    monkeypatch.setattr(
        api,
        "check_imap_mail_login",
        lambda **_kwargs: ImapMailReadResult(
            ok=True,
            messages=(),
            message="ok",
            blocked_reasons=(),
            external_call_used=True,
            read_only=True,
        ),
    )

    def _save(account, **_kwargs):
        saved_accounts.append(account)
        return SimpleNamespace(persisted=True, message="saved")

    monkeypatch.setattr(api, "save_imap_mail_account", _save)
    monkeypatch.setattr(
        api,
        "imap_mail_account_status",
        lambda: {"connected": True, "account_count": len(saved_accounts), "accounts": []},
    )

    client = TestClient(api.app)
    response = client.post(
        "/api/accounts/imap-mail/connect",
        json={
            "username": "philip07102000@gmail.com",
            "app_password": "runtime-secret",
            "approval_token": "KONTO SPEICHERN",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["saved"] is True
    assert payload["account_id"] == "gmail_philip07102000_gmail_com"
    assert "runtime-secret" not in response.text
    assert len(saved_accounts) == 1


def test_imap_mail_sync_is_blocked_when_flag_is_off(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    monkeypatch.setattr(api.config, "ENABLE_IMAP_MAIL_READ", False)

    client = TestClient(api.app)
    response = client.post("/api/accounts/imap-mail/sync", json={"top": 25})

    assert response.status_code == 403


def test_imap_mail_sync_stores_messages_in_unified_inbox(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    monkeypatch.setattr(api.config, "ENABLE_IMAP_MAIL_READ", True)
    account = SimpleNamespace(
        account_id="gmail_philip07102000_gmail_com",
        username="philip07102000@gmail.com",
    )
    monkeypatch.setattr(api, "list_imap_mail_accounts", lambda: (account,))
    monkeypatch.setattr(api, "load_imap_mail_account", lambda account_id=None: account)
    monkeypatch.setattr(api, "decrypt_imap_mail_app_password", lambda _account: "runtime-secret")
    monkeypatch.setattr(
        api,
        "read_imap_mail_messages",
        lambda **_kwargs: ImapMailReadResult(
            ok=True,
            messages=(
                ImapMailMessage(
                    provider_message_id="gmail-1",
                    sender="Kollegin <kollegin@example.test>",
                    subject="Bitte Philip Rechnung pruefen",
                    received_at="2026-07-09T10:00:00Z",
                    snippet="Bitte pruefen.",
                    body_full="Hallo Philip, bitte pruefen.",
                    recipients=({"type": "to", "name": "Philip", "address": "philip07102000@gmail.com"},),
                ),
            ),
            message="ok",
            blocked_reasons=(),
            external_call_used=True,
            read_only=True,
        ),
    )

    client = TestClient(api.app)
    response = client.post("/api/accounts/imap-mail/sync", json={"top": 25})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["stored_count"] == 1
    assert payload["accounts_synced"] == 1
    assert payload["read_only"] is True
    assert payload["real_email_enabled"] is False

    repo = MsMailMessageRepository(db_path)
    items = repo.list_messages()
    assert len(items) == 1
    assert items[0]["source"] == "imap_mail"

    inbox = client.get("/api/messages/mail").json()["data"]
    assert inbox["count"] == 1
    assert inbox["items"][0]["source"] == "imap_mail"
    detail = client.get(f"/api/messages/mail/{items[0]['id']}").json()["data"]
    assert detail["body_full"] == "Hallo Philip, bitte pruefen."
    assert detail["read_only"] is True


def test_imap_mail_activation_endpoint_requires_gate() -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    response = client.post(
        "/api/accounts/imap-mail/activation-gate",
        json={"approval_token": "ja", "scanner_smoke_passed": True},
    )

    assert response.status_code == 200
    assert response.json()["data"]["allowed"] is False
