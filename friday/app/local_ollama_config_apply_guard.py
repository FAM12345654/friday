"""Guard a future manual Ollama config apply without writing configuration."""

from __future__ import annotations

from dataclasses import dataclass

from friday.app.local_ollama_config_preview import LocalOllamaConfigPreview


OLLAMA_CONFIG_APPLY_TOKEN = "OLLAMA AKTIVIEREN"


@dataclass(frozen=True)
class LocalOllamaConfigApplyGate:
    """Read-only guard result for a future manual Ollama config update."""

    allowed: bool
    status: str
    approval_token_required: str
    model: str
    base_url: str
    scanner_smoke_passed: bool
    health_check_passed: bool
    preview_would_enable_ollama: bool
    manual_edit_required: bool
    config_write_performed: bool
    cloud_fallback_allowed: bool
    external_send_enabled: bool
    external_call_used: bool
    product_flow_connected: bool
    blocked_reasons: tuple[str, ...]
    suggested_config_lines: tuple[str, ...]
    preview_only: bool = True
    persisted: bool = False


def build_local_ollama_config_apply_gate(
    *,
    preview: LocalOllamaConfigPreview,
    approval_token: str | None,
    scanner_smoke_passed: bool,
    health_check_passed: bool,
) -> LocalOllamaConfigApplyGate:
    """Return a guard decision without mutating config.py or runtime state."""
    blocked_reasons: list[str] = []

    if not preview.would_enable_ollama:
        blocked_reasons.append("Ollama config preview is not enable-ready")
        blocked_reasons.extend(preview.blocked_reasons)
    if (approval_token or "").strip() != OLLAMA_CONFIG_APPLY_TOKEN:
        blocked_reasons.append("Ollama config apply token is invalid")
    if not scanner_smoke_passed:
        blocked_reasons.append("Safety smoke must pass before Ollama config apply")
    if not health_check_passed:
        blocked_reasons.append("Local Ollama health check must pass before config apply")

    blockers = tuple(dict.fromkeys(blocked_reasons))
    allowed = not blockers

    return LocalOllamaConfigApplyGate(
        allowed=allowed,
        status="ready_for_manual_config_edit" if allowed else "blocked",
        approval_token_required=OLLAMA_CONFIG_APPLY_TOKEN,
        model=preview.normalized_model,
        base_url=preview.normalized_base_url,
        scanner_smoke_passed=scanner_smoke_passed,
        health_check_passed=health_check_passed,
        preview_would_enable_ollama=preview.would_enable_ollama,
        manual_edit_required=allowed,
        config_write_performed=False,
        cloud_fallback_allowed=False,
        external_send_enabled=False,
        external_call_used=False,
        product_flow_connected=True,
        blocked_reasons=blockers,
        suggested_config_lines=preview.suggested_config_lines,
    )
