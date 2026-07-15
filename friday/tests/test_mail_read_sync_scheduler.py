"""Tests for serialized periodic Microsoft-mail read synchronization."""

from __future__ import annotations

import asyncio

from friday.app.mail_read_sync_scheduler import MailReadSyncScheduler


def test_mail_read_scheduler_serializes_and_records_read_only_result() -> None:
    calls = 0

    async def load():
        nonlocal calls
        calls += 1
        await asyncio.sleep(0)
        return {"stored_count": 2, "read_only": True}

    scheduler = MailReadSyncScheduler(
        load,
        interval_seconds=60,
        clock=lambda: "2026-07-15T12:00:00+00:00",
    )
    first = asyncio.run(scheduler.refresh_once())
    first["last_result"]["stored_count"] = 99
    second = scheduler.status()

    assert calls == 1
    assert first["run_count"] == 1
    assert second["last_result"]["stored_count"] == 2
    assert second["read_only"] is True
    assert second["external_send_enabled"] is False


def test_mail_read_scheduler_retains_failure_without_raising() -> None:
    async def fail():
        raise RuntimeError("token refresh failed")

    scheduler = MailReadSyncScheduler(fail, interval_seconds=60)
    status = asyncio.run(scheduler.refresh_once())

    assert status["run_count"] == 0
    assert status["last_error"] == "token refresh failed"
    assert status["last_completed_at"]


def test_mail_read_scheduler_serializes_manual_and_scheduled_runs() -> None:
    active = 0
    max_active = 0

    async def tracked(result_name: str):
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.01)
        active -= 1
        return {"source": result_name, "read_only": True}

    scheduler = MailReadSyncScheduler(lambda: tracked("scheduled"), interval_seconds=60)

    async def run_both():
        return await asyncio.gather(
            scheduler.refresh_once(),
            scheduler.run_serialized(lambda: tracked("manual")),
        )

    scheduled_status, manual_result = asyncio.run(run_both())

    assert max_active == 1
    assert scheduled_status["run_count"] == 1
    assert manual_result["source"] == "manual"
    assert scheduler.status()["run_count"] == 2
