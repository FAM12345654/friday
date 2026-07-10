"""Tests for guarded encrypted read-only IMAP mail account storage."""

from __future__ import annotations

from friday.app.imap_mail_account_store import (
    IMAP_MAIL_ACCOUNT_DELETE_TOKEN,
    IMAP_MAIL_ACCOUNT_SAVE_TOKEN,
    build_imap_mail_account,
    decrypt_imap_mail_app_password,
    delete_imap_mail_account,
    imap_mail_account_status,
    list_imap_mail_accounts,
    load_imap_mail_account,
    normalize_imap_mail_account_id,
    save_imap_mail_account,
)


def _protector(raw: bytes) -> tuple[str, str]:
    return ("encrypted:" + raw.decode("utf-8")[::-1], "test")


def _unprotector(value: str, method: str) -> bytes:
    assert method == "test"
    return value.removeprefix("encrypted:")[::-1].encode("utf-8")


def test_imap_mail_account_save_requires_hard_token(tmp_path) -> None:
    account = build_imap_mail_account(
        username="philip07102000@gmail.com",
        app_password="app-secret",
        protector=_protector,
        last_test_ok=True,
    )

    blocked = save_imap_mail_account(account, approval_token="JA", accounts_dir=tmp_path)
    saved = save_imap_mail_account(
        account,
        approval_token=IMAP_MAIL_ACCOUNT_SAVE_TOKEN,
        accounts_dir=tmp_path,
    )

    assert blocked.persisted is False
    assert "approval_token_invalid" in blocked.blocked_reasons
    assert saved.persisted is True
    assert "app-secret" not in saved.account_path
    assert "app-secret" not in tmp_path.joinpath(f"{account.account_id}.json").read_text(encoding="utf-8")


def test_imap_mail_account_loads_decrypts_and_lists_multiple_accounts(tmp_path) -> None:
    first = build_imap_mail_account(
        username="philip07102000@gmail.com",
        app_password="first-secret",
        protector=_protector,
        last_test_ok=True,
    )
    second = build_imap_mail_account(
        username="team@example.test",
        app_password="second-secret",
        protector=_protector,
        last_test_ok=False,
    )
    save_imap_mail_account(first, approval_token=IMAP_MAIL_ACCOUNT_SAVE_TOKEN, accounts_dir=tmp_path)
    save_imap_mail_account(second, approval_token=IMAP_MAIL_ACCOUNT_SAVE_TOKEN, accounts_dir=tmp_path)

    accounts = list_imap_mail_accounts(accounts_dir=tmp_path)
    loaded = load_imap_mail_account(account_id=first.account_id, accounts_dir=tmp_path)
    status = imap_mail_account_status(accounts_dir=tmp_path)

    assert {item.account_id for item in accounts} == {first.account_id, second.account_id}
    assert loaded is not None
    assert decrypt_imap_mail_app_password(loaded, unprotector=_unprotector) == "first-secret"
    assert status["account_count"] == 2
    assert "encrypted_app_password" not in status["accounts"][0]
    assert status["last_test_ok"] is True


def test_imap_mail_account_delete_requires_delete_token(tmp_path) -> None:
    account = build_imap_mail_account(
        username="philip07102000@gmail.com",
        app_password="app-secret",
        protector=_protector,
        last_test_ok=True,
    )
    save_imap_mail_account(account, approval_token=IMAP_MAIL_ACCOUNT_SAVE_TOKEN, accounts_dir=tmp_path)

    blocked = delete_imap_mail_account(
        account_id=account.account_id,
        approval_token="KONTO SPEICHERN",
        accounts_dir=tmp_path,
    )

    assert blocked.persisted is False
    assert load_imap_mail_account(account_id=account.account_id, accounts_dir=tmp_path) is not None

    deleted = delete_imap_mail_account(
        account_id=account.account_id,
        approval_token=IMAP_MAIL_ACCOUNT_DELETE_TOKEN,
        accounts_dir=tmp_path,
    )

    assert deleted.persisted is True
    assert load_imap_mail_account(account_id=account.account_id, accounts_dir=tmp_path) is None


def test_imap_mail_account_id_is_stable_for_gmail() -> None:
    assert normalize_imap_mail_account_id("philip07102000@gmail.com") == "gmail_philip07102000_gmail_com"
