"""Tests for the local model provider abstraction and mock implementation."""

from __future__ import annotations

from types import SimpleNamespace

from friday import config
from friday.app.local_model_preview import preview_local_model_response
from friday.app.local_model_provider import (
    MockLocalModelProvider,
    OllamaLocalModelProvider,
    build_local_ai_finalization_gate,
    safety_flags_locked,
    select_local_model_provider,
)


def test_safety_flags_locked_for_local_provider() -> None:
    assert safety_flags_locked() is True


def test_mock_provider_health_check_is_local_only() -> None:
    provider = MockLocalModelProvider()
    health = provider.health_check()

    assert health.provider == "mock"
    assert health.available is True
    assert health.is_mock is True
    assert health.external_call_used is False
    assert health.safety_flags_locked is True


def test_mock_provider_generate_json_returns_deterministic_payload() -> None:
    provider = MockLocalModelProvider()
    result = provider.generate_json(
        prompt="Bitte zusammenfassen",
        schema={"type": "object"},
    )

    assert result.provider == "mock"
    assert result.model == "mock-local-json"
    assert result.prompt == "Bitte zusammenfassen"
    assert result.output["summary"] == "Lokale Mock-Antwort ohne externen Modellaufruf."
    assert result.output["prompt_received"] is True
    assert result.schema == {"type": "object"}
    assert result.is_mock is True
    assert result.external_call_used is False
    assert result.product_flow_connected is False
    assert result.error is None


def test_mock_provider_handles_empty_prompt() -> None:
    provider = MockLocalModelProvider()
    result = provider.generate_json(prompt="   ", schema={})

    assert result.prompt == ""
    assert result.output["prompt_received"] is False
    assert result.external_call_used is False


def test_mock_provider_config_has_no_external_enablement() -> None:
    provider = MockLocalModelProvider()

    assert provider.config.provider == "mock"
    assert provider.config.mode == "local_mock"
    assert provider.config.timeout_seconds == 0
    assert provider.config.external_enabled is False


def test_local_ai_finalization_gate_is_mock_default_and_read_only() -> None:
    gate = build_local_ai_finalization_gate()

    assert gate.status == "finalized_local_ollama_opt_in_configured"
    assert gate.default_provider == "ollama"
    assert gate.mock_provider_default is False
    assert gate.ollama_enabled is True
    assert gate.cloud_fallback_allowed is False
    assert gate.product_flow_connected is True
    assert gate.external_call_used is False
    assert gate.preview_only is True
    assert gate.persisted is False
    assert "mock_provider_default" in gate.completed_checks
    assert "product_flow_uses_guarded_provider_layer" in gate.completed_checks
    assert "model_triggered_obsidian_write" in gate.blocked_actions
    assert "cloud_model_call" in gate.blocked_actions


def test_local_ai_finalization_stays_preview_only_and_mock_only() -> None:
    provider = MockLocalModelProvider()
    provider_result = provider.generate_json("  Hallo  ", {"type": "object"})
    preview = preview_local_model_response("  Hallo  ")

    assert config.ENABLE_LOCAL_OLLAMA is True
    assert config.OLLAMA_MODEL == "qwen3:8b"
    assert config.REQUIRE_USER_APPROVAL is True
    assert config.USE_SQLITE_STORAGE is True

    assert provider_result.output["approval_required"] is True
    assert provider_result.output["provider"] == "mock"
    assert provider_result.external_call_used is False
    assert provider_result.product_flow_connected is False

    assert preview.preview_only is True
    assert preview.product_flow_connected is False
    assert preview.result.is_mock is True
    assert preview.result.external_call_used is False
    assert preview.readiness.provider_config_present is True
    assert preview.readiness.approval_flow_available is True
    assert preview.readiness.safety_flags_locked is True


def test_select_local_model_provider_uses_mock_when_flag_disabled(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_LOCAL_OLLAMA", False)
    monkeypatch.setattr(config, "OLLAMA_MODEL", "local")

    provider = select_local_model_provider()

    assert isinstance(provider, MockLocalModelProvider)


def test_select_local_model_provider_falls_back_to_mock_when_health_fails(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_LOCAL_OLLAMA", True)
    monkeypatch.setattr(config, "OLLAMA_MODEL", "local")

    def _health(*args, **kwargs):
        return SimpleNamespace(available=False, external_call_used=True, error="down")

    provider = select_local_model_provider(health_check=_health)

    assert isinstance(provider, MockLocalModelProvider)


def test_select_local_model_provider_uses_ollama_when_enabled_healthy_and_configured(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_LOCAL_OLLAMA", True)
    monkeypatch.setattr(config, "OLLAMA_MODEL", "local")

    def _health(*args, **kwargs):
        return SimpleNamespace(available=True, external_call_used=True, error=None)

    provider = select_local_model_provider(health_check=_health)

    assert isinstance(provider, OllamaLocalModelProvider)


def test_ollama_provider_returns_validator_error(monkeypatch) -> None:
    monkeypatch.setattr(config, "OLLAMA_MODEL", "local")

    def _generator(**kwargs):
        return SimpleNamespace(
            output={},
            validation_errors=("Pflichtfeld fehlt: summary",),
            external_call_used=True,
            error="Modellantwort wurde durch den Validator blockiert.",
        )

    provider = OllamaLocalModelProvider(
        health_check=lambda *args, **kwargs: SimpleNamespace(available=True, external_call_used=True, error=None),
        generator=_generator,
    )
    result = provider.generate_json("Hallo", {"required": ["summary"]})

    assert result.provider == "ollama"
    assert result.external_call_used is True
    assert result.error == "Modellantwort wurde durch den Validator blockiert."
