"""Tests for setup status, deterministic calendar extraction and contact category API."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location(
        "friday_api_main_for_setup_calendar_contact_test",
        module_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_setup_status_endpoint_reports_local_only_safety_flags() -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    response = client.get("/api/setup/status")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["app_name"] == "Friday"
    assert payload["local_mode"] is True
    assert payload["safety_flags"]["ENABLE_REAL_EMAIL"] is False
    assert payload["safety_flags"]["ENABLE_REAL_WHATSAPP"] is False
    assert payload["safety_flags"]["ENABLE_REAL_CALENDAR"] is False
    assert payload["calendar"]["real_enabled"] is False
    assert payload["calendar"]["auto_write_enabled"] is False


def test_calendar_extract_event_endpoint_uses_review_only_preview() -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    response = client.post(
        "/api/calendar/extract-event",
        json={
            "text": "Termin am 15.07.2026 um 10:00 im Buero",
            "base_date": "2026-07-09",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["calendar_write_enabled"] is False
    assert payload["review_required"] is True
    assert payload["extraction"]["has_event"] is True
    assert payload["extraction"]["proposed_date"] == "2026-07-15"
    assert payload["extraction"]["proposed_start"] == "10:00"
    assert payload["extraction"]["external_action_used"] is False


def test_contact_category_preview_endpoint_is_local_preview_only() -> None:
    api = _load_api_module()
    client = TestClient(api.app)

    response = client.post(
        "/api/contacts/category-preview",
        json={
            "display_name": "Max",
            "context_text": "Kollege aus dem Projekt",
            "model_raw_category": "arbeit",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["category"] == "arbeit"
    assert payload["preview_only"] is True
    assert payload["persisted"] is False
    assert payload["external_lookup_used"] is False
