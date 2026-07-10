"""Guarded activation gate for read-only IMAP mail sync."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable

from friday import config
from friday.app.imap_mail_account_store import list_imap_mail_accounts, load_imap_mail_account


IMAP_MAIL_READ_ACTIVATION_TOKEN = "MAIL LESEN AKTIVIEREN"


@dataclass(frozen=True)
class ImapMailReadActivationGate:
    """Readiness decision for enabling read-only IMAP mail sync."""

    allowed: bool
    status: str
    approval_token_required: str
    account_connected: bool
    last_test_ok: bool
    scanner_smoke_passed: bool
    blocked_reasons: tuple[str, ...]
    persisted: bool
    read_enabled: bool
    real_email_enabled: bool
    external_send_enabled: bool


def build_imap_mail_read_activation_gate(
    *,
    approval_token: str,
    scanner_smoke_passed: bool,
    account_path: Path | str | None = None,
) -> ImapMailReadActivationGate:
    """Check whether read-only IMAP mail sync can be activated."""
    if account_path is not None:
        account = load_imap_mail_account(account_path)
        accounts = (account,) if account is not None else ()
    else:
        accounts = list_imap_mail_accounts()

    blocked: list[str] = []
    if approval_token != IMAP_MAIL_READ_ACTIVATION_TOKEN:
        blocked.append("approval_token_invalid")
    if not scanner_smoke_passed:
        blocked.append("scanner_smoke_not_passed")
    if not accounts:
        blocked.append("imap_mail_account_missing")
    if accounts and not any(account.last_test_ok for account in accounts):
        blocked.append("imap_mail_login_not_confirmed")
    if config.ENABLE_REAL_EMAIL:
        blocked.append("real_email_send_flag_enabled")

    allowed = not blocked
    return ImapMailReadActivationGate(
        allowed=allowed,
        status="ready_for_imap_mail_read_activation" if allowed else "blocked",
        approval_token_required=IMAP_MAIL_READ_ACTIVATION_TOKEN,
        account_connected=bool(accounts),
        last_test_ok=any(account.last_test_ok for account in accounts),
        scanner_smoke_passed=scanner_smoke_passed,
        blocked_reasons=tuple(blocked),
        persisted=False,
        read_enabled=config.ENABLE_IMAP_MAIL_READ,
        real_email_enabled=config.ENABLE_REAL_EMAIL,
        external_send_enabled=False,
    )


def _replace_enable_imap_mail_read(config_text: str, value: bool) -> str:
    replacement = f"ENABLE_IMAP_MAIL_READ = {value}"
    updated, count = re.subn(r"(?m)^ENABLE_IMAP_MAIL_READ\s*=.*$", replacement, config_text)
    if count != 1:
        raise ValueError("ENABLE_IMAP_MAIL_READ assignment not unique.")
    return updated


def apply_imap_mail_read_activation_to_config(
    *,
    config_path: Path | str,
    approval_token: str,
    scanner_smoke_passed: bool,
    account_path: Path | str | None = None,
    execute_write: bool = False,
    post_write_validation: Callable[[Path], bool] | None = None,
) -> ImapMailReadActivationGate:
    """Apply ENABLE_IMAP_MAIL_READ=True only through the guarded path."""
    gate = build_imap_mail_read_activation_gate(
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        account_path=account_path,
    )
    if not gate.allowed or not execute_write:
        return gate
    if post_write_validation is None:
        return ImapMailReadActivationGate(
            **{**gate.__dict__, "allowed": False, "status": "blocked", "blocked_reasons": ("post_write_validation_required",)}
        )

    path = Path(config_path).resolve()
    if path.name != "config.py" or path != (config.PACKAGE_DIR / "config.py").resolve():
        return ImapMailReadActivationGate(
            **{**gate.__dict__, "allowed": False, "status": "blocked", "blocked_reasons": ("config_path_invalid",)}
        )
    original = path.read_text(encoding="utf-8")
    backup = path.with_suffix(".py.imap_mail_read_activation.bak")
    backup.write_text(original, encoding="utf-8")
    path.write_text(_replace_enable_imap_mail_read(original, True), encoding="utf-8")
    if not post_write_validation(path):
        path.write_text(original, encoding="utf-8")
        return ImapMailReadActivationGate(
            **{**gate.__dict__, "allowed": False, "status": "blocked", "blocked_reasons": ("post_write_validation_failed",)}
        )
    return ImapMailReadActivationGate(
        allowed=True,
        status="imap_mail_read_activation_applied",
        approval_token_required=IMAP_MAIL_READ_ACTIVATION_TOKEN,
        account_connected=gate.account_connected,
        last_test_ok=gate.last_test_ok,
        scanner_smoke_passed=scanner_smoke_passed,
        blocked_reasons=(),
        persisted=True,
        read_enabled=True,
        real_email_enabled=config.ENABLE_REAL_EMAIL,
        external_send_enabled=False,
    )
