"""Tests for Friday API email account endpoints."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from pathlib import Path

import friday.config as config
from friday.app.email_imap_reader import EmailInboxPreviewItem
from friday.app.email_send_guard import EmailSendGuardResult


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location("friday_api_main_for_email_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class _Ok:
    ok: bool = True
    message_id: str | None = "msg-1"
    error: str | None = None
    sent: bool = True


def test_api_email_status_never_exposes_password(monkeypatch) -> None:
    api = _load_api_module()
    monkeypatch.setattr(
        api,
        "email_account_status",
        lambda: {
            "connected": True,
            "email_address": "user@example.test",
            "last_test_ok": True,
            "real_email_enabled": False,
        },
    )

    response = api.get_email_account_status()

    assert response["ok"] is True
    assert response["data"]["connected"] is True
    assert "app_password" not in response["data"]
    assert "encrypted_app_password" not in response["data"]


def test_api_connect_email_account_uses_tests_and_save_token(monkeypatch) -> None:
    api = _load_api_module()
    saved = {}

    monkeypatch.setattr(api, "check_smtp_login", lambda **_kwargs: _Ok())
    monkeypatch.setattr(api, "check_imap_login", lambda **_kwargs: _Ok())

    def _save(account, approval_token):
        saved["account"] = account
        saved["approval_token"] = approval_token

        return type(
            "Result",
            (),
            {
                "persisted": True,
                "message": "saved",
            },
        )()

    monkeypatch.setattr(api, "save_email_account", _save)
    monkeypatch.setattr(
        api,
        "email_account_status",
        lambda: {"connected": True, "email_address": "user@example.test", "last_test_ok": True},
    )

    response = api.connect_email_account(
        api.EmailAccountConnectRequest(
            preset_name="gmail",
            email_address="user@example.test",
            username="user@example.test",
            app_password="runtime-secret",
            approval_token="KONTO SPEICHERN",
        )
    )

    assert response["ok"] is True
    assert response["data"]["saved"] is True
    assert saved["approval_token"] == "KONTO SPEICHERN"
    assert saved["account"].last_test_ok is True


def test_api_email_inbox_returns_read_only_preview(monkeypatch) -> None:
    api = _load_api_module()
    account = object()
    item = EmailInboxPreviewItem(
        sender="sender@example.test",
        subject="Hallo",
        date="2026-07-09",
        text_preview="Kurz",
    )
    result = type(
        "InboxResult",
        (),
        {
            "ok": True,
            "items": (item,),
            "error": None,
            "read_only": True,
        },
    )()

    monkeypatch.setattr(api, "load_email_account", lambda: account)
    monkeypatch.setattr(api, "decrypt_email_account_password", lambda _account: "runtime-secret")
    monkeypatch.setattr(api, "read_recent_inbox_emails", lambda **_kwargs: result)

    response = api.get_email_inbox_preview()

    assert response["ok"] is True
    assert response["data"]["connected"] is True
    assert response["data"]["read_only"] is True
    assert response["data"]["items"][0]["subject"] == "Hallo"


def test_api_send_task_forward_email_is_blocked_while_real_email_disabled(monkeypatch) -> None:
    api = _load_api_module()
    monkeypatch.setattr(config, "ENABLE_REAL_EMAIL", False)
    monkeypatch.setattr(
        api.task_agent,
        "get_task_by_id",
        lambda task_id: {"id": task_id, "title": "Aufgabe"},
    )
    monkeypatch.setattr(
        api.contact_agent,
        "load_contacts",
        lambda: [{"id": 5, "name": "Mia", "email_address": "mia@example.test"}],
    )
    monkeypatch.setattr(
        api,
        "check_email_send_allowed",
        lambda **_kwargs: EmailSendGuardResult(
            allowed=False,
            blocked_reasons=("real_email_disabled",),
            recipient="mia@example.test",
            subject="Aufgabe",
            daily_limit=20,
            sent_today_count=0,
            account_connected=False,
            last_test_ok=False,
            recipient_is_contact=True,
            real_email_enabled=False,
        ),
    )

    response = api.send_task_forward_email(
        api.EmailSendRequest(
            task_id=1,
            contact_id=5,
            subject="Aufgabe",
            body="Hallo",
            approval_token="EMAIL SENDEN",
        )
    )

    assert response["ok"] is True
    assert response["data"]["sent"] is False
    assert "real_email_disabled" in response["data"]["guard"]["blocked_reasons"]
