"""Tests for encrypted Microsoft mail account storage."""

from __future__ import annotations

import json

from friday.app.ms_mail_account_store import (
    MS_MAIL_ACCOUNT_DELETE_TOKEN,
    MS_MAIL_ACCOUNT_SAVE_TOKEN,
    build_ms_mail_account,
    decrypt_ms_mail_token_bundle,
    delete_ms_mail_account,
    list_ms_mail_accounts,
    load_ms_mail_account,
    migrate_legacy_ms_mail_account,
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


def test_ms_mail_legacy_account_migrates_idempotently(tmp_path) -> None:
    legacy_path = tmp_path / "accounts" / "ms_mail_account.json"
    accounts_dir = tmp_path / "accounts" / "ms_mail_accounts"
    account = build_ms_mail_account(
        client_id="client-1",
        tenant="common",
        username="office@familienhelden.at",
        token_bundle={"access_token": "secret"},
        last_test_ok=True,
        protector=_protector,
    )
    save_ms_mail_account(
        account,
        approval_token=MS_MAIL_ACCOUNT_SAVE_TOKEN,
        account_path=legacy_path,
    )

    first = migrate_legacy_ms_mail_account(legacy_path=legacy_path, accounts_dir=accounts_dir)
    second = migrate_legacy_ms_mail_account(legacy_path=legacy_path, accounts_dir=accounts_dir)
    accounts = list_ms_mail_accounts(accounts_dir=accounts_dir, migrate_legacy=False)

    assert first == second
    assert legacy_path.exists()
    assert len(accounts) == 1
    assert accounts[0].account_id == "office_familienhelden_at"
    assert accounts[0].username == "office@familienhelden.at"


def test_ms_mail_store_keeps_multiple_accounts_separate(tmp_path) -> None:
    accounts_dir = tmp_path / "accounts" / "ms_mail_accounts"
    first = build_ms_mail_account(
        client_id="client-1",
        tenant="tenant-1",
        username="office@familienhelden.at",
        token_bundle={"access_token": "office-secret"},
        last_test_ok=True,
        protector=_protector,
    )
    second = build_ms_mail_account(
        client_id="client-1",
        tenant="tenant-1",
        username="philip@familienhelden.at",
        token_bundle={"access_token": "philip-secret"},
        last_test_ok=True,
        protector=_protector,
    )

    save_ms_mail_account(first, approval_token=MS_MAIL_ACCOUNT_SAVE_TOKEN, accounts_dir=accounts_dir)
    save_ms_mail_account(second, approval_token=MS_MAIL_ACCOUNT_SAVE_TOKEN, accounts_dir=accounts_dir)
    accounts = list_ms_mail_accounts(accounts_dir=accounts_dir, migrate_legacy=False)

    assert [account.account_id for account in accounts] == [
        "office_familienhelden_at",
        "philip_familienhelden_at",
    ]
    assert decrypt_ms_mail_token_bundle(accounts[0], unprotector=_unprotector) == {
        "access_token": "office-secret",
    }
    assert decrypt_ms_mail_token_bundle(accounts[1], unprotector=_unprotector) == {
        "access_token": "philip-secret",
    }


def test_ms_mail_delete_removes_only_selected_account(tmp_path) -> None:
    accounts_dir = tmp_path / "accounts" / "ms_mail_accounts"
    first = build_ms_mail_account(
        client_id="client-1",
        tenant="tenant-1",
        username="office@familienhelden.at",
        token_bundle={"access_token": "office-secret"},
        protector=_protector,
    )
    second = build_ms_mail_account(
        client_id="client-1",
        tenant="tenant-1",
        username="philip@familienhelden.at",
        token_bundle={"access_token": "philip-secret"},
        protector=_protector,
    )
    save_ms_mail_account(first, approval_token=MS_MAIL_ACCOUNT_SAVE_TOKEN, accounts_dir=accounts_dir)
    save_ms_mail_account(second, approval_token=MS_MAIL_ACCOUNT_SAVE_TOKEN, accounts_dir=accounts_dir)

    result = delete_ms_mail_account(
        approval_token=MS_MAIL_ACCOUNT_DELETE_TOKEN,
        account_id=first.account_id,
        accounts_dir=accounts_dir,
    )
    remaining = list_ms_mail_accounts(accounts_dir=accounts_dir, migrate_legacy=False)

    assert result.persisted is True
    assert [account.account_id for account in remaining] == ["philip_familienhelden_at"]
