"""Tests for Friday API local AI status endpoint."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location("friday_api_main_for_ai_status_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_api_ai_status_reports_mock_default_without_health_check() -> None:
    api = _load_api_module()

    response = api.get_ai_status(run_health_check=False)

    assert response["ok"] is True
    payload = response["data"]
    assert payload["active_provider"] == "mock"
    assert payload["mock_fallback_active"] is True
    assert payload["ollama_enabled"] is True
    assert payload["configured_model"] == "qwen3:8b"
    assert payload["fallback_count"] >= 0
    assert payload["external_send_enabled"] is False
    assert payload["cloud_fallback_allowed"] is False
    assert payload["product_flow_connected"] is True
