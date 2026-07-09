"""Preview a possible local Ollama configuration without applying it."""

from __future__ import annotations

from dataclasses import dataclass

from friday import config
from friday.app.local_model_provider import safety_flags_locked
from friday.app.local_ollama_runtime import is_local_ollama_url


DEFAULT_LOCAL_OLLAMA_BASE_URL = "http://localhost:11434"


@dataclass(frozen=True)
class LocalOllamaConfigPreview:
    """Read-only preview for a possible local Ollama configuration."""

    requested_model: str
    requested_base_url: str
    normalized_model: str
    normalized_base_url: str
    base_url_allowed: bool
    model_configured: bool
    would_enable_ollama: bool
    current_ollama_enabled: bool
    current_model: str
    current_base_url: str
    config_change_required: bool
    cloud_fallback_allowed: bool
    product_flow_connected: bool
    external_send_enabled: bool
    external_call_used: bool
    safety_flags_locked: bool
    blocked_reasons: tuple[str, ...]
    suggested_config_lines: tuple[str, ...]
    preview_only: bool = True
    persisted: bool = False


def _normalize_model(model: str | None) -> str:
    return " ".join((model or "").strip().split())


def _normalize_base_url(base_url: str | None) -> str:
    return (base_url or DEFAULT_LOCAL_OLLAMA_BASE_URL).strip().rstrip("/")


def build_local_ollama_config_preview(
    *,
    model: str | None = None,
    base_url: str | None = None,
    enable_requested: bool = True,
) -> LocalOllamaConfigPreview:
    """Preview safe local Ollama config values without mutating runtime config."""
    normalized_model = _normalize_model(model)
    normalized_base_url = _normalize_base_url(base_url)
    base_url_allowed = is_local_ollama_url(normalized_base_url)
    locked = safety_flags_locked()

    blocked_reasons: list[str] = []
    if not enable_requested:
        blocked_reasons.append("Ollama enable was not requested")
    if not normalized_model:
        blocked_reasons.append("Ollama model is not configured")
    if not base_url_allowed:
        blocked_reasons.append("Ollama base URL is not local")
    if not locked:
        blocked_reasons.append("External action safety flags are not locked")

    suggested_lines = (
        "ENABLE_LOCAL_OLLAMA = True",
        f'OLLAMA_BASE_URL = "{normalized_base_url}"',
        f'OLLAMA_MODEL = "{normalized_model}"',
    )

    would_enable = not blocked_reasons
    config_change_required = (
        config.ENABLE_LOCAL_OLLAMA != would_enable
        or config.OLLAMA_BASE_URL.strip().rstrip("/") != normalized_base_url
        or config.OLLAMA_MODEL.strip() != normalized_model
    )

    return LocalOllamaConfigPreview(
        requested_model=model or "",
        requested_base_url=base_url or "",
        normalized_model=normalized_model,
        normalized_base_url=normalized_base_url,
        base_url_allowed=base_url_allowed,
        model_configured=bool(normalized_model),
        would_enable_ollama=would_enable,
        current_ollama_enabled=config.ENABLE_LOCAL_OLLAMA,
        current_model=config.OLLAMA_MODEL,
        current_base_url=config.OLLAMA_BASE_URL,
        config_change_required=config_change_required,
        cloud_fallback_allowed=False,
        product_flow_connected=True,
        external_send_enabled=False,
        external_call_used=False,
        safety_flags_locked=locked,
        blocked_reasons=tuple(dict.fromkeys(blocked_reasons)),
        suggested_config_lines=suggested_lines,
    )
