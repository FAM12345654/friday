"""Tests for local push token storage and Expo push sending."""

from __future__ import annotations

import json

import pytest

from friday import config
from friday.app.push_notifications import (
    build_expo_push_messages,
    build_due_task_notifications,
    is_valid_expo_token,
    list_push_tokens,
    register_push_token,
    remove_push_token,
    send_push_notifications,
)
from friday.storage.database import initialize_database

TOKEN = "ExponentPushToken[abc123DEF-_]"


def _db(tmp_path):
    db_file = tmp_path / "friday.db"
    initialize_database(db_file)
    return db_file


def test_token_validation() -> None:
    assert is_valid_expo_token(TOKEN)
    assert is_valid_expo_token("ExpoPushToken[xyz]")
    assert not is_valid_expo_token("kein-token")
    assert not is_valid_expo_token("")
    assert not is_valid_expo_token("ExponentPushToken[bad chars!]")


def test_register_list_remove_tokens(tmp_path) -> None:
    db = _db(tmp_path)
    assert register_push_token(TOKEN, "android", db_path=db)
    assert not register_push_token("ungueltig", db_path=db)
    # Duplicate registration keeps one row.
    assert register_push_token(TOKEN, "ios", db_path=db)

    tokens = list_push_tokens(db_path=db)
    assert len(tokens) == 1
    assert tokens[0]["token"] == TOKEN
    assert tokens[0]["platform"] == "ios"

    assert remove_push_token(TOKEN, db_path=db)
    assert list_push_tokens(db_path=db) == []
    assert not remove_push_token(TOKEN, db_path=db)


def test_build_due_task_notifications() -> None:
    tasks = [
        {"title": "Heute", "due_date": "2026-07-13", "status": "open"},
        {"title": "Überfällig", "due_date": "2026-07-10", "status": "open"},
        {"title": "Erledigt", "due_date": "2026-07-13", "status": "done"},
        {"title": "Ohne Datum", "due_date": None, "status": "open"},
        {"title": "Zukunft", "due_date": "2026-08-01", "status": "open"},
    ]
    notifications = build_due_task_notifications(tasks, "2026-07-13")
    assert len(notifications) == 2
    assert "1 Aufgabe(n) heute fällig" in notifications[0]["title"]
    assert "Heute" in notifications[0]["body"]
    assert "überfällige" in notifications[1]["title"]
    assert "Überfällig" in notifications[1]["body"]


def test_snoozed_task_does_not_trigger_reminder() -> None:
    tasks = [
        {
            "title": "Überfällig aber snoozed",
            "due_date": "2026-07-10",
            "status": "open",
            "snoozed_until": "2026-07-20",
        },
        {
            "title": "Snooze bereits abgelaufen",
            "due_date": "2026-07-10",
            "status": "open",
            "snoozed_until": "2026-07-12",
        },
    ]
    notifications = build_due_task_notifications(tasks, "2026-07-13")
    assert len(notifications) == 1
    assert "Snooze bereits abgelaufen" in notifications[0]["body"]
    assert "Überfällig aber snoozed" not in notifications[0]["body"]


def test_send_disabled_by_gate(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = _db(tmp_path)
    monkeypatch.setattr(config, "ENABLE_PUSH_NOTIFICATIONS", False, raising=False)
    register_push_token(TOKEN, db_path=db)
    result = send_push_notifications(
        [{"title": "Test"}], db_path=db, poster=lambda *a: (200, b"{}")
    )
    assert not result.ok
    assert not result.external_call_used
    assert "deaktiviert" in result.message


def test_send_with_enabled_flag(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = _db(tmp_path)
    monkeypatch.setattr(config, "ENABLE_PUSH_NOTIFICATIONS", True, raising=False)
    register_push_token(TOKEN, db_path=db)

    captured = {}

    def poster(url, payload, timeout):
        captured["url"] = url
        captured["messages"] = json.loads(payload)
        return 200, b'{"data": []}'

    result = send_push_notifications(
        [{"title": "Friday", "body": "2 Aufgaben fällig"}], db_path=db, poster=poster
    )
    assert result.ok
    assert result.sent == 1
    assert result.external_call_used
    assert captured["url"].startswith("https://exp.host/")
    assert captured["messages"][0]["to"] == TOKEN
    assert captured["messages"][0]["body"] == "2 Aufgaben fällig"


def test_send_without_devices_is_noop(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = _db(tmp_path)
    monkeypatch.setattr(config, "ENABLE_PUSH_NOTIFICATIONS", True, raising=False)
    result = send_push_notifications(
        [{"title": "Test"}], db_path=db, poster=lambda *a: (200, b"{}")
    )
    assert result.ok
    assert result.sent == 0
    assert not result.external_call_used


def test_send_maps_http_error(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = _db(tmp_path)
    monkeypatch.setattr(config, "ENABLE_PUSH_NOTIFICATIONS", True, raising=False)
    register_push_token(TOKEN, db_path=db)
    result = send_push_notifications(
        [{"title": "Test"}], db_path=db, poster=lambda *a: (500, b"")
    )
    assert not result.ok
    assert "500" in result.message


def test_explicit_recipient_snapshot_ignores_later_database_changes(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = _db(tmp_path)
    monkeypatch.setattr(config, "ENABLE_PUSH_NOTIFICATIONS", True, raising=False)
    register_push_token(TOKEN, db_path=db)
    approved_tokens = [TOKEN]
    remove_push_token(TOKEN, db_path=db)
    register_push_token("ExpoPushToken[new-device]", db_path=db)
    captured = {}

    def poster(_url, payload, _timeout):
        captured["messages"] = json.loads(payload)
        return 200, b"{}"

    result = send_push_notifications(
        [{"title": "Friday", "body": "Genehmigt"}],
        db_path=db,
        recipient_tokens=approved_tokens,
        poster=poster,
    )

    assert result.sent == 1
    assert captured["messages"][0]["to"] == TOKEN


def test_push_message_builder_approves_exact_bounded_vector() -> None:
    notifications = [{"title": f"N{i}"} for i in range(60)]
    messages = build_expo_push_messages(
        notifications,
        [TOKEN, "ExpoPushToken[second]"],
    )

    assert len(messages) == 100
    assert messages[0]["to"] == TOKEN
    assert messages[-1]["to"] == "ExpoPushToken[second]"
