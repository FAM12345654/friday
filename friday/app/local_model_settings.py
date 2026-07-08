"""Local model settings preview with mock as the safe default."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from friday import config


LocalModelProviderName = Literal["mock", "ollama"]


@dataclass(frozen=True)
class LocalModelSettings:
    """Read-only settings for local model runtime selection."""

    provider: LocalModelProviderName
    model: str
    base_url: str
    timeout_seconds: int
    mock_is_default: bool
    ollama_enabled: bool
    cloud_fallback_allowed: bool
    product_flow_connected: bool
    preview_only: bool
    persisted: bool
    external_call_used: bool


def build_default_local_model_settings() -> LocalModelSettings:
    """Return the safe default local model settings."""

    return LocalModelSettings(
        provider="mock",
        model="mock-local-json",
        base_url="",
        timeout_seconds=0,
        mock_is_default=True,
        ollama_enabled=False,
        cloud_fallback_allowed=False,
        product_flow_connected=False,
        preview_only=True,
        persisted=False,
        external_call_used=False,
    )


def build_local_model_settings_preview(
    provider: LocalModelProviderName = "mock",
) -> LocalModelSettings:
    """Build local model settings metadata without changing runtime state."""

    if provider == "mock":
        return build_default_local_model_settings()

    return LocalModelSettings(
        provider="ollama",
        model=config.OLLAMA_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        timeout_seconds=config.OLLAMA_TIMEOUT_SECONDS,
        mock_is_default=True,
        ollama_enabled=config.ENABLE_LOCAL_OLLAMA,
        cloud_fallback_allowed=False,
        product_flow_connected=False,
        preview_only=True,
        persisted=False,
        external_call_used=False,
    )
