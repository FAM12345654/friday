"""Tests for payload-bound, one-time action approvals."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from friday.app.action_approval_store import ActionApprovalStore
from friday.app.action_approval_store import ActionApprovalCapacityError


def test_approval_is_payload_bound_and_one_time(tmp_path) -> None:
    store = ActionApprovalStore(db_path=tmp_path / "approvals.db")
    payload = {"event_id": "event-1", "calendar_id": "primary"}
    approval = store.issue(action="calendar.delete", payload=payload)

    assert store.consume(
        approval_id=approval.approval_id,
        action="calendar.delete",
        payload=payload,
    ) is True
    assert store.consume(
        approval_id=approval.approval_id,
        action="calendar.delete",
        payload=payload,
    ) is False


def test_payload_mismatch_consumes_invalid_approval(tmp_path) -> None:
    store = ActionApprovalStore(db_path=tmp_path / "approvals.db")
    approval = store.issue(action="calendar.delete", payload={"event_id": "event-1"})

    assert store.consume(
        approval_id=approval.approval_id,
        action="calendar.delete",
        payload={"event_id": "event-2"},
    ) is False
    assert store.consume(
        approval_id=approval.approval_id,
        action="calendar.delete",
        payload={"event_id": "event-1"},
    ) is False


def test_approval_expires(tmp_path) -> None:
    now = [10.0]
    store = ActionApprovalStore(
        ttl_seconds=30,
        clock=lambda: now[0],
        db_path=tmp_path / "approvals.db",
    )
    approval = store.issue(action="push.send", payload={"count": 1})
    now[0] += 31
    assert store.consume(
        approval_id=approval.approval_id,
        action="push.send",
        payload={"count": 1},
    ) is False


def test_only_one_of_multiple_approvals_for_same_action_can_execute(tmp_path) -> None:
    db_path = tmp_path / "approvals.db"
    store = ActionApprovalStore(db_path=db_path)
    payload = {"title": "Termin", "start": "2026-07-15T10:00:00+02:00"}
    approvals = [store.issue(action="calendar.create", payload=payload) for _ in range(8)]

    def consume(approval_id: str) -> bool:
        # A separate store instance models another API worker.
        return ActionApprovalStore(db_path=db_path).consume(
            approval_id=approval_id,
            action="calendar.create",
            payload=payload,
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(consume, [item.approval_id for item in approvals]))

    assert results.count(True) == 1
    assert results.count(False) == 7
    assert store.try_issue(action="calendar.create", payload=payload) is None
    with pytest.raises(RuntimeError, match="bereits freigegeben"):
        store.issue(action="calendar.create", payload=payload)


def test_consumed_operation_can_be_approved_again_after_ttl(tmp_path) -> None:
    now = [10.0]
    store = ActionApprovalStore(
        ttl_seconds=30,
        clock=lambda: now[0],
        db_path=tmp_path / "approvals.db",
    )
    payload = {"count": 1}
    approval = store.issue(action="push.send", payload=payload)
    assert store.consume(
        approval_id=approval.approval_id,
        action="push.send",
        payload=payload,
    )
    assert store.try_issue(action="push.send", payload=payload) is None
    now[0] += 31
    assert store.try_issue(action="push.send", payload=payload) is not None


def test_approval_survives_store_restart_and_is_consumed_once(tmp_path) -> None:
    db_path = tmp_path / "approvals.db"
    payload = {"event_id": "event-1"}
    issued = ActionApprovalStore(db_path=db_path).issue(
        action="calendar.delete",
        payload=payload,
    )

    restarted = ActionApprovalStore(db_path=db_path)
    assert restarted.consume(
        approval_id=issued.approval_id,
        action="calendar.delete",
        payload=payload,
    ) is True
    assert ActionApprovalStore(db_path=db_path).consume(
        approval_id=issued.approval_id,
        action="calendar.delete",
        payload=payload,
    ) is False


def test_capacity_fails_closed_without_evicting_existing_approval(tmp_path) -> None:
    store = ActionApprovalStore(db_path=tmp_path / "approvals.db", max_pending=1)
    first_payload = {"event_id": "first"}
    first = store.issue(action="calendar.delete", payload=first_payload)

    with pytest.raises(ActionApprovalCapacityError, match="offene Einmalfreigaben"):
        store.issue(action="calendar.delete", payload={"event_id": "second"})

    assert store.consume(
        approval_id=first.approval_id,
        action="calendar.delete",
        payload=first_payload,
    ) is True


def test_backward_clock_jump_invalidates_future_approval(tmp_path) -> None:
    now = [100.0]
    store = ActionApprovalStore(
        ttl_seconds=30,
        clock=lambda: now[0],
        db_path=tmp_path / "approvals.db",
    )
    payload = {"count": 1}
    approval = store.issue(action="push.send", payload=payload)

    now[0] = 90.0
    assert store.consume(
        approval_id=approval.approval_id,
        action="push.send",
        payload=payload,
    ) is False
