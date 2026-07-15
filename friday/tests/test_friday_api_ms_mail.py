"""Tests for Microsoft Graph read-only mail API endpoints."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from friday.agents.message_agent import MessageAgent
from friday.app.ms_mail_provider import MsMailProviderResult
from friday.app.ms_mail_account_store import (
    decrypt_ms_mail_token_bundle as decrypt_stored_ms_mail_token_bundle,
)
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
        "build_ms_mail_authorization_flow",
        lambda **kwargs: (
            MsMailProviderResult(
                ok=True,
                message="ok",
                authorization_url=f"https://login.microsoftonline.com/auth?state={kwargs['state']}",
            ),
            {"state": kwargs["state"], "code_verifier": "private"},
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
        api.oauth_transactions,
        "consume",
        lambda **kwargs: SimpleNamespace(
            state=kwargs["state"],
            context={
                "client_id": "client-1",
                "tenant": "common",
                "auth_flow": {"state": kwargs["state"], "code_verifier": "private"},
            },
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
            authorization_response="http://localhost/?code=one&state=state-one",
            approval_token="KONTO SPEICHERN",
        )
    )
    second = api.connect_ms_mail_account(
        api.MsMailConnectRequest(
            client_id="client-1",
            authorization_response="http://localhost/?code=two&state=state-two",
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
    monkeypatch.setattr(
        api,
        "ensure_fresh_ms_mail_access_token",
        lambda **kwargs: MsMailProviderResult(
            ok=True,
            message="unchanged",
            token_bundle=kwargs["token_bundle"],
            external_call_used=False,
        ),
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


def test_ms_mail_endpoint_hides_office_irrelevant_by_default_and_include_all_restores(tmp_path) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    repo = MsMailMessageRepository(db_path)
    repo.upsert_messages(
        [
            {
                "message_id": "graph-office-hidden",
                "sender": "info@example.test",
                "subject": "Bitte Unterlagen prüfen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Bitte erledigen.",
                "recipients": [{"name": "Alex", "address": "alex@familienhelden.at"}],
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )

    client = TestClient(api.app)
    default_view = client.get("/api/messages/ms-mail").json()["data"]
    all_view = client.get("/api/messages/ms-mail?include_all=true").json()["data"]

    assert default_view["count"] == 0
    assert default_view["include_all"] is False
    assert all_view["count"] == 1
    assert all_view["include_all"] is True
    assert all_view["items"][0]["relevant_for_user"] == 0
    assert all_view["items"][0]["relevance_reason"] == "not_relevant"


def test_ms_mail_detail_endpoint_returns_full_local_body_and_recipients(tmp_path) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    repo = MsMailMessageRepository(db_path)
    stored = repo.upsert_messages(
        [
            {
                "message_id": "graph-detail",
                "sender": "Info <info@example.test>",
                "subject": "Bitte Philip prüfen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Kurz",
                "body_full": "Der komplette lokale Mailtext.",
                "recipients": [{"type": "to", "name": "Philip", "address": "philip@example.test"}],
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )[0]

    client = TestClient(api.app)
    response = client.get(f"/api/messages/ms-mail/{stored['id']}")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["body_full"] == "Der komplette lokale Mailtext."
    assert payload["recipients_list"][0]["name"] == "Philip"
    assert payload["read_only"] is True
    assert payload["real_email_enabled"] is False


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


def test_ms_mail_spam_endpoint_blocks_sender_and_include_spam_restores_view(tmp_path) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    repo = MsMailMessageRepository(db_path)
    stored = repo.upsert_messages(
        [
            {
                "message_id": "graph-spam",
                "sender": "spam@example.test",
                "subject": "Werbung",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Nicht relevant.",
            }
        ]
    )[0]

    client = TestClient(api.app)
    marked = client.post(f"/api/messages/ms_mail/{stored['id']}/spam")

    assert marked.status_code == 200
    assert marked.json()["data"]["provider_changed"] is False
    assert client.get("/api/messages/ms-mail").json()["data"]["count"] == 0
    spam_view = client.get("/api/messages/ms-mail?include_spam=true").json()["data"]
    assert spam_view["count"] == 1
    assert spam_view["items"][0]["is_spam"] == 1

    blocked = client.get("/api/senders/blocked").json()["data"]["items"]
    assert len(blocked) == 1
    assert blocked[0]["source"] == "ms_mail"

    unblocked = client.delete(f"/api/senders/blocked/{blocked[0]['id']}")
    assert unblocked.status_code == 200
    restored = client.get("/api/messages/ms-mail").json()["data"]
    assert restored["count"] == 1
    assert restored["items"][0]["is_spam"] == 0


def test_blocked_ms_mail_sender_syncs_as_spam_without_suggestions(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    monkeypatch.setattr(api.config, "ENABLE_MS_MAIL_READ", True)
    api.BlockedSenderRepository(db_path).block_sender(
        source="ms_mail",
        sender="spam@example.test",
        label="Spam Sender",
    )
    account = SimpleNamespace(account_id="office_familienhelden_at", username="office@familienhelden.at")
    monkeypatch.setattr(api, "list_ms_mail_accounts", lambda: (account,))
    monkeypatch.setattr(api, "decrypt_ms_mail_token_bundle", lambda _account: {"access_token": "token"})
    monkeypatch.setattr(
        api,
        "list_ms_mail_messages",
        lambda **_kwargs: MsMailProviderResult(
            ok=True,
            message="ok",
            messages=(
                {
                    "message_id": "graph-spam",
                    "sender": "spam@example.test",
                    "subject": "Bitte Unterlagen prüfen",
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
    assert payload["process_result"]["processed_count"] == 0
    assert payload["process_result"]["task_suggestions_created"] == 0
    assert client.get("/api/messages/ms-mail").json()["data"]["count"] == 0
    assert client.get("/api/messages/ms-mail?include_spam=true").json()["data"]["count"] == 1


def test_ms_mail_sync_refreshes_token_and_saves_bundle(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    monkeypatch.setattr(api.config, "ENABLE_MS_MAIL_READ", True)
    account = SimpleNamespace(
        account_id="office_familienhelden_at",
        username="office@familienhelden.at",
        client_id="client-1",
        tenant="common",
        last_test_ok=True,
        connected_at="2026-07-09T10:00:00+00:00",
    )
    saved_accounts = []
    monkeypatch.setattr(api, "list_ms_mail_accounts", lambda: (account,))
    monkeypatch.setattr(api, "decrypt_ms_mail_token_bundle", lambda _account: {"access_token": "old", "refresh_token": "old-refresh"})
    monkeypatch.setattr(
        api,
        "ensure_fresh_ms_mail_access_token",
        lambda **_kwargs: MsMailProviderResult(
            ok=True,
            message="refreshed",
            token_bundle={"access_token": "fresh", "refresh_token": "new-refresh"},
            external_call_used=True,
        ),
    )

    def _save(account_to_save, **_kwargs):
        saved_accounts.append(account_to_save)
        return SimpleNamespace(persisted=True, message="saved", blocked_reasons=())

    monkeypatch.setattr(api, "save_ms_mail_account", _save)

    def _fake_list_ms_mail_messages(*, token_bundle, top):
        assert token_bundle["access_token"] == "fresh"
        return MsMailProviderResult(
            ok=True,
            message="ok",
            messages=(
                {
                    "message_id": "graph-refresh",
                    "sender": "kunde@example.test",
                    "subject": "Bitte Philip Rechnung prüfen",
                    "received_at": "2026-07-09T10:00:00Z",
                    "snippet": "Bitte erledigen.",
                },
            ),
            external_call_used=True,
        )

    monkeypatch.setattr(api, "list_ms_mail_messages", _fake_list_ms_mail_messages)

    client = TestClient(api.app)
    response = client.post("/api/accounts/ms-mail/sync", json={"top": 25})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["stored_count"] == 1
    assert payload["accounts_synced"] == 1
    assert len(saved_accounts) == 1
    refreshed_bundle = decrypt_stored_ms_mail_token_bundle(saved_accounts[0])
    assert refreshed_bundle["access_token"] == "fresh"
    assert refreshed_bundle["refresh_token"] == "new-refresh"


def test_ms_mail_sync_reports_reconnect_when_refresh_fails(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    monkeypatch.setattr(api.config, "ENABLE_MS_MAIL_READ", True)
    account = SimpleNamespace(
        account_id="office_familienhelden_at",
        username="office@familienhelden.at",
        client_id="client-1",
        tenant="common",
        last_test_ok=True,
        connected_at="2026-07-09T10:00:00+00:00",
    )
    monkeypatch.setattr(api, "list_ms_mail_accounts", lambda: (account,))
    monkeypatch.setattr(api, "decrypt_ms_mail_token_bundle", lambda _account: {"access_token": "old", "refresh_token": "expired"})
    monkeypatch.setattr(
        api,
        "ensure_fresh_ms_mail_access_token",
        lambda **_kwargs: MsMailProviderResult(
            ok=False,
            message="expired",
            blocked_reasons=("token_refresh_failed", "reconnect_required"),
            external_call_used=True,
        ),
    )
    monkeypatch.setattr(
        api,
        "list_ms_mail_messages",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("Graph must not be called")),
    )

    client = TestClient(api.app)
    response = client.post("/api/accounts/ms-mail/sync", json={"top": 25})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["stored_count"] == 0
    assert payload["accounts_synced"] == 0
    assert payload["accounts"][0]["ok"] is False
    assert "reconnect_required" in payload["accounts"][0]["blocked_reasons"]
