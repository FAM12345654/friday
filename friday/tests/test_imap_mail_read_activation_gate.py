"""Tests for the guarded IMAP mail read activation gate."""

from __future__ import annotations

from friday.app.imap_mail_account_store import (
    IMAP_MAIL_ACCOUNT_SAVE_TOKEN,
    build_imap_mail_account,
    save_imap_mail_account,
)
from friday.app.imap_mail_read_activation_gate import (
    IMAP_MAIL_READ_ACTIVATION_TOKEN,
    build_imap_mail_read_activation_gate,
)


def _save_account(tmp_path, *, last_test_ok: bool = True):
    account = build_imap_mail_account(
        username="philip07102000@gmail.com",
        app_password="app-secret",
        protector=lambda raw: ("enc:" + raw.decode("utf-8"), "test"),
        last_test_ok=last_test_ok,
    )
    result = save_imap_mail_account(account, approval_token=IMAP_MAIL_ACCOUNT_SAVE_TOKEN, accounts_dir=tmp_path)
    return account, result


def test_imap_mail_activation_gate_blocks_wrong_token_and_missing_scanner(tmp_path) -> None:
    _account, saved = _save_account(tmp_path)

    gate = build_imap_mail_read_activation_gate(
        approval_token="JA",
        scanner_smoke_passed=False,
        account_path=saved.account_path,
    )

    assert gate.allowed is False
    assert "approval_token_invalid" in gate.blocked_reasons
    assert "scanner_smoke_not_passed" in gate.blocked_reasons
    assert gate.external_send_enabled is False


def test_imap_mail_activation_gate_requires_confirmed_login(tmp_path) -> None:
    _account, saved = _save_account(tmp_path, last_test_ok=False)

    gate = build_imap_mail_read_activation_gate(
        approval_token=IMAP_MAIL_READ_ACTIVATION_TOKEN,
        scanner_smoke_passed=True,
        account_path=saved.account_path,
    )

    assert gate.allowed is False
    assert "imap_mail_login_not_confirmed" in gate.blocked_reasons


def test_imap_mail_activation_gate_allows_read_only_after_hard_checks(tmp_path) -> None:
    _account, saved = _save_account(tmp_path)

    gate = build_imap_mail_read_activation_gate(
        approval_token=IMAP_MAIL_READ_ACTIVATION_TOKEN,
        scanner_smoke_passed=True,
        account_path=saved.account_path,
    )

    assert gate.allowed is True
    assert gate.status == "ready_for_imap_mail_read_activation"
    assert gate.account_connected is True
    assert gate.last_test_ok is True
    assert gate.real_email_enabled is False
