"""Tests for the SSE event broker and stream."""

from __future__ import annotations

import asyncio
import json
import threading

from events import EventBroker, format_sse, sse_stream


def test_publish_reaches_subscriber() -> None:
    async def scenario() -> dict:
        broker = EventBroker()
        _, queue = broker.subscribe()
        broker.publish("dashboard")
        # publish hops via call_soon_threadsafe; yield control once.
        return await asyncio.wait_for(queue.get(), timeout=1)

    event = asyncio.run(scenario())
    assert event["topic"] == "dashboard"
    assert event["id"] == 1


def test_publish_from_other_thread() -> None:
    async def scenario() -> dict:
        broker = EventBroker()
        _, queue = broker.subscribe()
        thread = threading.Thread(target=broker.publish, args=("mail",))
        thread.start()
        thread.join()
        return await asyncio.wait_for(queue.get(), timeout=1)

    event = asyncio.run(scenario())
    assert event["topic"] == "mail"


def test_unsubscribe_stops_delivery() -> None:
    async def scenario() -> tuple[int, int]:
        broker = EventBroker()
        subscriber_id, queue = broker.subscribe()
        before = broker.subscriber_count()
        broker.unsubscribe(subscriber_id)
        broker.publish("tasks")
        await asyncio.sleep(0)
        return before, queue.qsize()

    before, pending = asyncio.run(scenario())
    assert before == 1
    assert pending == 0


def test_slow_subscriber_drops_oldest_event() -> None:
    async def scenario() -> tuple[int, int]:
        broker = EventBroker()
        _, queue = broker.subscribe()
        from events import MAX_QUEUE_SIZE

        for _ in range(MAX_QUEUE_SIZE + 5):
            broker.publish("mail")
        await asyncio.sleep(0)
        first = await queue.get()
        return first["id"], queue.qsize()

    first_id, remaining = asyncio.run(scenario())
    # The oldest events were dropped, so the first delivered id is > 1.
    assert first_id > 1


def test_format_sse_frame() -> None:
    frame = format_sse({"id": 7, "topic": "calendar", "ts": 123.0})
    assert frame.startswith("id: 7\nevent: change\n")
    payload = json.loads(frame.split("data: ", 1)[1].strip())
    assert payload["topic"] == "calendar"


def test_sse_stream_yields_connect_then_event() -> None:
    async def scenario() -> tuple[str, str]:
        broker = EventBroker()
        stream = sse_stream(broker, keepalive_seconds=5)
        first = await asyncio.wait_for(stream.__anext__(), timeout=1)
        broker.publish("dashboard")
        second = await asyncio.wait_for(stream.__anext__(), timeout=1)
        await stream.aclose()
        return first, second

    first, second = asyncio.run(scenario())
    assert first == ": connected\n\n"
    assert "event: change" in second
    assert '"topic": "dashboard"' in second


def test_sse_stream_sends_keepalive_when_idle() -> None:
    async def scenario() -> str:
        broker = EventBroker()
        stream = sse_stream(broker, keepalive_seconds=0.05)
        await stream.__anext__()  # connected
        frame = await asyncio.wait_for(stream.__anext__(), timeout=1)
        await stream.aclose()
        return frame

    assert asyncio.run(scenario()) == ": keepalive\n\n"


def test_sse_stream_unsubscribes_on_close() -> None:
    async def scenario() -> tuple[int, int]:
        broker = EventBroker()
        stream = sse_stream(broker, keepalive_seconds=5)
        await stream.__anext__()
        during = broker.subscriber_count()
        await stream.aclose()
        return during, broker.subscriber_count()

    during, after = asyncio.run(scenario())
    assert during == 1
    assert after == 0
