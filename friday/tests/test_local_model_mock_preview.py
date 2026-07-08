"""Tests for local model mock preview functionality."""

from __future__ import annotations

from friday.app.local_model_preview import LocalModelPreview, preview_local_model_response


def test_preview_local_model_response_uses_mock_adapter() -> None:
    preview = preview_local_model_response("Hallo")

    assert isinstance(preview, LocalModelPreview)
    assert preview.preview_only is True
    assert preview.product_flow_connected is False
    assert preview.result.provider == "mock-local"
    assert preview.result.model == "mock-readiness"
    assert preview.result.external_call_used is False


def test_preview_local_model_response_includes_readiness_status() -> None:
    preview = preview_local_model_response("Hallo")

    readiness = preview.readiness
    assert readiness.mode_supported is True
    assert readiness.fallback_path_defined is True
    assert readiness.safety_flags_locked is True


def test_preview_local_model_response_handles_empty_prompt() -> None:
    preview = preview_local_model_response("   ")

    assert preview.prompt == ""
    assert preview.result.is_mock is True
    assert preview.result.external_call_used is False


def test_preview_local_model_response_is_deterministic() -> None:
    first = preview_local_model_response("Ein Test")
    second = preview_local_model_response("Ein Test")

    assert first.result.response == second.result.response
    assert first.result.provider == second.result.provider
    assert first.result.model == second.result.model
    assert first.result.external_call_used is False
    assert second.result.external_call_used is False
