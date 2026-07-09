"""Guarded activation gate for read-only Microsoft Graph mail sync."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable

from friday import config
from friday.app.ms_mail_account_store import load_ms_mail_account


MS_MAIL_READ_ACTIVATION_TOKEN = "MAIL LESEN AKTIVIEREN"


@dataclass(frozen=True)
class MsMailReadActivationGate:
    """Readiness decision for enabling Microsoft Graph mail read sync."""

    allowed: bool
    status: str
    approval_token_required: str
    account_connected: bool
    last_test_ok: bool
    scanner_smoke_passed: bool
    config_write_performed: bool
    blocked_reasons: tuple[str, ...]
    preview_only: bool
    persisted: bool
    read_enabled: bool
    real_email_enabled: bool
    external_send_enabled: bool


def build_ms_mail_read_activation_gate(
    *,
    approval_token: str,
    scanner_smoke_passed: bool,
    account_path: Path | str | None = None,
) -> MsMailReadActivationGate:
    """Check whether read-only MS mail sync can be activated."""
    account = load_ms_mail_account(account_path)
    blocked: list[str] = []
    if approval_token != MS_MAIL_READ_ACTIVATION_TOKEN:
        blocked.append("approval_token_invalid")
    if not scanner_smoke_passed:
        blocked.append("scanner_smoke_not_passed")
    if account is None:
        blocked.append("ms_mail_account_missing")
    elif not account.last_test_ok:
        blocked.append("ms_mail_account_test_not_ok")
    if config.ENABLE_REAL_EMAIL is not False:
        blocked.append("real_email_must_remain_false")

    allowed = not blocked
    return MsMailReadActivationGate(
        allowed=allowed,
        status="ready_for_ms_mail_read_activation" if allowed else "blocked",
        approval_token_required=MS_MAIL_READ_ACTIVATION_TOKEN,
        account_connected=account is not None,
        last_test_ok=bool(account and account.last_test_ok),
        scanner_smoke_passed=scanner_smoke_passed,
        config_write_performed=False,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        preview_only=True,
        persisted=False,
        read_enabled=config.ENABLE_MS_MAIL_READ,
        real_email_enabled=config.ENABLE_REAL_EMAIL,
        external_send_enabled=False,
    )


def _replace_enable_ms_mail_read(config_text: str, value: bool) -> str:
    replacement = f"ENABLE_MS_MAIL_READ = {value}"
    updated, count = re.subn(r"(?m)^ENABLE_MS_MAIL_READ\s*=.*$", replacement, config_text)
    if count != 1:
        raise ValueError("ENABLE_MS_MAIL_READ assignment not unique.")
    return updated


def apply_ms_mail_read_activation_to_config(
    *,
    config_path: Path | str,
    approval_token: str,
    scanner_smoke_passed: bool,
    account_path: Path | str | None = None,
    execute_write: bool = False,
    post_write_validation: Callable[[Path], bool] | None = None,
) -> MsMailReadActivationGate:
    """Apply ENABLE_MS_MAIL_READ=True only through the guarded path."""
    gate = build_ms_mail_read_activation_gate(
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        account_path=account_path,
    )
    if not execute_write:
        return gate
    if not gate.allowed:
        return gate
    if post_write_validation is None:
        return MsMailReadActivationGate(
            **{**gate.__dict__, "allowed": False, "status": "blocked", "blocked_reasons": ("post_write_validation_required",)}
        )

    path = Path(config_path).resolve()
    if path.name != "config.py" or path != (config.PACKAGE_DIR / "config.py").resolve():
        return MsMailReadActivationGate(
            **{**gate.__dict__, "allowed": False, "status": "blocked", "blocked_reasons": ("config_path_invalid",)}
        )
    original = path.read_text(encoding="utf-8")
    backup = path.with_name(path.name + ".ms_mail_read_apply_backup")
    backup.write_text(original, encoding="utf-8")
    path.write_text(_replace_enable_ms_mail_read(original, True), encoding="utf-8")
    if not post_write_validation(path):
        path.write_text(original, encoding="utf-8")
        return MsMailReadActivationGate(
            **{**gate.__dict__, "allowed": False, "status": "blocked", "blocked_reasons": ("post_write_validation_failed",)}
        )
    return MsMailReadActivationGate(
        allowed=True,
        status="ms_mail_read_activation_applied",
        approval_token_required=MS_MAIL_READ_ACTIVATION_TOKEN,
        account_connected=gate.account_connected,
        last_test_ok=gate.last_test_ok,
        scanner_smoke_passed=scanner_smoke_passed,
        config_write_performed=True,
        blocked_reasons=(),
        preview_only=False,
        persisted=True,
        read_enabled=True,
        real_email_enabled=False,
        external_send_enabled=False,
    )
