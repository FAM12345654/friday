"""Preview-only Ollama adapter helpers without network calls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from friday import config


@dataclass(frozen=True)
class OllamaAdapterPreviewConfig:
    """Configuration for a preview-only local Ollama adapter."""

    enabled: bool
    base_url: str
    model: str
    timeout_seconds: int
    allow_cloud_fallback: bool


@dataclass(frozen=True)
class OllamaAdapterPreviewHealth:
    """Health-like preview result that never performs a live check."""

    provider: str
    enabled: bool
    available: bool
    base_url: str
    model: str
    preview_only: bool
    external_call_used: bool
    cloud_fallback_used: bool
    message: str


@dataclass(frozen=True)
class OllamaRequestPreview:
    """A local request preview for a future Ollama JSON generation call."""

    endpoint: str
    payload: dict[str, Any]
    would_call_local: bool
    executed: bool
    preview_only: bool
    external_call_used: bool
    cloud_fallback_used: bool
    product_flow_connected: bool


def default_ollama_preview_config() -> OllamaAdapterPreviewConfig:
    """Return the safe default config from friday.config."""
    return OllamaAdapterPreviewConfig(
        enabled=config.ENABLE_LOCAL_OLLAMA,
        base_url=config.OLLAMA_BASE_URL,
        model=config.OLLAMA_MODEL,
        timeout_seconds=config.OLLAMA_TIMEOUT_SECONDS,
        allow_cloud_fallback=False,
    )


def _is_local_ollama_base_url(base_url: str) -> bool:
    """Return whether a base URL targets the local machine only."""
    value = (base_url or "").strip().lower().rstrip("/")
    allowed_roots = ("http://localhost", "http://127.0.0.1", "http://[::1]")
    return any(
        value == root or value.startswith(f"{root}:") or value.startswith(f"{root}/")
        for root in allowed_roots
    )


def validate_ollama_preview_config(
    preview_config: OllamaAdapterPreviewConfig,
) -> OllamaAdapterPreviewConfig:
    """Validate that the preview config cannot point to cloud endpoints."""
    if preview_config.allow_cloud_fallback:
        raise ValueError("Cloud-Fallback ist fuer Ollama Preview nicht erlaubt.")
    if not _is_local_ollama_base_url(preview_config.base_url):
        raise ValueError("Ollama Preview erlaubt nur lokale Base-URLs.")
    if preview_config.timeout_seconds < 1:
        raise ValueError("Ollama Timeout muss mindestens 1 Sekunde betragen.")
    return preview_config


class OllamaLocalAdapterPreview:
    """Preview-only adapter for a possible future local Ollama integration."""

    provider = "ollama-local-preview"

    def __init__(self, preview_config: OllamaAdapterPreviewConfig | None = None) -> None:
        self.config = validate_ollama_preview_config(
            preview_config or default_ollama_preview_config()
        )

    def health_check(self) -> OllamaAdapterPreviewHealth:
        """Return a stable preview health result without touching the network."""
        if not self.config.enabled:
            return OllamaAdapterPreviewHealth(
                provider=self.provider,
                enabled=False,
                available=False,
                base_url=self.config.base_url,
                model=self.config.model,
                preview_only=True,
                external_call_used=False,
                cloud_fallback_used=False,
                message="Ollama Preview ist deaktiviert.",
            )

        return OllamaAdapterPreviewHealth(
            provider=self.provider,
            enabled=True,
            available=False,
            base_url=self.config.base_url,
            model=self.config.model,
            preview_only=True,
            external_call_used=False,
            cloud_fallback_used=False,
            message="Ollama Preview ist aktiviert, aber es wurde kein Live-Check ausgeführt.",
        )

    def build_json_request_preview(
        self,
        prompt: str,
        schema: Mapping[str, Any],
    ) -> OllamaRequestPreview:
        """Build a future local Ollama request preview without executing it."""
        clean_prompt = (prompt or "").strip()
        endpoint = f"{self.config.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.config.model or "not-configured",
            "prompt": clean_prompt,
            "format": "json",
            "stream": False,
            "schema": dict(schema or {}),
        }

        return OllamaRequestPreview(
            endpoint=endpoint,
            payload=payload,
            would_call_local=self.config.enabled and bool(self.config.model),
            executed=False,
            preview_only=True,
            external_call_used=False,
            cloud_fallback_used=False,
            product_flow_connected=False,
        )
