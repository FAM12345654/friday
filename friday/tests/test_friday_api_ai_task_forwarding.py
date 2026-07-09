"""Tests for the Friday API AI task forwarding draft endpoint."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location("friday_api_main_for_ai_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_api_creates_ai_task_forwarding_draft(monkeypatch) -> None:
    api = _load_api_module()

    monkeypatch.setattr(
        api.task_agent,
        "get_task_by_id",
        lambda task_id: {
            "id": task_id,
            "title": "API Aufgabe weiterleiten",
            "due_date": "2026-07-10",
            "notes": "Bitte lokal pruefen.",
        },
    )
    monkeypatch.setattr(
        api.contact_agent,
        "load_contacts",
        lambda: [
            {
                "id": 4,
                "name": "Mia",
                "email_address": "mia@example.test",
                "whatsapp_target": "+491234",
            }
        ],
    )

    response = api.create_ai_task_forward_draft(
        api.TaskForwardDraftRequest(task_id=2, contact_id=4, channel="email")
    )

    assert response["ok"] is True
    payload = response["data"]
    assert payload["ai_connected"] is True
    assert payload["provider"] == "mock"
    assert payload["product_flow_connected"] is True
    assert payload["external_send_enabled"] is False
    assert payload["approval_token_required"] == "EMAIL SENDEN"
    assert "API Aufgabe weiterleiten" in payload["draft_text"]
