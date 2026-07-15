"""Tests for the WhatsApp read bridge API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from friday.agents.message_agent import MessageAgent
from friday.storage.database import setup_local_database

import importlib.util
from pathlib import Path


def _load_api_module():
    module_path = Path(__file__).resolve().parents[2] / "friday-api" / "main.py"
    spec = importlib.util.spec_from_file_location("friday_api_main_whatsapp_test", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_whatsapp_ingest_blocked_when_read_flag_is_off(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    monkeypatch.setattr(api.config, "ENABLE_WHATSAPP_BRIDGE_READ", False)

    client = TestClient(api.app)
    response = client.post(
        "/api/whatsapp/ingest",
        json={
            "chat_id": "blocked-chat",
            "sender_name": "Kontakt",
            "sender_number": "blocked-number",
            "body": "[redacted]",
            "received_at": "2026-07-09T10:00:00+00:00",
        },
    )

    assert response.status_code == 403


def test_whatsapp_ingest_stores_and_processes_when_enabled(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    monkeypatch.setattr(api.config, "ENABLE_WHATSAPP_BRIDGE_READ", True)
    from friday.app import whatsapp_inbox_store

    bridge_token = "test-whatsapp-bridge-token-with-32-chars"
    token_path = tmp_path / "bridge-token.txt"
    token_path.write_text(bridge_token, encoding="utf-8")
    monkeypatch.setattr(
        whatsapp_inbox_store,
        "get_whatsapp_bridge_token_path",
        lambda: token_path,
    )

    client = TestClient(api.app)
    response = client.post(
        "/api/whatsapp/ingest",
        json={
            "chat_id": "allowed-chat",
            "sender_name": "Kontakt",
            "sender_number": "allowed-number",
            "body": "todo",
            "received_at": "2026-07-09T10:10:00+00:00",
        },
        headers={"X-Friday-WhatsApp-Bridge-Token": bridge_token},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["stored"] is True
    assert payload["send_via_bridge"] is False
    assert payload["processed_count"] == 1

    messages = client.get("/api/whatsapp/messages").json()["data"]
    assert messages["count"] == 1
    assert messages["items"][0]["sender_number_masked"].startswith("hash:")


def test_whatsapp_story_is_ignored_without_storage(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    api.message_agent = MessageAgent(db_path=db_path)
    monkeypatch.setattr(api.config, "ENABLE_WHATSAPP_BRIDGE_READ", True)
    from friday.app import whatsapp_inbox_store

    bridge_token = "test-whatsapp-bridge-token-with-32-chars"
    token_path = tmp_path / "bridge-token.txt"
    token_path.write_text(bridge_token, encoding="utf-8")
    monkeypatch.setattr(
        whatsapp_inbox_store,
        "get_whatsapp_bridge_token_path",
        lambda: token_path,
    )

    client = TestClient(api.app)
    response = client.post(
        "/api/whatsapp/ingest",
        json={
            "chat_id": "status@broadcast",
            "sender_name": "WhatsApp Status",
            "sender_number": "status@broadcast",
            "body": "Diese Story darf nicht gespeichert werden.",
            "received_at": "2026-07-15T10:30:00+00:00",
        },
        headers={"X-Friday-WhatsApp-Bridge-Token": bridge_token},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["stored"] is False
    assert payload["ignored"] is True
    assert payload["ignore_reason"] == "whatsapp_story"
    assert payload["processed_count"] == 0

    messages = client.get("/api/whatsapp/messages").json()["data"]
    assert messages["count"] == 0


def test_whatsapp_activation_gate_requires_hard_token(monkeypatch) -> None:
    api = _load_api_module()
    monkeypatch.setattr(api.config, "ENABLE_REAL_WHATSAPP", False)
    monkeypatch.setattr(api.config, "ENABLE_WHATSAPP_BRIDGE_READ", False)
    client = TestClient(api.app)

    blocked = client.post(
        "/api/whatsapp/activation-gate",
        json={"approval_token": "ja", "scanner_smoke_passed": True},
    ).json()["data"]
    allowed = client.post(
        "/api/whatsapp/activation-gate",
        json={"approval_token": "WHATSAPP BRIDGE AKTIVIEREN", "scanner_smoke_passed": False},
    ).json()["data"]

    assert blocked["allowed"] is False
    assert allowed["allowed"] is True
    assert allowed["server_safety_smoke"]["passed"] is True
    assert allowed["client_smoke_claim_ignored"] is True
