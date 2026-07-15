"""Serialized periodic Microsoft-mail read synchronization state."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Mapping


SyncLoader = Callable[[], Awaitable[Mapping[str, Any]]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MailReadSyncScheduler:
    """Run one read-only mail sync at a time and retain a detached status."""

    def __init__(
        self,
        loader: SyncLoader,
        *,
        interval_seconds: int = 15 * 60,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self._loader = loader
        self.interval_seconds = max(60, int(interval_seconds))
        self._clock = clock or _utc_now
        self._lock = asyncio.Lock()
        self._last_started_at: str | None = None
        self._last_completed_at: str | None = None
        self._last_error: str | None = None
        self._last_result: dict[str, Any] | None = None
        self._run_count = 0

    def status(self) -> dict[str, Any]:
        return {
            "running": self._lock.locked(),
            "interval_seconds": self.interval_seconds,
            "run_count": self._run_count,
            "last_started_at": self._last_started_at,
            "last_completed_at": self._last_completed_at,
            "last_error": self._last_error,
            "last_result": deepcopy(self._last_result),
            "read_only": True,
            "external_send_enabled": False,
        }

    async def refresh_once(self) -> dict[str, Any]:
        await self.run_serialized(propagate_errors=False)
        return self.status()

    async def run_serialized(
        self,
        loader: SyncLoader | None = None,
        *,
        propagate_errors: bool = True,
    ) -> dict[str, Any]:
        """Run a manual or scheduled loader under the same process-wide lock."""
        async with self._lock:
            self._last_started_at = self._clock()
            result: dict[str, Any] = {}
            try:
                result = dict(await (loader or self._loader)())
                self._last_result = deepcopy(result)
                self._last_error = None
                self._run_count += 1
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # pragma: no cover - provider boundary
                self._last_error = str(exc)
                if propagate_errors:
                    raise
            finally:
                self._last_completed_at = self._clock()
        return deepcopy(result)

    async def run_forever(self, *, initial_delay_seconds: float = 60) -> None:
        if initial_delay_seconds > 0:
            await asyncio.sleep(initial_delay_seconds)
        while True:
            await self.refresh_once()
            await asyncio.sleep(self.interval_seconds)
