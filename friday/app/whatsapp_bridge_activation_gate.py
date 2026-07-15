"""Guarded activation gate for the local WhatsApp read bridge."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from friday import config


WHATSAPP_BRIDGE_ACTIVATION_TOKEN = "WHATSAPP BRIDGE AKTIVIEREN"


@dataclass(frozen=True)
class WhatsAppBridgeActivationGate:
    """Preview result for enabling the read-only WhatsApp bridge."""

    allowed: bool
    blocked_reasons: tuple[str, ...]
    read_enabled_currently: bool
    real_whatsapp_enabled: bool
    required_token: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class WhatsAppBridgeApplyResult:
    """Result of a guarded config apply attempt."""

    allowed: bool
    applied: bool
    message: str
    backup_path: str | None
    blocked_reasons: tuple[str, ...]


def build_whatsapp_bridge_activation_gate(
    *,
    approval_token: str,
    scanner_smoke_passed: bool,
) -> WhatsAppBridgeActivationGate:
    """Build a side-effect-free activation preview."""
    blocked: list[str] = []
    if approval_token != WHATSAPP_BRIDGE_ACTIVATION_TOKEN:
        blocked.append("Token stimmt nicht.")
    if not scanner_smoke_passed:
        blocked.append("Safety Smoke muss PASS sein.")
    if config.ENABLE_REAL_WHATSAPP is not False:
        blocked.append("ENABLE_REAL_WHATSAPP muss False bleiben.")

    return WhatsAppBridgeActivationGate(
        allowed=not blocked,
        blocked_reasons=tuple(blocked),
        read_enabled_currently=config.ENABLE_WHATSAPP_BRIDGE_READ,
        real_whatsapp_enabled=config.ENABLE_REAL_WHATSAPP,
        required_token=WHATSAPP_BRIDGE_ACTIVATION_TOKEN,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def apply_whatsapp_bridge_read_activation_to_config(
    *,
    approval_token: str,
    scanner_smoke_passed: bool,
    config_path: Path | str | None = None,
    execute_write: bool = False,
    post_write_validation: Callable[[Path], bool] | None = None,
) -> WhatsAppBridgeApplyResult:
    """Enable the read bridge flag only through an explicit guarded writer."""
    gate = build_whatsapp_bridge_activation_gate(
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
    )
    if not gate.allowed:
        return WhatsAppBridgeApplyResult(
            allowed=False,
            applied=False,
            message="WhatsApp Read-Bridge wurde nicht freigegeben.",
            backup_path=None,
            blocked_reasons=gate.blocked_reasons,
        )
    if not execute_write:
        return WhatsAppBridgeApplyResult(
            allowed=True,
            applied=False,
            message="Dry Run erfolgreich. Es wurde nichts geschrieben.",
            backup_path=None,
            blocked_reasons=(),
        )

    if post_write_validation is None:
        return WhatsAppBridgeApplyResult(
            allowed=False,
            applied=False,
            message="Post-write Validation fehlt.",
            backup_path=None,
            blocked_reasons=("post_write_validation_required",),
        )

    path = Path(config_path).resolve() if config_path is not None else Path(config.__file__).resolve()
    if path.name != "config.py" or path != (config.PACKAGE_DIR / "config.py").resolve():
        return WhatsAppBridgeApplyResult(
            allowed=False,
            applied=False,
            message="Config-Pfad wurde abgelehnt.",
            backup_path=None,
            blocked_reasons=("config_path_invalid",),
        )
    text = path.read_text(encoding="utf-8")
    old_line = "ENABLE_WHATSAPP_BRIDGE_READ = False"
    new_line = "ENABLE_WHATSAPP_BRIDGE_READ = True"
    if old_line not in text and new_line not in text:
        return WhatsAppBridgeApplyResult(
            allowed=False,
            applied=False,
            message="Config-Zeile fuer WhatsApp Read-Bridge wurde nicht gefunden.",
            backup_path=None,
            blocked_reasons=("Config-Zeile fehlt.",),
        )
    if new_line in text:
        return WhatsAppBridgeApplyResult(
            allowed=True,
            applied=False,
            message="WhatsApp Read-Bridge war bereits aktiviert.",
            backup_path=None,
            blocked_reasons=(),
        )

    backup_path = path.with_suffix(path.suffix + ".whatsapp_bridge_backup")
    backup_path.write_text(text, encoding="utf-8")
    path.write_text(text.replace(old_line, new_line, 1), encoding="utf-8")
    if not post_write_validation(path):
        path.write_text(text, encoding="utf-8")
        return WhatsAppBridgeApplyResult(
            allowed=False,
            applied=False,
            message="Post-write Validation ist fehlgeschlagen; Config wurde zurückgesetzt.",
            backup_path=str(backup_path),
            blocked_reasons=("post_write_validation_failed",),
        )
    return WhatsAppBridgeApplyResult(
        allowed=True,
        applied=True,
        message="WhatsApp Read-Bridge wurde lokal aktiviert.",
        backup_path=str(backup_path),
        blocked_reasons=(),
    )
