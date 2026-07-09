"""Tests for encrypted Microsoft mail account storage."""

from __future__ import annotations

import json

from friday.app.ms_mail_account_store import (
    MS_MAIL_ACCOUNT_DELETE_TOKEN,
    MS_MAIL_ACCOUNT_SAVE_TOKEN,
    build_ms_mail_account,
    decrypt_ms_mail_token_bundle,
    delete_ms_mail_account,
    load_ms_mail_account,
    ms_mail_account_status,
    save_ms_mail_account,
)


def _protector(raw: bytes) -> tuple[str, str]:
    return raw.decode("utf-8"), "plain-test"


def _unprotector(value: str, method: str) -> bytes:
    assert method == "plain-test"
    return value.encode("utf-8")


def test_ms_mail_account_save_requires_hard_token(tmp_path) -> None:
    account = build_ms_mail_account(
        client_id="client-1",
        tenant="common",
        username="mail@familienhelden.at",
        token_bundle={"access_token": "secret"},
        protector=_protector,
    )
    account_path = tmp_path / "ms_mail_account.json"

    blocked = save_ms_mail_account(account, approval_token="ja", account_path=account_path)
    saved = save_ms_mail_account(account, approval_token=MS_MAIL_ACCOUNT_SAVE_TOKEN, account_path=account_path)

    assert blocked.persisted is False
    assert saved.persisted is True
    assert load_ms_mail_account(account_path) == account


def test_ms_mail_account_decrypts_only_at_runtime(tmp_path) -> None:
    token_bundle = {"access_token": "secret", "refresh_token": "refresh"}
    account = build_ms_mail_account(
        client_id="client-1",
        tenant="common",
        username="mail@familienhelden.at",
        token_bundle=token_bundle,
        protector=_protector,
    )

    decrypted = decrypt_ms_mail_token_bundle(account, unprotector=_unprotector)

    assert decrypted == token_bundle
    assert json.dumps(account.__dict__).find("refresh") >= 0


def test_ms_mail_status_never_exposes_token(tmp_path) -> None:
    account = build_ms_mail_account(
        client_id="client-1",
        tenant="common",
        username="mail@familienhelden.at",
        token_bundle={"access_token": "secret"},
        last_test_ok=True,
        protector=_protector,
    )
    account_path = tmp_path / "ms_mail_account.json"
    save_ms_mail_account(account, approval_token=MS_MAIL_ACCOUNT_SAVE_TOKEN, account_path=account_path)

    status = ms_mail_account_status(account_path)

    assert status["connected"] is True
    assert status["username_masked"] == "m***@familienhelden.at"
    assert "token" not in status
    assert "encrypted_token_bundle" not in status
    assert status["real_email_enabled"] is False


def test_ms_mail_delete_requires_hard_token(tmp_path) -> None:
    account_path = tmp_path / "ms_mail_account.json"
    account_path.write_text("{}", encoding="utf-8")

    blocked = delete_ms_mail_account(approval_token="ja", account_path=account_path)
    deleted = delete_ms_mail_account(approval_token=MS_MAIL_ACCOUNT_DELETE_TOKEN, account_path=account_path)

    assert blocked.persisted is False
    assert deleted.persisted is True
    assert not account_path.exists()
