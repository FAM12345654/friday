"""Tests for Microsoft Graph read-only mail API endpoints."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
from pathlib import Path
from types import SimpleNamespace

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
            "account_count": 2,
            "accounts": [
                {
                    "account_id": "office_familienhelden_at",
                    "username_masked": "o***@familienhelden.at",
                    "last_test_ok": True,
                }
            ],
            "username_masked": "m***@familienhelden.at",
            "read_enabled": False,
            "real_email_enabled": False,
        },
    )

    response = api.get_ms_mail_status()

    assert response["ok"] is True
    assert response["data"]["connected"] is True
    assert response["data"]["account_count"] == 2
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


def test_ms_mail_connect_callback_adds_accounts_without_overwriting(monkeypatch) -> None:
    api = _load_api_module()
    saved_accounts = []
    usernames = iter(["office@familienhelden.at", "philip@familienhelden.at"])
    monkeypatch.setattr(
        api,
        "exchange_ms_mail_auth_response",
        lambda **_kwargs: MsMailProviderResult(
            ok=True,
            message="ok",
            token_bundle={"access_token": "token"},
        ),
    )
    monkeypatch.setattr(
        api,
        "test_ms_mail_connection",
        lambda **_kwargs: MsMailProviderResult(ok=True, message="ok", username=next(usernames)),
    )

    def _save(account, **_kwargs):
        saved_accounts.append(account)
        return SimpleNamespace(persisted=True, message="saved")

    monkeypatch.setattr(api, "save_ms_mail_account", _save)
    monkeypatch.setattr(
        api,
        "ms_mail_account_status",
        lambda: {
            "connected": True,
            "account_count": len(saved_accounts),
            "accounts": [{"account_id": item.account_id} for item in saved_accounts],
            "read_enabled": False,
            "real_email_enabled": False,
        },
    )

    first = api.connect_ms_mail_account(
        api.MsMailConnectRequest(
            client_id="client-1",
            authorization_response="http://localhost/?code=one",
            approval_token="KONTO SPEICHERN",
        )
    )
    second = api.connect_ms_mail_account(
        api.MsMailConnectRequest(
            client_id="client-1",
            authorization_response="http://localhost/?code=two",
            approval_token="KONTO SPEICHERN",
        )
    )

    assert first["data"]["account_id"] == "office_familienhelden_at"
    assert second["data"]["account_id"] == "philip_familienhelden_at"
    assert len(saved_accounts) == 2


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
    accounts = (
        SimpleNamespace(account_id="office_familienhelden_at", username="office@familienhelden.at"),
        SimpleNamespace(account_id="philip_familienhelden_at", username="philip@familienhelden.at"),
    )
    monkeypatch.setattr(api, "list_ms_mail_accounts", lambda: accounts)
    monkeypatch.setattr(
        api,
        "load_ms_mail_account",
        lambda account_id=None: next((item for item in accounts if item.account_id == account_id), None),
    )
    monkeypatch.setattr(
        api,
        "decrypt_ms_mail_token_bundle",
        lambda account: {"access_token": account.account_id},
    )

    def _fake_list_ms_mail_messages(*, token_bundle, top):
        account_id = token_bundle["access_token"]
        username = "kunde@example.test" if account_id.startswith("office") else "philip@example.test"
        return MsMailProviderResult(
            ok=True,
            message="ok",
            messages=(
                {
                    "message_id": "graph-1",
                    "sender": username,
                    "subject": f"Bitte Philip Rechnung prüfen {account_id}",
                    "received_at": "2026-07-09T10:00:00Z",
                    "snippet": "Bitte erledigen.",
                },
            ),
            external_call_used=True,
        )

    monkeypatch.setattr(
        api,
        "list_ms_mail_messages",
        _fake_list_ms_mail_messages,
    )

    client = TestClient(api.app)
    response = client.post("/api/accounts/ms-mail/sync", json={"top": 25})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["stored_count"] == 2
    assert payload["accounts_synced"] == 2
    assert payload["read_only"] is True
    assert payload["real_email_enabled"] is False

    repo = MsMailMessageRepository(db_path)
    assert len(repo.list_messages()) == 2
    assert len(repo.list_messages(account_id="office_familienhelden_at")) == 1
    preview = client.get("/api/messages/ms-mail").json()["data"]
    assert preview["count"] == 2
    filtered = client.get("/api/messages/ms-mail?account_id=philip_familienhelden_at").json()["data"]
    assert filtered["count"] == 1
    assert filtered["items"][0]["account_username"] == "philip@familienhelden.at"


def test_ms_mail_delete_endpoint_removes_selected_account(monkeypatch) -> None:
    api = _load_api_module()
    deleted = []
    monkeypatch.setattr(
        api,
        "delete_ms_mail_account",
        lambda **kwargs: deleted.append(kwargs["account_id"]) or SimpleNamespace(allowed=True, message="deleted"),
    )
    monkeypatch.setattr(
        api,
        "ms_mail_account_status",
        lambda: {"connected": False, "account_count": 0, "accounts": []},
    )

    client = TestClient(api.app)
    response = client.request(
        "DELETE",
        "/api/accounts/ms-mail/office_familienhelden_at",
        json={"approval_token": "KONTO LOESCHEN"},
    )

    assert response.status_code == 200
    assert deleted == ["office_familienhelden_at"]


def test_ms_mail_activation_endpoint_requires_gate(monkeypatch) -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    response = client.post(
        "/api/accounts/ms-mail/activation-gate",
        json={"approval_token": "ja", "scanner_smoke_passed": True},
    )

    assert response.status_code == 200
    assert response.json()["data"]["allowed"] is False
