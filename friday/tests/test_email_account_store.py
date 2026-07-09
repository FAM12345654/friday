"""Tests for guarded local email account storage."""

from __future__ import annotations

import json

from friday.app.email_account_store import (
    EMAIL_ACCOUNT_DELETE_TOKEN,
    EMAIL_ACCOUNT_SAVE_TOKEN,
    build_email_account_from_preset,
    delete_email_account,
    decrypt_email_account_password,
    email_account_status,
    load_email_account,
    save_email_account,
)


def _protector(secret: bytes) -> tuple[str, str]:
    assert secret == b"app-password-secret"
    return "encrypted-secret", "test-dpapi"


def _unprotector(value: str, method: str) -> bytes:
    assert value == "encrypted-secret"
    assert method == "test-dpapi"
    return b"app-password-secret"


def test_email_account_store_encrypts_and_roundtrips_without_plaintext(tmp_path) -> None:
    path = tmp_path / "accounts" / "email_account.json"
    account = build_email_account_from_preset(
        preset_name="gmail",
        email_address="user@example.test",
        username="user@example.test",
        app_password="app-password-secret",
        last_test_ok=True,
        protector=_protector,
    )

    result = save_email_account(
        account,
        approval_token=EMAIL_ACCOUNT_SAVE_TOKEN,
        account_path=path,
    )
    loaded = load_email_account(path)
    raw_text = path.read_text(encoding="utf-8")

    assert result.persisted is True
    assert "app-password-secret" not in raw_text
    assert json.loads(raw_text)["encrypted_app_password"] == "encrypted-secret"
    assert loaded is not None
    assert decrypt_email_account_password(loaded, unprotector=_unprotector) == "app-password-secret"


def test_email_account_store_requires_save_token(tmp_path) -> None:
    path = tmp_path / "email_account.json"
    account = build_email_account_from_preset(
        preset_name="gmail",
        email_address="user@example.test",
        username="user@example.test",
        app_password="app-password-secret",
        protector=_protector,
    )

    result = save_email_account(account, approval_token="wrong", account_path=path)

    assert result.persisted is False
    assert "approval_token_invalid" in result.blocked_reasons
    assert not path.exists()


def test_email_account_store_delete_requires_token(tmp_path) -> None:
    path = tmp_path / "email_account.json"
    account = build_email_account_from_preset(
        preset_name="gmail",
        email_address="user@example.test",
        username="user@example.test",
        app_password="app-password-secret",
        protector=_protector,
    )
    save_email_account(account, approval_token=EMAIL_ACCOUNT_SAVE_TOKEN, account_path=path)

    blocked = delete_email_account(approval_token="wrong", account_path=path)
    deleted = delete_email_account(approval_token=EMAIL_ACCOUNT_DELETE_TOKEN, account_path=path)

    assert blocked.persisted is False
    assert path.exists() is False
    assert deleted.persisted is True


def test_email_account_status_never_exposes_password(tmp_path) -> None:
    path = tmp_path / "email_account.json"
    account = build_email_account_from_preset(
        preset_name="outlook",
        email_address="user@example.test",
        username="user@example.test",
        app_password="app-password-secret",
        protector=_protector,
    )
    save_email_account(account, approval_token=EMAIL_ACCOUNT_SAVE_TOKEN, account_path=path)

    status = email_account_status(path)

    assert status["connected"] is True
    assert "encrypted_app_password" not in status
    assert "app_password" not in status
    assert status["smtp_host"] == "smtp.office365.com"
