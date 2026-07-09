"""Tests for the local learning API."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from friday.agents.calendar_agent import CalendarAgent
from friday.agents.contact_context_agent import ContactContextAgent
from friday.agents.message_agent import MessageAgent
from friday.agents.task_agent import TaskAgent
from friday.storage.database import get_connection, setup_local_database


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location(
        "friday_api_main_for_learning_test",
        module_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_api(tmp_path):
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file, seed_demo_data=False)
    api = _load_api_module()
    contact_agent = ContactContextAgent(db_path=db_file)
    api.task_agent = TaskAgent(db_path=db_file)
    api.contact_agent = contact_agent
    api.message_agent = MessageAgent(db_path=db_file, contact_agent=contact_agent)
    api.calendar_agent = CalendarAgent(db_path=db_file)
    return api, db_file


def test_learning_endpoint_detects_local_open_questions(tmp_path) -> None:
    api, db_file = _build_api(tmp_path)
    with get_connection(db_file) as connection:
        connection.executemany(
            "INSERT INTO messages (sender, text, received_at, contact_type) VALUES (?, ?, ?, ?)",
            [
                ("Kunde Example <kunde@example.test>", "Bitte Angebot vorbereiten.", "2026-07-09", "email"),
                ("Kunde Example <kunde@example.test>", "Bitte Rueckmeldung.", "2026-07-09", "email"),
            ],
        )
    client = TestClient(api.app)

    response = client.get("/api/learning")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["local_only"] is True
    assert payload["model_training"] is False
    assert payload["external_actions"] is False
    assert payload["open_count"] >= 1
    assert payload["open_questions"][0]["status"] == "open"


def test_learning_answer_creates_rule_and_hides_question(tmp_path) -> None:
    api, db_file = _build_api(tmp_path)
    with get_connection(db_file) as connection:
        connection.executemany(
            "INSERT INTO messages (sender, text, received_at, contact_type) VALUES (?, ?, ?, ?)",
            [
                ("Kunde Example <kunde@example.test>", "Bitte Angebot vorbereiten.", "2026-07-09", "email"),
                ("Kunde Example <kunde@example.test>", "Bitte Rueckmeldung.", "2026-07-09", "email"),
            ],
        )
    client = TestClient(api.app)
    question = client.get("/api/learning").json()["data"]["open_questions"][0]

    response = client.post(
        f"/api/learning/questions/{question['id']}/answer",
        json={"option_id": "kunde_philip"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["result"]["rule"]["kind"] == "sender_contact"
    assert not any(item["id"] == question["id"] for item in payload["open_questions"])
    assert payload["learned_rules"][0]["value"]["betreuer"] == "philip"


def test_learning_rule_can_be_disabled_via_api(tmp_path) -> None:
    api, db_file = _build_api(tmp_path)
    with get_connection(db_file) as connection:
        connection.executemany(
            "INSERT INTO messages (sender, text, received_at, contact_type) VALUES (?, ?, ?, ?)",
            [
                ("Kunde Example <kunde@example.test>", "Bitte Angebot vorbereiten.", "2026-07-09", "email"),
                ("Kunde Example <kunde@example.test>", "Bitte Rueckmeldung.", "2026-07-09", "email"),
            ],
        )
    client = TestClient(api.app)
    question = client.get("/api/learning").json()["data"]["open_questions"][0]
    rule = client.post(
        f"/api/learning/questions/{question['id']}/answer",
        json={"option_id": "kunde_philip"},
    ).json()["data"]["result"]["rule"]

    response = client.patch(f"/api/learning/rules/{rule['id']}", json={"enabled": False})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["rule"]["enabled"] is False
