"""Guarded execution helper for a real local Ollama project config apply."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

from friday.app.local_ollama_config_apply_writer import apply_local_ollama_config
from friday.app.local_ollama_real_project_apply_dry_run import (
    LocalOllamaRealProjectApplyDryRun,
    build_local_ollama_real_project_apply_dry_run,
)


LocalOllamaRealProjectApplyBlockReason = Literal[
    "real_project_apply_execution_not_requested",
    "dry_run_blocked",
    "post_write_validation_required",
    "config_writer_blocked",
    "post_write_validation_failed",
    "post_write_validation_error",
    "rollback_failed",
]


PostWriteValidation = Callable[[Path], bool]


@dataclass(frozen=True)
class LocalOllamaRealProjectApplyResult:
    """Result of a guarded real project config apply attempt."""

    allowed: bool
    persisted: bool
    status: str
    config_path: str
    backup_path: str | None
    model: str
    base_url: str
    timeout_seconds: int
    dry_run_allowed: bool
    config_write_performed: bool
    post_write_validation_passed: bool
    rollback_performed: bool
    preview_only: bool
    external_call_used: bool
    external_send_enabled: bool
    cloud_fallback_allowed: bool
    product_flow_connected: bool
    blocked_reasons: tuple[LocalOllamaRealProjectApplyBlockReason | str, ...]
    message: str
    dry_run: LocalOllamaRealProjectApplyDryRun


def _blocked_result(
    *,
    dry_run: LocalOllamaRealProjectApplyDryRun,
    blocked_reasons: tuple[LocalOllamaRealProjectApplyBlockReason | str, ...],
    message: str,
    backup_path: str | None = None,
    config_write_performed: bool = False,
    rollback_performed: bool = False,
    post_write_validation_passed: bool = False,
) -> LocalOllamaRealProjectApplyResult:
    return LocalOllamaRealProjectApplyResult(
        allowed=False,
        persisted=False,
        status="blocked",
        config_path=dry_run.config_path,
        backup_path=backup_path,
        model=dry_run.model,
        base_url=dry_run.base_url,
        timeout_seconds=dry_run.timeout_seconds,
        dry_run_allowed=dry_run.allowed,
        config_write_performed=config_write_performed,
        post_write_validation_passed=post_write_validation_passed,
        rollback_performed=rollback_performed,
        preview_only=True,
        external_call_used=False,
        external_send_enabled=False,
        cloud_fallback_allowed=False,
        product_flow_connected=False,
        blocked_reasons=blocked_reasons,
        message=message,
        dry_run=dry_run,
    )


def _restore_backup(config_path: Path, backup_path: Path | None) -> bool:
    if backup_path is None or not backup_path.exists() or not backup_path.is_file():
        return False
    config_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
    return True


def execute_local_ollama_real_project_apply(
    *,
    model: str,
    base_url: str = "http://localhost:11434",
    approval_token: str | None = None,
    scanner_smoke_passed: bool = False,
    health_check_passed: bool = False,
    timeout_seconds: int = 5,
    config_path: str | Path | None = None,
    execute_write: bool = False,
    post_write_validation: PostWriteValidation | None = None,
) -> LocalOllamaRealProjectApplyResult:
    """Execute a guarded project config apply only when all gates pass.

    This helper is not connected to CLI, mobile, or API flows. It requires an
    explicit execution flag and a validation callback. If validation fails after
    the config write, the previous config backup is restored immediately.
    """
    dry_run = build_local_ollama_real_project_apply_dry_run(
        model=model,
        base_url=base_url,
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        health_check_passed=health_check_passed,
        timeout_seconds=timeout_seconds,
        config_path=config_path,
    )

    if not execute_write:
        return _blocked_result(
            dry_run=dry_run,
            blocked_reasons=("real_project_apply_execution_not_requested",),
            message="Ollama-Projekt-Apply wurde nicht ausgefuehrt, weil execute_write nicht gesetzt ist.",
        )
    if not dry_run.allowed:
        return _blocked_result(
            dry_run=dry_run,
            blocked_reasons=("dry_run_blocked", *dry_run.guard_blocked_reasons),
            message="Ollama-Projekt-Apply wurde nicht ausgefuehrt, weil der Dry Run blockiert.",
        )
    if post_write_validation is None:
        return _blocked_result(
            dry_run=dry_run,
            blocked_reasons=("post_write_validation_required",),
            message="Ollama-Projekt-Apply wurde nicht ausgefuehrt, weil die Post-Write-Validierung fehlt.",
        )

    write_result = apply_local_ollama_config(
        config_path=dry_run.config_path,
        model=model,
        base_url=base_url,
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        health_check_passed=health_check_passed,
        timeout_seconds=timeout_seconds,
        allow_project_config_write=True,
    )

    if not write_result.persisted:
        return _blocked_result(
            dry_run=dry_run,
            blocked_reasons=("config_writer_blocked", *write_result.blocked_reasons),
            message="Ollama-Projekt-Apply wurde vom Config Writer blockiert.",
            backup_path=write_result.backup_path,
        )

    config_file = Path(write_result.config_path)
    backup_file = Path(write_result.backup_path) if write_result.backup_path else None
    try:
        validation_passed = bool(post_write_validation(config_file))
    except Exception as exc:  # pragma: no cover - exercised by tests, message only
        rollback_performed = _restore_backup(config_file, backup_file)
        reasons: tuple[LocalOllamaRealProjectApplyBlockReason | str, ...] = (
            "post_write_validation_error",
            type(exc).__name__,
        )
        if not rollback_performed:
            reasons = (*reasons, "rollback_failed")
        return _blocked_result(
            dry_run=dry_run,
            blocked_reasons=reasons,
            message="Ollama-Projekt-Apply wurde nach Validierungsfehler zurueckgerollt.",
            backup_path=write_result.backup_path,
            config_write_performed=True,
            rollback_performed=rollback_performed,
        )

    if not validation_passed:
        rollback_performed = _restore_backup(config_file, backup_file)
        reasons: tuple[LocalOllamaRealProjectApplyBlockReason | str, ...] = (
            "post_write_validation_failed",
        )
        if not rollback_performed:
            reasons = (*reasons, "rollback_failed")
        return _blocked_result(
            dry_run=dry_run,
            blocked_reasons=reasons,
            message="Ollama-Projekt-Apply wurde nach fehlgeschlagener Validierung zurueckgerollt.",
            backup_path=write_result.backup_path,
            config_write_performed=True,
            rollback_performed=rollback_performed,
        )

    return LocalOllamaRealProjectApplyResult(
        allowed=True,
        persisted=True,
        status="real_project_config_apply_completed",
        config_path=write_result.config_path,
        backup_path=write_result.backup_path,
        model=write_result.model,
        base_url=write_result.base_url,
        timeout_seconds=write_result.timeout_seconds,
        dry_run_allowed=dry_run.allowed,
        config_write_performed=True,
        post_write_validation_passed=True,
        rollback_performed=False,
        preview_only=False,
        external_call_used=False,
        external_send_enabled=False,
        cloud_fallback_allowed=False,
        product_flow_connected=False,
        blocked_reasons=(),
        message="Ollama-Projekt-Apply wurde lokal ausgefuehrt und validiert.",
        dry_run=dry_run,
    )


__all__ = [
    "LocalOllamaRealProjectApplyResult",
    "execute_local_ollama_real_project_apply",
]
