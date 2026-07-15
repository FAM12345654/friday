"""Read-only periodic refresh state for calendar source sync previews."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Awaitable, Callable, Mapping


PreviewLoader = Callable[[], Awaitable[Mapping[str, Any]]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _snapshot_digest(snapshot: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        dict(snapshot),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class CalendarSourceSyncPreviewScheduler:
    """Refresh and retain a source-sync preview without ever executing writes."""

    def __init__(
        self,
        loader: PreviewLoader,
        *,
        interval_seconds: int = 15 * 60,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self._loader = loader
        self.interval_seconds = max(30, int(interval_seconds))
        self._clock = clock or _utc_now
        self._lock = asyncio.Lock()
        self._snapshot: dict[str, Any] | None = None
        self._snapshot_digest = ""
        self._revision = 0
        self._last_started_at: str | None = None
        self._last_completed_at: str | None = None
        self._last_error: str | None = None

    def status(self) -> dict[str, Any]:
        """Return a detached public status payload."""
        return {
            "running": self._lock.locked(),
            "interval_seconds": self.interval_seconds,
            "revision": self._revision,
            "last_started_at": self._last_started_at,
            "last_completed_at": self._last_completed_at,
            "last_error": self._last_error,
            "snapshot": deepcopy(self._snapshot),
            "write_mode": "approval_required",
            "approval_action": "calendar.source_sync.create_batch",
        }

    async def refresh_once(self) -> dict[str, Any]:
        """Perform one serialized read-only refresh and return current status."""
        async with self._lock:
            self._last_started_at = self._clock()
            try:
                loaded = dict(await self._loader())
                digest = _snapshot_digest(loaded)
                if digest != self._snapshot_digest:
                    self._revision += 1
                    self._snapshot = deepcopy(loaded)
                    self._snapshot_digest = digest
                self._last_error = None
                self._last_completed_at = self._clock()
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # pragma: no cover - provider boundary
                self._last_error = str(exc)
                self._last_completed_at = self._clock()
        return self.status()

    async def run_forever(self, *, initial_delay_seconds: float | None = None) -> None:
        """Refresh periodically until the owning application cancels the task."""
        initial_delay = (
            self.interval_seconds
            if initial_delay_seconds is None
            else max(0.0, float(initial_delay_seconds))
        )
        if initial_delay:
            await asyncio.sleep(initial_delay)
        while True:
            await self.refresh_once()
            await asyncio.sleep(self.interval_seconds)
