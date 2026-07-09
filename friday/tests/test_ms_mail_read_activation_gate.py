"""Tests for Microsoft mail read activation gate."""

from __future__ import annotations

from friday.app.ms_mail_account_store import (
    MS_MAIL_ACCOUNT_SAVE_TOKEN,
    build_ms_mail_account,
    save_ms_mail_account,
)
from friday.app.ms_mail_read_activation_gate import (
    MS_MAIL_READ_ACTIVATION_TOKEN,
    apply_ms_mail_read_activation_to_config,
    build_ms_mail_read_activation_gate,
)


def _protector(raw: bytes) -> tuple[str, str]:
    return raw.decode("utf-8"), "plain-test"


def _write_account(path, *, last_test_ok=True):
    account = build_ms_mail_account(
        client_id="client-1",
        tenant="common",
        username="mail@familienhelden.at",
        token_bundle={"access_token": "secret"},
        last_test_ok=last_test_ok,
        protector=_protector,
    )
    save_ms_mail_account(account, approval_token=MS_MAIL_ACCOUNT_SAVE_TOKEN, account_path=path)


def test_ms_mail_activation_gate_requires_token_account_and_smoke(tmp_path) -> None:
    account_path = tmp_path / "ms_mail_account.json"

    blocked = build_ms_mail_read_activation_gate(
        approval_token="ja",
        scanner_smoke_passed=False,
        account_path=account_path,
    )

    assert blocked.allowed is False
    assert "approval_token_invalid" in blocked.blocked_reasons
    assert "scanner_smoke_not_passed" in blocked.blocked_reasons
    assert "ms_mail_account_missing" in blocked.blocked_reasons


def test_ms_mail_activation_gate_allows_read_only_when_account_tested(tmp_path) -> None:
    account_path = tmp_path / "ms_mail_account.json"
    _write_account(account_path)

    gate = build_ms_mail_read_activation_gate(
        approval_token=MS_MAIL_READ_ACTIVATION_TOKEN,
        scanner_smoke_passed=True,
        account_path=account_path,
    )

    assert gate.allowed is True
    assert gate.real_email_enabled is False
    assert gate.external_send_enabled is False


def test_ms_mail_activation_apply_refuses_wrong_config_path(tmp_path) -> None:
    account_path = tmp_path / "ms_mail_account.json"
    config_path = tmp_path / "config.py"
    config_path.write_text("ENABLE_MS_MAIL_READ = False\nENABLE_REAL_EMAIL = False\n", encoding="utf-8")
    _write_account(account_path)

    gate = apply_ms_mail_read_activation_to_config(
        config_path=config_path,
        approval_token=MS_MAIL_READ_ACTIVATION_TOKEN,
        scanner_smoke_passed=True,
        account_path=account_path,
        execute_write=True,
        post_write_validation=lambda _path: True,
    )

    assert gate.allowed is False
    assert "config_path_invalid" in gate.blocked_reasons
