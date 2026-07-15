"""Tests for the local-LLM voice intent fallback (hermetic, no network)."""

from __future__ import annotations

from typing import Any, Mapping

from friday.app import voice_intent_llm
from friday.app.local_model_provider import (
    MockLocalModelProvider,
    ProviderConfig,
    ProviderResult,
)

TODAY = "2026-07-13"


def _result(output: dict[str, Any], *, error: str | None = None) -> ProviderResult:
    return ProviderResult(
        provider="ollama",
        model="test-model",
        prompt="",
        output=output,
        schema={},
        is_mock=False,
        external_call_used=False,
        product_flow_connected=False,
        error=error,
    )


class FakeProvider:
    """Non-mock provider returning a crafted ProviderResult."""

    def __init__(self, result: ProviderResult) -> None:
        self._result = result
        self.config = ProviderConfig(
            provider="ollama",
            model="test-model",
            mode="local_ollama",
            timeout_seconds=5,
            external_enabled=True,
        )

    def generate_json(self, prompt: str, schema: Mapping[str, Any]) -> ProviderResult:
        return self._result


def test_valid_create_task_mapping() -> None:
    provider = FakeProvider(
        _result({"intent": "create_task", "argument": "Milch kaufen", "language": "de"})
    )
    result = voice_intent_llm.resolve_intent_with_llm(
        "kannst du dir merken dass ich Milch kaufen muss",
        provider=provider,
        today=TODAY,
    )
    assert result is not None
    assert result.intent == "create_task"
    assert result.argument == "Milch kaufen"
    assert result.language == "de"
    assert result.snooze_until is None


def test_language_en_us_normalizes_to_en() -> None:
    # Delegates to voice_synthesis.normalize_language, so region tags collapse.
    provider = FakeProvider(
        _result({"intent": "create_task", "argument": "buy milk", "language": "en-US"})
    )
    result = voice_intent_llm.resolve_intent_with_llm("x", provider=provider, today=TODAY)
    assert result is not None
    assert result.language == "en"


def test_snooze_task_days_offset_arithmetic() -> None:
    provider = FakeProvider(
        _result(
            {
                "intent": "snooze_task",
                "argument": "Steuererklärung",
                "language": "de",
                "days_offset": 7,
            }
        )
    )
    result = voice_intent_llm.resolve_intent_with_llm(
        "kannst du die Steuererklärung auf nächste Woche schieben",
        provider=provider,
        today=TODAY,
    )
    assert result is not None
    assert result.intent == "snooze_task"
    assert result.argument == "Steuererklärung"
    assert result.snooze_until == "2026-07-20"


def test_snooze_days_offset_clamped_and_defaulted() -> None:
    provider = FakeProvider(
        _result({"intent": "snooze_task", "argument": "X", "language": "de", "days_offset": 999})
    )
    clamped = voice_intent_llm.resolve_intent_with_llm("...", provider=provider, today=TODAY)
    assert clamped is not None
    assert clamped.snooze_until == "2026-08-12"  # +30 days

    provider_missing = FakeProvider(
        _result({"intent": "snooze_task", "argument": "X", "language": "de"})
    )
    default = voice_intent_llm.resolve_intent_with_llm("...", provider=provider_missing, today=TODAY)
    assert default is not None
    assert default.snooze_until == "2026-07-14"  # default offset 1


def test_invalid_intent_name_returns_none() -> None:
    provider = FakeProvider(_result({"intent": "delete_everything", "argument": "x", "language": "de"}))
    assert voice_intent_llm.resolve_intent_with_llm("x", provider=provider, today=TODAY) is None


def test_provider_error_returns_none() -> None:
    provider = FakeProvider(
        _result({"intent": "create_task", "argument": "x", "language": "de"}, error="Ollama down")
    )
    assert voice_intent_llm.resolve_intent_with_llm("x", provider=provider, today=TODAY) is None


def test_mock_provider_short_circuits() -> None:
    assert (
        voice_intent_llm.resolve_intent_with_llm(
            "irgendetwas", provider=MockLocalModelProvider(), today=TODAY
        )
        is None
    )


def test_default_provider_is_mock_returns_none(monkeypatch) -> None:
    # select_local_model_provider() yields the mock when Ollama is off.
    monkeypatch.setattr(
        "friday.app.local_model_provider.select_local_model_provider",
        lambda: MockLocalModelProvider(),
    )
    assert voice_intent_llm.resolve_intent_with_llm("irgendetwas", today=TODAY) is None


def test_garbage_output_types_return_none() -> None:
    for bad_output in ("not a dict", ["list"], 42, None):
        provider = FakeProvider(_result({}))  # placeholder, replaced below
        provider._result = _result({})  # type: ignore[assignment]
        provider._result = ProviderResult(  # type: ignore[assignment]
            provider="ollama",
            model="test-model",
            prompt="",
            output=bad_output,  # type: ignore[arg-type]
            schema={},
            is_mock=False,
            external_call_used=False,
            product_flow_connected=False,
            error=None,
        )
        assert voice_intent_llm.resolve_intent_with_llm("x", provider=provider, today=TODAY) is None


def test_empty_text_returns_none() -> None:
    provider = FakeProvider(_result({"intent": "create_task", "argument": "x", "language": "de"}))
    assert voice_intent_llm.resolve_intent_with_llm("   ", provider=provider, today=TODAY) is None
