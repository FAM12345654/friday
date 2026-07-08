"""Preview-only local model health checks without network calls."""

from __future__ import annotations

from dataclasses import dataclass

from friday.app.local_model_settings import LocalModelSettings


@dataclass(frozen=True)
class LocalModelHealthCheckPreview:
    """A non-executing preview of a local model health check."""

    provider: str
    base_url: str
    endpoint: str
    would_check_localhost: bool
    executed: bool
    preview_only: bool
    external_call_used: bool
    product_flow_connected: bool
    blocked_reasons: tuple[str, ...]
    message: str


def _is_127_local_url(base_url: str) -> bool:
    value = (base_url or "").strip().lower().rstrip("/")
    return value == "http://127.0.0.1" or value.startswith("http://127.0.0.1:")


def build_ollama_health_check_preview(
    settings: LocalModelSettings,
) -> LocalModelHealthCheckPreview:
    """Describe a future Ollama health check without performing it."""

    blocked_reasons: list[str] = []
    base_url = (settings.base_url or "").strip().rstrip("/")
    endpoint = f"{base_url}/api/tags" if base_url else ""

    if settings.provider != "ollama":
        blocked_reasons.append("provider_not_ollama")
    if not settings.ollama_enabled:
        blocked_reasons.append("ollama_disabled")
    if not _is_127_local_url(base_url):
        blocked_reasons.append("base_url_not_127_localhost")
    if settings.product_flow_connected:
        blocked_reasons.append("product_flow_connected")
    if settings.cloud_fallback_allowed:
        blocked_reasons.append("cloud_fallback_requested")

    return LocalModelHealthCheckPreview(
        provider=settings.provider,
        base_url=base_url,
        endpoint=endpoint,
        would_check_localhost=not blocked_reasons,
        executed=False,
        preview_only=True,
        external_call_used=False,
        product_flow_connected=False,
        blocked_reasons=tuple(dict.fromkeys(blocked_reasons)),
        message=(
            "Ollama Health Check Preview ist bereit."
            if not blocked_reasons
            else "Ollama Health Check Preview ist blockiert."
        ),
    )
