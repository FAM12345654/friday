"""Server-sent-events broker for Friday live updates.

Clients subscribe to ``GET /api/events`` and receive one SSE message whenever
server-side data changes (dashboard, mail, calendar, tasks, whatsapp). The
payload intentionally carries only the topic and a timestamp — clients react
by refetching through the normal cached endpoints.

``publish`` is safe to call from any thread (endpoint handlers run in the
threadpool); delivery hops onto each subscriber's event loop.
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from typing import Any, AsyncIterator

KEEPALIVE_SECONDS = 15.0
MAX_QUEUE_SIZE = 100

VALID_TOPICS: tuple[str, ...] = ("dashboard", "mail", "calendar", "tasks", "whatsapp")


class EventBroker:
    """Fan-out of change notifications to SSE subscribers."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subscribers: dict[int, tuple[asyncio.AbstractEventLoop, asyncio.Queue]] = {}
        self._next_id = 1
        self._event_counter = 0

    def subscribe(self) -> tuple[int, asyncio.Queue]:
        """Register the calling event loop as a subscriber."""
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
        with self._lock:
            subscriber_id = self._next_id
            self._next_id += 1
            self._subscribers[subscriber_id] = (loop, queue)
        return subscriber_id, queue

    def unsubscribe(self, subscriber_id: int) -> None:
        with self._lock:
            self._subscribers.pop(subscriber_id, None)

    def subscriber_count(self) -> int:
        with self._lock:
            return len(self._subscribers)

    def publish(self, topic: str) -> None:
        """Notify all subscribers that a topic changed. Thread-safe."""
        with self._lock:
            self._event_counter += 1
            event = {
                "id": self._event_counter,
                "topic": topic,
                "ts": time.time(),
            }
            targets = list(self._subscribers.values())
        for loop, queue in targets:
            try:
                loop.call_soon_threadsafe(self._offer, queue, event)
            except RuntimeError:
                # Subscriber loop already closed; it will be dropped on
                # unsubscribe when its request context unwinds.
                continue

    @staticmethod
    def _offer(queue: asyncio.Queue, event: dict[str, Any]) -> None:
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            # Slow client: drop the oldest event, keep the newest.
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass


broker = EventBroker()


def format_sse(event: dict[str, Any]) -> str:
    return f"id: {event['id']}\nevent: change\ndata: {json.dumps(event)}\n\n"


async def sse_stream(
    subscribed_broker: EventBroker | None = None,
    *,
    keepalive_seconds: float = KEEPALIVE_SECONDS,
) -> AsyncIterator[str]:
    """Yield SSE frames for one client until it disconnects."""
    active_broker = subscribed_broker or broker
    subscriber_id, queue = active_broker.subscribe()
    try:
        yield ": connected\n\n"
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=keepalive_seconds)
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"
                continue
            yield format_sse(event)
    finally:
        active_broker.unsubscribe(subscriber_id)
