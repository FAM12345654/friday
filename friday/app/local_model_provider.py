"""Local-only model provider abstraction with deterministic mock implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from friday import config


_FALLBACK_COUNT = 0


@dataclass(frozen=True)
class ProviderConfig:
    """Configuration metadata for a local provider instance."""

    provider: str
    model: str
    mode: str
    timeout_seconds: int
    external_enabled: bool


@dataclass(frozen=True)
class ProviderHealth:
    """Health status for a local provider."""

    provider: str
    model: str
    available: bool
    is_mock: bool
    external_call_used: bool
    safety_flags_locked: bool
    message: str


@dataclass(frozen=True)
class ProviderResult:
    """Structured local provider result."""

    provider: str
    model: str
    prompt: str
    output: dict[str, Any]
    schema: dict[str, Any]
    is_mock: bool
    external_call_used: bool
    product_flow_connected: bool
    error: str | None


@dataclass(frozen=True)
class LocalAIFinalizationGate:
    """Read-only release gate summary for the local AI block."""

    status: str
    default_provider: str
    mock_provider_default: bool
    ollama_enabled: bool
    ollama_base_url: str
    cloud_fallback_allowed: bool
    product_flow_connected: bool
    external_call_used: bool
    completed_checks: tuple[str, ...]
    required_live_call_gates: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    deferred_items: tuple[str, ...]
    preview_only: bool = True
    persisted: bool = False


def safety_flags_locked() -> bool:
    """Return True when all external action flags are disabled."""
    return not any(
        (
            config.ENABLE_REAL_EMAIL,
            config.ENABLE_REAL_WHATSAPP,
            config.ENABLE_REAL_SMS,
            config.ENABLE_REAL_CALENDAR,
            config.ENABLE_REAL_WEATHER,
            config.ENABLE_REAL_MUSIC,
        )
    )


def get_local_model_fallback_count() -> int:
    """Return how often the runtime fell back from enabled Ollama to mock."""
    return _FALLBACK_COUNT


def reset_local_model_fallback_count() -> None:
    """Reset the in-memory fallback counter for focused tests."""
    global _FALLBACK_COUNT
    _FALLBACK_COUNT = 0


def _record_ollama_fallback() -> None:
    global _FALLBACK_COUNT
    _FALLBACK_COUNT += 1


def build_local_ai_finalization_gate() -> LocalAIFinalizationGate:
    """Return the local-only AI release gate status without model calls."""
    ollama_enabled = config.ENABLE_LOCAL_OLLAMA
    product_flow_connected = bool(ollama_enabled and config.OLLAMA_MODEL.strip())

    return LocalAIFinalizationGate(
        status=(
            "finalized_local_ollama_opt_in_configured"
            if product_flow_connected
            else "finalized_mock_ready_live_calls_disabled"
        ),
        default_provider="ollama" if product_flow_connected else "mock",
        mock_provider_default=not product_flow_connected,
        ollama_enabled=ollama_enabled,
        ollama_base_url=config.OLLAMA_BASE_URL,
        cloud_fallback_allowed=False,
        product_flow_connected=product_flow_connected,
        external_call_used=False,
        completed_checks=(
            "mock_provider_default",
            "mock_provider_deterministic",
            "ollama_preview_disabled_by_default",
            "ollama_preview_local_url_only",
            "model_output_validator_available",
            "logic_check_agent_available",
            "product_flow_uses_guarded_provider_layer" if product_flow_connected else "no_product_flow_model_calls",
            "no_cloud_fallback",
        ),
        required_live_call_gates=(
            "ENABLE_LOCAL_OLLAMA must be True",
            "base URL must point to localhost, 127.0.0.1, or ::1",
            "model name must be configured explicitly",
            "request must stay previewed until a separate execution gate exists",
            "model output must pass validator",
            "logic check must not flag risky actions",
            "product flow integration needs a separate release gate",
        ),
        blocked_actions=(
            "openai_call",
            "anthropic_call",
            "cloud_model_call",
            "ollama_live_call_in_product_flow",
            "cloud_fallback",
            "model_output_direct_write",
            "model_triggered_obsidian_write",
            "model_triggered_external_action",
        ),
        deferred_items=(
            "local_ollama_execution_gate",
            "product_flow_integration_gate",
            "model_audit_log",
            "user_selected_model_runtime",
        ),
    )


class LocalModelProvider:
    """Interface-like base for future local model providers."""

    config: ProviderConfig

    def health_check(self) -> ProviderHealth:
        raise NotImplementedError

    def generate_json(self, prompt: str, schema: Mapping[str, Any]) -> ProviderResult:
        raise NotImplementedError


class MockLocalModelProvider(LocalModelProvider):
    """Deterministic provider used as the only active implementation."""

    def __init__(self) -> None:
        self.config = ProviderConfig(
            provider="mock",
            model="mock-local-json",
            mode="local_mock",
            timeout_seconds=0,
            external_enabled=False,
        )

    def health_check(self) -> ProviderHealth:
        """Return local mock health without external calls."""
        return ProviderHealth(
            provider=self.config.provider,
            model=self.config.model,
            available=True,
            is_mock=True,
            external_call_used=False,
            safety_flags_locked=safety_flags_locked(),
            message="Lokaler Mock-Provider ist verfügbar.",
        )

    def generate_json(self, prompt: str, schema: Mapping[str, Any]) -> ProviderResult:
        """Return deterministic JSON-like data without calling a model."""
        clean_prompt = (prompt or "").strip()
        clean_schema = dict(schema or {})
        output = {
            "summary": "Lokale Mock-Antwort ohne externen Modellaufruf.",
            "prompt_received": bool(clean_prompt),
            "approval_required": config.REQUIRE_USER_APPROVAL,
            "provider": self.config.provider,
        }
        return ProviderResult(
            provider=self.config.provider,
            model=self.config.model,
            prompt=clean_prompt,
            output=output,
            schema=clean_schema,
            is_mock=True,
            external_call_used=False,
            product_flow_connected=False,
            error=None,
        )


class OllamaLocalModelProvider(LocalModelProvider):
    """Opt-in local Ollama provider guarded by localhost health checks."""

    def __init__(self, health_check=None, generator=None) -> None:
        from friday.app.local_ollama_runtime import check_ollama_health, generate_ollama_json

        self._health_check = health_check or check_ollama_health
        self._generator = generator or generate_ollama_json
        self.config = ProviderConfig(
            provider="ollama",
            model=config.OLLAMA_MODEL,
            mode="local_ollama",
            timeout_seconds=config.OLLAMA_TIMEOUT_SECONDS,
            external_enabled=config.ENABLE_LOCAL_OLLAMA,
        )

    def health_check(self) -> ProviderHealth:
        result = self._health_check(config.OLLAMA_BASE_URL, config.OLLAMA_TIMEOUT_SECONDS)
        return ProviderHealth(
            provider=self.config.provider,
            model=self.config.model,
            available=result.available,
            is_mock=False,
            external_call_used=result.external_call_used,
            safety_flags_locked=safety_flags_locked(),
            message="Lokales Ollama ist verfügbar." if result.available else (result.error or "Ollama ist nicht verfügbar."),
        )

    def generate_json(self, prompt: str, schema: Mapping[str, Any]) -> ProviderResult:
        result = self._generator(
            prompt=prompt,
            schema=schema,
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL,
            timeout_seconds=config.OLLAMA_TIMEOUT_SECONDS,
        )
        return ProviderResult(
            provider=self.config.provider,
            model=self.config.model,
            prompt=(prompt or "").strip(),
            output=result.output,
            schema=dict(schema or {}),
            is_mock=False,
            external_call_used=result.external_call_used,
            product_flow_connected=False,
            error=result.error or ("; ".join(result.validation_errors) if result.validation_errors else None),
        )


def select_local_model_provider(health_check=None) -> LocalModelProvider:
    """Return Ollama only when explicitly enabled, healthy and configured; otherwise Mock."""
    if not config.ENABLE_LOCAL_OLLAMA or not config.OLLAMA_MODEL.strip():
        return MockLocalModelProvider()
    candidate = OllamaLocalModelProvider(health_check=health_check)
    health = candidate.health_check()
    if not health.available:
        _record_ollama_fallback()
        return MockLocalModelProvider()
    return candidate
