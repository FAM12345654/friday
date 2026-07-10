from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from friday.storage.database import setup_local_database


@pytest.fixture()
def api_module(tmp_path, monkeypatch):
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    module_path = Path(__file__).resolve().parents[2] / "friday-api" / "main.py"
    spec = importlib.util.spec_from_file_location("friday_api_main_mail_organize", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.message_agent.db_path = db_path
    monkeypatch.setattr(module.config, "ENABLE_MAIL_ORGANIZE", False)
    return module


def test_mail_organize_run_blocked_when_flag_is_false(api_module) -> None:
    client = TestClient(api_module.app)

    response = client.post("/api/mail/organize/run", json={"top": 5})

    assert response.status_code == 403


def test_mail_organize_log_endpoint_returns_empty_log(api_module) -> None:
    client = TestClient(api_module.app)

    response = client.get("/api/mail/organize/log")

    assert response.status_code == 200
    assert response.json()["data"]["items"] == []
    assert response.json()["data"]["deleted"] is False


def test_mail_organize_activation_gate_rejects_wrong_token(api_module) -> None:
    client = TestClient(api_module.app)

    response = client.post(
        "/api/mail/organize/activation-gate",
        json={"approval_token": "JA", "scanner_smoke_passed": True, "execute_write": False},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["allowed"] is False
    assert "approval_token_required" in payload["blocked_reasons"]


def test_mail_organize_dry_run_selects_only_gmail_noise(api_module, monkeypatch) -> None:
    monkeypatch.setattr(api_module.config, "ENABLE_MAIL_ORGANIZE", True)
    account = api_module.build_imap_mail_account(
        provider="gmail",
        host="imap.gmail.com",
        port=993,
        username="test@example.com",
        app_password="pw",
        last_test_ok=True,
    )
    monkeypatch.setattr(api_module, "list_imap_mail_accounts", lambda: (account,))
    repo = api_module.MsMailMessageRepository(api_module.message_agent.db_path)
    repo.upsert_messages(
        [
            {
                "source": "imap_mail",
                "account_id": account.account_id,
                "provider_message_id": "m1",
                "sender": "Instagram <noreply@instagram.com>",
                "subject": "Newsletter",
            },
            {
                "source": "imap_mail",
                "account_id": account.account_id,
                "provider_message_id": "m2",
                "sender": "Kunde <kunde@example.com>",
                "subject": "Bitte melden",
            },
        ],
        account_id=account.account_id,
        account_username=account.username,
    )
    api_module.ContactRepository(api_module.message_agent.db_path).create_contact(
        "Kunde",
        "kunde",
        email_address="kunde@example.com",
    )
    client = TestClient(api_module.app)

    response = client.post("/api/mail/organize/run", json={"top": 10, "dry_run": True})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["candidate_count"] == 1
    assert data["candidates"][0]["provider_message_id"] == "m1"
    assert data["moved_count"] == 0


def test_mail_organize_undo_marks_log_entry(api_module, monkeypatch) -> None:
    monkeypatch.setattr(api_module.config, "ENABLE_MAIL_ORGANIZE", True)
    account = api_module.build_imap_mail_account(
        provider="gmail",
        host="imap.gmail.com",
        port=993,
        username="test@example.com",
        app_password="pw",
        last_test_ok=True,
    )
    monkeypatch.setattr(api_module, "load_imap_mail_account", lambda account_id: account)
    monkeypatch.setattr(api_module, "decrypt_imap_mail_app_password", lambda account: "pw")
    monkeypatch.setattr(
        api_module,
        "move_back_to_inbox",
        lambda **kwargs: api_module.ImapMailWriteResult(
            ok=True,
            message="Mail wurde zurueck in den Posteingang gelegt.",
            account_id=account.account_id,
            provider_message_id=kwargs["provider_message_id"],
            from_folder="Friday/Aussortiert",
            to_label="INBOX",
        ),
    )
    entry = api_module.MailboxCleanupLogRepository(api_module.message_agent.db_path).create_entry(
        account_id=account.account_id,
        provider_message_id="m1",
        sender="Noise",
        subject="Newsletter",
    )
    client = TestClient(api_module.app)

    response = client.post(f"/api/mail/organize/undo/{entry['id']}")

    assert response.status_code == 200
    assert response.json()["data"]["undone"] is True
