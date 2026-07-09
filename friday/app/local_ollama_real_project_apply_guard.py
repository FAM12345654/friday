"""Read-only guard for a future real project Ollama config apply."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from friday.app.local_ollama_config_apply_guard import (
    OLLAMA_CONFIG_APPLY_TOKEN,
    build_local_ollama_config_apply_gate,
)
from friday.app.local_ollama_config_apply_writer import PROJECT_CONFIG_PATH, REQUIRED_CONFIG_KEYS
from friday.app.local_ollama_config_preview import build_local_ollama_config_preview


@dataclass(frozen=True)
class LocalOllamaRealProjectApplyGuard:
    """Read-only decision for whether a real project config apply may proceed later."""

    allowed: bool
    status: str
    approval_token_required: str
    config_path: str
    project_config_path: str
    config_path_is_project_config: bool
    project_config_exists: bool
    required_config_lines_present: bool
    required_config_lines_unique: bool
    model: str
    base_url: str
    timeout_seconds: int
    scanner_smoke_passed: bool
    health_check_passed: bool
    real_project_write_allowed: bool
    config_write_performed: bool
    preview_only: bool
    persisted: bool
    external_call_used: bool
    external_send_enabled: bool
    cloud_fallback_allowed: bool
    product_flow_connected: bool
    blocked_reasons: tuple[str, ...]
    required_next_steps: tuple[str, ...]
    suggested_config_lines: tuple[str, ...]


def _assignment_count(config_text: str, key: str) -> int:
    pattern = rf"(?m)^{re.escape(key)}\s*=.*$"
    return len(re.findall(pattern, config_text))


def _resolve_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def build_local_ollama_real_project_apply_guard(
    *,
    model: str,
    base_url: str = "http://localhost:11434",
    approval_token: str | None = None,
    scanner_smoke_passed: bool = False,
    health_check_passed: bool = False,
    timeout_seconds: int = 5,
    config_path: str | Path | None = None,
) -> LocalOllamaRealProjectApplyGuard:
    """Return whether a later real project config apply may be allowed.

    This guard does not write config.py and is not connected to CLI, mobile, or
    API apply flows. It only validates the preconditions for a separate future
    apply step.
    """
    project_config = _resolve_path(PROJECT_CONFIG_PATH)
    resolved_config = _resolve_path(config_path or project_config)
    preview = build_local_ollama_config_preview(
        model=model,
        base_url=base_url,
        enable_requested=True,
    )
    apply_gate = build_local_ollama_config_apply_gate(
        preview=preview,
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        health_check_passed=health_check_passed,
    )

    blocked_reasons: list[str] = []
    if not apply_gate.allowed:
        blocked_reasons.append("Ollama config apply gate is blocked")
        blocked_reasons.extend(apply_gate.blocked_reasons)

    config_path_is_project_config = resolved_config == project_config
    project_config_exists = resolved_config.exists() and resolved_config.is_file()
    required_config_lines_present = False
    required_config_lines_unique = False

    if not config_path_is_project_config:
        blocked_reasons.append("Config path is not Friday project config.py")
    if not resolved_config.exists():
        blocked_reasons.append("Friday project config.py is missing")
    elif not resolved_config.is_file():
        blocked_reasons.append("Friday project config.py path is not a file")
    if timeout_seconds < 1 or timeout_seconds > 60:
        blocked_reasons.append("Ollama timeout seconds is invalid")

    if project_config_exists:
        config_text = resolved_config.read_text(encoding="utf-8")
        missing = tuple(
            key for key in REQUIRED_CONFIG_KEYS if _assignment_count(config_text, key) == 0
        )
        duplicates = tuple(
            key for key in REQUIRED_CONFIG_KEYS if _assignment_count(config_text, key) > 1
        )
        required_config_lines_present = not missing
        required_config_lines_unique = not duplicates
        if missing:
            blocked_reasons.append("Required Ollama config line is missing")
            blocked_reasons.extend(missing)
        if duplicates:
            blocked_reasons.append("Required Ollama config line is duplicated")
            blocked_reasons.extend(duplicates)

    blockers = tuple(dict.fromkeys(blocked_reasons))
    allowed = not blockers
    suggested_config_lines = (
        "ENABLE_LOCAL_OLLAMA = True",
        f'OLLAMA_BASE_URL = "{preview.normalized_base_url}"',
        f'OLLAMA_MODEL = "{preview.normalized_model}"',
        f"OLLAMA_TIMEOUT_SECONDS = {timeout_seconds}",
    )

    return LocalOllamaRealProjectApplyGuard(
        allowed=allowed,
        status="ready_for_real_project_config_apply" if allowed else "blocked",
        approval_token_required=OLLAMA_CONFIG_APPLY_TOKEN,
        config_path=str(resolved_config),
        project_config_path=str(project_config),
        config_path_is_project_config=config_path_is_project_config,
        project_config_exists=project_config_exists,
        required_config_lines_present=required_config_lines_present,
        required_config_lines_unique=required_config_lines_unique,
        model=preview.normalized_model,
        base_url=preview.normalized_base_url,
        timeout_seconds=timeout_seconds,
        scanner_smoke_passed=scanner_smoke_passed,
        health_check_passed=health_check_passed,
        real_project_write_allowed=allowed,
        config_write_performed=False,
        preview_only=True,
        persisted=False,
        external_call_used=False,
        external_send_enabled=False,
        cloud_fallback_allowed=False,
        product_flow_connected=False,
        blocked_reasons=blockers,
        required_next_steps=(
            "Run Safety Smoke immediately before any real project config write",
            "Run local Ollama health check immediately before any real project config write",
            "Require exact token OLLAMA AKTIVIEREN",
            "Write only allowlisted Ollama config keys",
            "Run compileall, focus tests, full regression and Safety Smoke after write",
            "Rollback to mock config on any failure",
        ),
        suggested_config_lines=suggested_config_lines,
    )


__all__ = [
    "LocalOllamaRealProjectApplyGuard",
    "build_local_ollama_real_project_apply_guard",
]
