"""Tests for EMAIL AKTIVIEREN guard."""

from __future__ import annotations

from friday.app.email_account_store import EMAIL_ACCOUNT_SAVE_TOKEN, build_email_account_from_preset, save_email_account
from friday.app.email_activation_gate import EMAIL_ACTIVATION_TOKEN, build_email_activation_gate


def _account():
    return build_email_account_from_preset(
        preset_name="gmail",
        email_address="user@example.test",
        username="user@example.test",
        app_password="secret",
        last_test_ok=True,
        protector=lambda _secret: ("encrypted", "test"),
    )


def test_email_activation_gate_requires_account_token_and_smoke(tmp_path) -> None:
    account_path = tmp_path / "email_account.json"

    no_account = build_email_activation_gate(
        approval_token=EMAIL_ACTIVATION_TOKEN,
        scanner_smoke_passed=True,
        account_path=account_path,
    )
    save_email_account(_account(), approval_token=EMAIL_ACCOUNT_SAVE_TOKEN, account_path=account_path)
    wrong_token = build_email_activation_gate(
        approval_token="wrong",
        scanner_smoke_passed=True,
        account_path=account_path,
    )
    no_smoke = build_email_activation_gate(
        approval_token=EMAIL_ACTIVATION_TOKEN,
        scanner_smoke_passed=False,
        account_path=account_path,
    )
    allowed = build_email_activation_gate(
        approval_token=EMAIL_ACTIVATION_TOKEN,
        scanner_smoke_passed=True,
        account_path=account_path,
    )

    assert no_account.allowed is False
    assert "email_account_missing" in no_account.blocked_reasons
    assert wrong_token.allowed is False
    assert "approval_token_invalid" in wrong_token.blocked_reasons
    assert no_smoke.allowed is False
    assert "scanner_smoke_not_passed" in no_smoke.blocked_reasons
    assert allowed.allowed is True
    assert allowed.config_write_performed is False
