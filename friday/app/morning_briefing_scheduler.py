"""APScheduler setup for Friday's nightly morning briefing."""

from __future__ import annotations

from typing import Any, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from friday import config


MORNING_BRIEFING_JOB_ID = "friday-nightly-morning-briefing"


def build_morning_briefing_scheduler() -> AsyncIOScheduler:
    return AsyncIOScheduler(timezone=config.MORNING_BRIEFING_TIMEZONE)


def register_morning_briefing_job(scheduler: AsyncIOScheduler, job: Callable[..., Any]) -> None:
    scheduler.add_job(
        job,
        trigger=CronTrigger(
            hour=config.MORNING_BRIEFING_SCHEDULE_HOUR,
            minute=0,
            timezone=config.MORNING_BRIEFING_TIMEZONE,
        ),
        id=MORNING_BRIEFING_JOB_ID,
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=3600,
    )
