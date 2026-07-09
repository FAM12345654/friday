"""Dry-run preview for a future real project Ollama config apply."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from friday.app import local_ollama_real_project_apply_guard as real_project_guard


ROLLBACK_CONFIG_LINES = (
    "ENABLE_LOCAL_OLLAMA = False",
    'OLLAMA_BASE_URL = "http://localhost:11434"',
    'OLLAMA_MODEL = ""',
    "OLLAMA_TIMEOUT_SECONDS = 5",
)


@dataclass(frozen=True)
class LocalOllamaRealProjectApplyPlannedChange:
    """One planned config line change in a dry run."""

    key: str
    current_line: str
    planned_line: str
    changed: bool


@dataclass(frozen=True)
class LocalOllamaRealProjectApplyDryRun:
    """Read-only dry-run result for a future real project config apply."""

    allowed: bool
    status: str
    config_path: str
    model: str
    base_url: str
    timeout_seconds: int
    planned_changes: tuple[LocalOllamaRealProjectApplyPlannedChange, ...]
    rollback_config_lines: tuple[str, ...]
    guard_blocked_reasons: tuple[str, ...]
    required_next_steps: tuple[str, ...]
    config_write_performed: bool
    preview_only: bool
    persisted: bool
    external_call_used: bool
    external_send_enabled: bool
    cloud_fallback_allowed: bool
    product_flow_connected: bool
    message: str


def _assignment_line(config_text: str, key: str) -> str:
    pattern = rf"(?m)^{re.escape(key)}\s*=.*$"
    match = re.search(pattern, config_text)
    return match.group(0) if match else ""


def _planned_changes(
    *,
    config_text: str,
    suggested_config_lines: tuple[str, ...],
) -> tuple[LocalOllamaRealProjectApplyPlannedChange, ...]:
    changes: list[LocalOllamaRealProjectApplyPlannedChange] = []
    for planned_line in suggested_config_lines:
        key = planned_line.split("=", 1)[0].strip()
        current_line = _assignment_line(config_text, key)
        changes.append(
            LocalOllamaRealProjectApplyPlannedChange(
                key=key,
                current_line=current_line,
                planned_line=planned_line,
                changed=current_line != planned_line,
            )
        )
    return tuple(changes)


def build_local_ollama_real_project_apply_dry_run(
    *,
    model: str,
    base_url: str = "http://localhost:11434",
    approval_token: str | None = None,
    scanner_smoke_passed: bool = False,
    health_check_passed: bool = False,
    timeout_seconds: int = 5,
    config_path: str | Path | None = None,
) -> LocalOllamaRealProjectApplyDryRun:
    """Build a dry-run preview without writing config.py."""
    guard = real_project_guard.build_local_ollama_real_project_apply_guard(
        model=model,
        base_url=base_url,
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        health_check_passed=health_check_passed,
        timeout_seconds=timeout_seconds,
        config_path=config_path,
    )

    planned_changes: tuple[LocalOllamaRealProjectApplyPlannedChange, ...] = ()
    if guard.allowed:
        config_text = Path(guard.config_path).read_text(encoding="utf-8")
        planned_changes = _planned_changes(
            config_text=config_text,
            suggested_config_lines=guard.suggested_config_lines,
        )

    return LocalOllamaRealProjectApplyDryRun(
        allowed=guard.allowed,
        status="ready_for_real_project_config_apply_dry_run" if guard.allowed else "blocked",
        config_path=guard.config_path,
        model=guard.model,
        base_url=guard.base_url,
        timeout_seconds=guard.timeout_seconds,
        planned_changes=planned_changes,
        rollback_config_lines=ROLLBACK_CONFIG_LINES,
        guard_blocked_reasons=guard.blocked_reasons,
        required_next_steps=(
            "Review planned config line changes",
            "Confirm rollback lines before any real write",
            "Run Safety Smoke immediately before write",
            "Run local Ollama health check immediately before write",
            "Require exact token OLLAMA AKTIVIEREN",
            "Execute a separate real apply step only after this dry run is accepted",
        ),
        config_write_performed=False,
        preview_only=True,
        persisted=False,
        external_call_used=False,
        external_send_enabled=False,
        cloud_fallback_allowed=False,
        product_flow_connected=False,
        message=(
            "Ollama-Projekt-Apply-Dry-Run ist bereit."
            if guard.allowed
            else "Ollama-Projekt-Apply-Dry-Run wurde blockiert."
        ),
    )


__all__ = [
    "ROLLBACK_CONFIG_LINES",
    "LocalOllamaRealProjectApplyDryRun",
    "LocalOllamaRealProjectApplyPlannedChange",
    "build_local_ollama_real_project_apply_dry_run",
]
