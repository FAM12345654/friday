"""Guarded local Ollama config writer.

This module can update an explicit config.py path with local Ollama settings,
but it is intentionally not connected to CLI or mobile flows. The real project
config is blocked by default so tests can exercise the writer on tmp_path only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Literal

from friday import config
from friday.app.local_ollama_config_apply_guard import (
    OLLAMA_CONFIG_APPLY_TOKEN,
    build_local_ollama_config_apply_gate,
)
from friday.app.local_ollama_config_preview import (
    LocalOllamaConfigPreview,
    build_local_ollama_config_preview,
)


LocalOllamaConfigApplyWriteBlockReason = Literal[
    "guard_blocked",
    "config_path_missing",
    "config_path_not_file",
    "config_filename_invalid",
    "project_config_write_blocked",
    "timeout_seconds_invalid",
    "required_config_line_missing",
    "required_config_line_duplicate",
]

PROJECT_CONFIG_PATH = (config.PACKAGE_DIR / "config.py").resolve()
WRITABLE_CONFIG_NAMES = ("config.py",)
REQUIRED_CONFIG_KEYS = (
    "ENABLE_LOCAL_OLLAMA",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "OLLAMA_TIMEOUT_SECONDS",
)


@dataclass(frozen=True)
class LocalOllamaConfigApplyWriteResult:
    """Result of a guarded local Ollama config write attempt."""

    allowed: bool
    persisted: bool
    config_path: str
    backup_path: str | None
    model: str
    base_url: str
    timeout_seconds: int
    config_write_performed: bool
    preview_only: bool
    external_call_used: bool
    external_send_enabled: bool
    cloud_fallback_allowed: bool
    product_flow_connected: bool
    blocked_reasons: tuple[LocalOllamaConfigApplyWriteBlockReason | str, ...]
    message: str
    written_config_lines: tuple[str, ...]


def _resolved_config_path(config_path: str | Path) -> Path:
    return Path(config_path).expanduser().resolve()


def _assignment_count(config_text: str, key: str) -> int:
    pattern = rf"(?m)^{re.escape(key)}\s*=.*$"
    return len(re.findall(pattern, config_text))


def _replace_assignment(config_text: str, key: str, value: str) -> str:
    pattern = rf"(?m)^({re.escape(key)}\s*=\s*).*$"
    replaced, count = re.subn(pattern, rf"\g<1>{value}", config_text)
    if count != 1:
        return config_text
    return replaced


def _double_quoted(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _blocked_result(
    *,
    config_path: Path,
    preview: LocalOllamaConfigPreview,
    timeout_seconds: int,
    blocked_reasons: tuple[LocalOllamaConfigApplyWriteBlockReason | str, ...],
    message: str,
) -> LocalOllamaConfigApplyWriteResult:
    return LocalOllamaConfigApplyWriteResult(
        allowed=False,
        persisted=False,
        config_path=str(config_path),
        backup_path=None,
        model=preview.normalized_model,
        base_url=preview.normalized_base_url,
        timeout_seconds=timeout_seconds,
        config_write_performed=False,
        preview_only=True,
        external_call_used=False,
        external_send_enabled=False,
        cloud_fallback_allowed=False,
        product_flow_connected=False,
        blocked_reasons=blocked_reasons,
        message=message,
        written_config_lines=(),
    )


def apply_local_ollama_config(
    *,
    config_path: str | Path,
    model: str,
    base_url: str = "http://localhost:11434",
    approval_token: str | None = None,
    scanner_smoke_passed: bool = False,
    health_check_passed: bool = False,
    timeout_seconds: int = 5,
    allow_project_config_write: bool = False,
) -> LocalOllamaConfigApplyWriteResult:
    """Apply safe local Ollama values to an explicit config.py file.

    The function writes only four allowlisted config keys. It does not run an
    Ollama request, does not call cloud providers, and does not send messages.
    """
    resolved_path = _resolved_config_path(config_path)
    preview = build_local_ollama_config_preview(
        model=model,
        base_url=base_url,
        enable_requested=True,
    )
    gate = build_local_ollama_config_apply_gate(
        preview=preview,
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        health_check_passed=health_check_passed,
    )

    if not gate.allowed:
        return _blocked_result(
            config_path=resolved_path,
            preview=preview,
            timeout_seconds=timeout_seconds,
            blocked_reasons=("guard_blocked", *gate.blocked_reasons),
            message="Ollama-Konfiguration wurde nicht geschrieben, weil das Apply-Gate blockiert.",
        )
    if resolved_path.name not in WRITABLE_CONFIG_NAMES:
        return _blocked_result(
            config_path=resolved_path,
            preview=preview,
            timeout_seconds=timeout_seconds,
            blocked_reasons=("config_filename_invalid",),
            message="Ollama-Konfiguration wurde nicht geschrieben, weil nur config.py erlaubt ist.",
        )
    if resolved_path == PROJECT_CONFIG_PATH and not allow_project_config_write:
        return _blocked_result(
            config_path=resolved_path,
            preview=preview,
            timeout_seconds=timeout_seconds,
            blocked_reasons=("project_config_write_blocked",),
            message="Echte Projekt-config.py bleibt ohne separates Apply-Gate blockiert.",
        )
    if not resolved_path.exists():
        return _blocked_result(
            config_path=resolved_path,
            preview=preview,
            timeout_seconds=timeout_seconds,
            blocked_reasons=("config_path_missing",),
            message="Ollama-Konfiguration wurde nicht geschrieben, weil config.py fehlt.",
        )
    if not resolved_path.is_file():
        return _blocked_result(
            config_path=resolved_path,
            preview=preview,
            timeout_seconds=timeout_seconds,
            blocked_reasons=("config_path_not_file",),
            message="Ollama-Konfiguration wurde nicht geschrieben, weil der Pfad keine Datei ist.",
        )
    if timeout_seconds < 1 or timeout_seconds > 60:
        return _blocked_result(
            config_path=resolved_path,
            preview=preview,
            timeout_seconds=timeout_seconds,
            blocked_reasons=("timeout_seconds_invalid",),
            message="Ollama-Konfiguration wurde nicht geschrieben, weil der Timeout ungueltig ist.",
        )

    original_text = resolved_path.read_text(encoding="utf-8")
    missing = tuple(key for key in REQUIRED_CONFIG_KEYS if _assignment_count(original_text, key) == 0)
    duplicates = tuple(key for key in REQUIRED_CONFIG_KEYS if _assignment_count(original_text, key) > 1)
    if missing:
        return _blocked_result(
            config_path=resolved_path,
            preview=preview,
            timeout_seconds=timeout_seconds,
            blocked_reasons=("required_config_line_missing", *missing),
            message="Ollama-Konfiguration wurde nicht geschrieben, weil Pflichtzeilen fehlen.",
        )
    if duplicates:
        return _blocked_result(
            config_path=resolved_path,
            preview=preview,
            timeout_seconds=timeout_seconds,
            blocked_reasons=("required_config_line_duplicate", *duplicates),
            message="Ollama-Konfiguration wurde nicht geschrieben, weil Pflichtzeilen doppelt sind.",
        )

    replacements = {
        "ENABLE_LOCAL_OLLAMA": "True",
        "OLLAMA_BASE_URL": _double_quoted(preview.normalized_base_url),
        "OLLAMA_MODEL": _double_quoted(preview.normalized_model),
        "OLLAMA_TIMEOUT_SECONDS": str(timeout_seconds),
    }
    updated_text = original_text
    for key, value in replacements.items():
        updated_text = _replace_assignment(updated_text, key, value)

    backup_path = resolved_path.with_name(resolved_path.name + ".ollama_apply_backup")
    temp_path = resolved_path.with_name(resolved_path.name + ".ollama_apply_tmp")
    backup_path.write_text(original_text, encoding="utf-8")
    temp_path.write_text(updated_text, encoding="utf-8")
    temp_path.replace(resolved_path)

    written_lines = (
        "ENABLE_LOCAL_OLLAMA = True",
        f'OLLAMA_BASE_URL = "{preview.normalized_base_url}"',
        f'OLLAMA_MODEL = "{preview.normalized_model}"',
        f"OLLAMA_TIMEOUT_SECONDS = {timeout_seconds}",
    )
    return LocalOllamaConfigApplyWriteResult(
        allowed=True,
        persisted=True,
        config_path=str(resolved_path),
        backup_path=str(backup_path),
        model=preview.normalized_model,
        base_url=preview.normalized_base_url,
        timeout_seconds=timeout_seconds,
        config_write_performed=True,
        preview_only=False,
        external_call_used=False,
        external_send_enabled=False,
        cloud_fallback_allowed=False,
        product_flow_connected=False,
        blocked_reasons=(),
        message="Ollama-Konfiguration wurde lokal in die angegebene config.py geschrieben.",
        written_config_lines=written_lines,
    )


__all__ = [
    "OLLAMA_CONFIG_APPLY_TOKEN",
    "LocalOllamaConfigApplyWriteResult",
    "apply_local_ollama_config",
]
