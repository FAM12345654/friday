"""Read-only activation gate for Friday's optional local Ollama runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from friday import config
from friday.app.local_model_provider import safety_flags_locked
from friday.app.local_ollama_runtime import OllamaHealthResult, check_ollama_health, is_local_ollama_url


@dataclass(frozen=True)
class LocalOllamaActivationGate:
    """Read-only status for the optional local Ollama provider."""

    status: str
    active_provider: str
    mock_fallback_active: bool
    ollama_enabled: bool
    model_configured: bool
    base_url: str
    base_url_allowed: bool
    health_check_requested: bool
    health_available: bool
    health_error: str | None
    external_call_used: bool
    cloud_fallback_allowed: bool
    product_flow_connected: bool
    external_send_enabled: bool
    safety_flags_locked: bool
    blocked_reasons: tuple[str, ...]
    required_next_steps: tuple[str, ...]
    preview_only: bool = True
    persisted: bool = False


def _status_from_blockers(blocked_reasons: tuple[str, ...], health_check_requested: bool) -> str:
    if not blocked_reasons:
        return "ollama_ready_for_local_drafts"
    if "ENABLE_LOCAL_OLLAMA is False" in blocked_reasons:
        return "mock_active_ollama_disabled"
    if "Ollama model is not configured" in blocked_reasons:
        return "mock_active_model_missing"
    if "Ollama base URL is not local" in blocked_reasons:
        return "blocked_non_local_url"
    if health_check_requested:
        return "mock_active_ollama_unavailable"
    return "mock_active_health_not_checked"


def build_local_ollama_activation_gate(
    *,
    run_health_check: bool = False,
    health_check: Callable[[str, int], OllamaHealthResult] | None = None,
) -> LocalOllamaActivationGate:
    """Return read-only local Ollama readiness without changing runtime config."""
    base_url = config.OLLAMA_BASE_URL.strip()
    model_configured = bool(config.OLLAMA_MODEL.strip())
    base_url_allowed = is_local_ollama_url(base_url)
    locked = safety_flags_locked()
    blocked_reasons: list[str] = []

    if not config.ENABLE_LOCAL_OLLAMA:
        blocked_reasons.append("ENABLE_LOCAL_OLLAMA is False")
    if not model_configured:
        blocked_reasons.append("Ollama model is not configured")
    if not base_url_allowed:
        blocked_reasons.append("Ollama base URL is not local")
    if not locked:
        blocked_reasons.append("External action safety flags are not locked")

    health_available = False
    health_error: str | None = None
    external_call_used = False
    if run_health_check and not blocked_reasons:
        checker = health_check or check_ollama_health
        result = checker(base_url, config.OLLAMA_TIMEOUT_SECONDS)
        health_available = result.available
        health_error = result.error
        external_call_used = result.external_call_used
        if not result.available:
            blocked_reasons.append("Ollama health check is not available")
    elif not run_health_check:
        blocked_reasons.append("Ollama health check was not requested")

    blockers = tuple(dict.fromkeys(blocked_reasons))
    ollama_ready = not blockers

    return LocalOllamaActivationGate(
        status=_status_from_blockers(blockers, run_health_check),
        active_provider="ollama" if ollama_ready else "mock",
        mock_fallback_active=not ollama_ready,
        ollama_enabled=config.ENABLE_LOCAL_OLLAMA,
        model_configured=model_configured,
        base_url=base_url,
        base_url_allowed=base_url_allowed,
        health_check_requested=run_health_check,
        health_available=health_available,
        health_error=health_error,
        external_call_used=external_call_used,
        cloud_fallback_allowed=False,
        product_flow_connected=True,
        external_send_enabled=False,
        safety_flags_locked=locked,
        blocked_reasons=blockers,
        required_next_steps=(
            "Install Ollama locally on this Windows PC",
            "Pull a local model, for example llama3.1",
            "Keep OLLAMA_BASE_URL on localhost or 127.0.0.1",
            "Enable Friday's local Ollama flag only after a separate safety confirmation",
            "Keep all message sending disabled until a later provider-send gate",
        ),
    )
