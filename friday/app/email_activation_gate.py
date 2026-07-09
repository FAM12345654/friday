"""Guarded EMAIL AKTIVIEREN preview/dry-run/apply helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable

from friday import config
from friday.app.email_account_store import load_email_account


EMAIL_ACTIVATION_TOKEN = "EMAIL AKTIVIEREN"


@dataclass(frozen=True)
class EmailActivationGate:
    """Read-only decision for activating real email later."""

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
    external_send_enabled: bool


def build_email_activation_gate(
    *,
    approval_token: str,
    scanner_smoke_passed: bool,
    account_path: Path | str | None = None,
) -> EmailActivationGate:
    """Check whether a future EMAIL activation may proceed."""
    account = load_email_account(account_path)
    blocked: list[str] = []
    if approval_token != EMAIL_ACTIVATION_TOKEN:
        blocked.append("approval_token_invalid")
    if not scanner_smoke_passed:
        blocked.append("scanner_smoke_not_passed")
    if account is None:
        blocked.append("email_account_missing")
    elif not account.last_test_ok:
        blocked.append("email_account_test_not_ok")

    allowed = not blocked
    return EmailActivationGate(
        allowed=allowed,
        status="ready_for_email_activation" if allowed else "blocked",
        approval_token_required=EMAIL_ACTIVATION_TOKEN,
        account_connected=account is not None,
        last_test_ok=bool(account and account.last_test_ok),
        scanner_smoke_passed=scanner_smoke_passed,
        config_write_performed=False,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        preview_only=True,
        persisted=False,
        external_send_enabled=False,
    )


def _replace_enable_real_email(config_text: str, value: bool) -> str:
    replacement = f"ENABLE_REAL_EMAIL = {value}"
    updated, count = re.subn(r"(?m)^ENABLE_REAL_EMAIL\s*=.*$", replacement, config_text)
    if count != 1:
        raise ValueError("ENABLE_REAL_EMAIL assignment not unique.")
    return updated


def apply_email_activation_to_config(
    *,
    config_path: Path | str,
    approval_token: str,
    scanner_smoke_passed: bool,
    account_path: Path | str | None = None,
    execute_write: bool = False,
    post_write_validation: Callable[[Path], bool] | None = None,
) -> EmailActivationGate:
    """Apply ENABLE_REAL_EMAIL=True only through the guarded path.

    This helper is intentionally not called automatically by tests, API, CLI or
    mobile. It exists so the user can activate real email later.
    """
    gate = build_email_activation_gate(
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        account_path=account_path,
    )
    if not execute_write:
        return gate
    if not gate.allowed:
        return gate
    if post_write_validation is None:
        return EmailActivationGate(
            **{**gate.__dict__, "allowed": False, "status": "blocked", "blocked_reasons": ("post_write_validation_required",)}
        )

    path = Path(config_path).resolve()
    if path.name != "config.py" or path != (config.PACKAGE_DIR / "config.py").resolve():
        return EmailActivationGate(
            **{**gate.__dict__, "allowed": False, "status": "blocked", "blocked_reasons": ("config_path_invalid",)}
        )
    original = path.read_text(encoding="utf-8")
    backup = path.with_name(path.name + ".email_apply_backup")
    backup.write_text(original, encoding="utf-8")
    path.write_text(_replace_enable_real_email(original, True), encoding="utf-8")
    if not post_write_validation(path):
        path.write_text(original, encoding="utf-8")
        return EmailActivationGate(
            **{**gate.__dict__, "allowed": False, "status": "blocked", "blocked_reasons": ("post_write_validation_failed",)}
        )
    return EmailActivationGate(
        allowed=True,
        status="email_activation_applied",
        approval_token_required=EMAIL_ACTIVATION_TOKEN,
        account_connected=gate.account_connected,
        last_test_ok=gate.last_test_ok,
        scanner_smoke_passed=scanner_smoke_passed,
        config_write_performed=True,
        blocked_reasons=(),
        preview_only=False,
        persisted=True,
        external_send_enabled=True,
    )
