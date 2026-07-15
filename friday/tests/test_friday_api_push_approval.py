"""API tests for previewed, payload-bound push delivery approvals."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from friday.app.push_notifications import (
    register_push_token,
    remove_push_token,
)
from friday.storage.database import setup_local_database


TOKEN_A = "ExpoPushToken[approved-device]"
TOKEN_B = "ExpoPushToken[replacement-device]"


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location("friday_api_main_for_push_approval_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _configure_due_task(api, db_path, monkeypatch, *, title: str = "Push-Approval-Test") -> None:
    setup_local_database(db_path)
    api.message_agent.db_path = db_path
    api.task_agent.repository = SimpleNamespace(
        filter_tasks=lambda: [
            {
                "title": title,
                "due_date": "2026-07-15",
                "status": "open",
            }
        ]
    )
    monkeypatch.setattr(api, "_today", lambda: "2026-07-15")
    monkeypatch.setattr(api.config, "ENABLE_PUSH_NOTIFICATIONS", True, raising=False)


def test_push_requires_preview_then_sends_once_to_exact_recipient_snapshot(
    tmp_path,
    monkeypatch,
) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    _configure_due_task(api, db_path, monkeypatch)
    register_push_token(TOKEN_A, db_path=db_path)
    sent_to: list[list[str]] = []

    def fake_send(_notifications, **kwargs):
        sent_to.append(list(kwargs["recipient_tokens"]))
        return SimpleNamespace(
            ok=True,
            sent=1,
            message="gesendet",
            external_call_used=True,
        )

    monkeypatch.setattr(api, "send_push_notifications", fake_send)
    client = TestClient(api.app)

    preview_response = client.post(
        "/api/push/send-due-reminders",
        json={"dry_run": True},
    )
    preview = preview_response.json()["data"]
    assert preview_response.headers["cache-control"] == "no-store"
    assert preview["sent"] == 0
    assert preview["approval"]["payload_bound"] is True
    approval_id = preview["approval"]["id"]

    send_response = client.post(
        "/api/push/send-due-reminders",
        json={
            "dry_run": False,
            "approval_token": "PUSH SENDEN",
            "approval_id": approval_id,
        },
    )
    assert send_response.json()["data"]["sent"] == 1
    assert sent_to == [[TOKEN_A]]

    replay_response = client.post(
        "/api/push/send-due-reminders",
        json={
            "dry_run": False,
            "approval_token": "PUSH SENDEN",
            "approval_id": approval_id,
        },
    )
    assert replay_response.json()["data"]["blocked_reasons"] == [
        "one_time_approval_invalid"
    ]
    assert sent_to == [[TOKEN_A]]


def test_push_approval_is_invalid_after_recipient_change(tmp_path, monkeypatch) -> None:
    api = _load_api_module()
    db_path = tmp_path / "friday.db"
    _configure_due_task(api, db_path, monkeypatch, title="Recipient-Swap-Test")
    register_push_token(TOKEN_A, db_path=db_path)
    calls: list[object] = []
    monkeypatch.setattr(api, "send_push_notifications", lambda *args, **kwargs: calls.append(args))
    client = TestClient(api.app)

    preview = client.post(
        "/api/push/send-due-reminders",
        json={"dry_run": True},
    ).json()["data"]
    remove_push_token(TOKEN_A, db_path=db_path)
    register_push_token(TOKEN_B, db_path=db_path)

    response = client.post(
        "/api/push/send-due-reminders",
        json={
            "dry_run": False,
            "approval_token": "PUSH SENDEN",
            "approval_id": preview["approval"]["id"],
        },
    )

    assert response.json()["data"]["blocked_reasons"] == ["one_time_approval_invalid"]
    assert calls == []
