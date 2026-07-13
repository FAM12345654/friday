"""Tests for the shared performance helpers (TTL cache + ETag responses)."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

import perf
from perf import TTLCache, etag_response


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# TTLCache basics
# ---------------------------------------------------------------------------


def test_get_or_set_caches_value_and_calls_factory_once() -> None:
    cache = TTLCache(ttl=60)
    calls = 0

    def factory() -> str:
        nonlocal calls
        calls += 1
        return "value"

    async def scenario() -> tuple[str, str]:
        first = await cache.get_or_set("key", factory)
        second = await cache.get_or_set("key", factory)
        return first, second

    first, second = _run(scenario())
    assert first == "value"
    assert second == "value"
    assert calls == 1


def test_get_or_set_supports_async_factory() -> None:
    cache = TTLCache(ttl=60)

    async def factory() -> str:
        await asyncio.sleep(0)
        return "async-value"

    assert _run(cache.get_or_set("key", factory)) == "async-value"


def test_expired_entry_is_refreshed(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = TTLCache(ttl=10)
    now = 1000.0
    monkeypatch.setattr(perf.time, "monotonic", lambda: now)

    calls = 0

    def factory() -> int:
        nonlocal calls
        calls += 1
        return calls

    assert _run(cache.get_or_set("key", factory)) == 1
    # Still fresh: within the TTL window.
    now = 1009.0
    assert _run(cache.get_or_set("key", factory)) == 1
    # Expired: the factory must run again.
    now = 1011.0
    assert _run(cache.get_or_set("key", factory)) == 2
    assert calls == 2


def test_factory_error_is_not_cached() -> None:
    cache = TTLCache(ttl=60)
    calls = 0

    def factory() -> str:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("boom")
        return "recovered"

    with pytest.raises(RuntimeError, match="boom"):
        _run(cache.get_or_set("key", factory))
    assert _run(cache.get_or_set("key", factory)) == "recovered"
    assert calls == 2


def test_single_flight_runs_factory_once_for_concurrent_misses() -> None:
    cache = TTLCache(ttl=60)
    calls = 0

    async def factory() -> str:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.05)
        return "shared"

    async def scenario() -> list[str]:
        return list(
            await asyncio.gather(
                *(cache.get_or_set("key", factory) for _ in range(5))
            )
        )

    results = _run(scenario())
    assert results == ["shared"] * 5
    assert calls == 1


def test_single_flight_propagates_error_to_waiters() -> None:
    cache = TTLCache(ttl=60)

    async def factory() -> str:
        await asyncio.sleep(0.05)
        raise ValueError("shared failure")

    async def scenario() -> list[BaseException]:
        results = await asyncio.gather(
            *(cache.get_or_set("key", factory) for _ in range(3)),
            return_exceptions=True,
        )
        return [r for r in results if isinstance(r, BaseException)]

    errors = _run(scenario())
    assert len(errors) == 3
    assert all(isinstance(e, ValueError) for e in errors)


# ---------------------------------------------------------------------------
# Invalidation
# ---------------------------------------------------------------------------


def _seed(cache: TTLCache, *keys: Any) -> None:
    async def fill() -> None:
        for key in keys:
            await cache.get_or_set(key, lambda key=key: f"value:{key!r}")

    _run(fill())


def _cached_keys(cache: TTLCache) -> set[Any]:
    return set(cache._items)


def test_invalidate_drops_exact_key_only() -> None:
    cache = TTLCache(ttl=60)
    _seed(cache, ("mail", 1), ("mail", 2))
    cache.invalidate(("mail", 1))
    assert _cached_keys(cache) == {("mail", 2)}
    # Unknown keys are a no-op.
    cache.invalidate(("mail", 99))
    assert _cached_keys(cache) == {("mail", 2)}


def test_invalidate_prefix_tuple_keys() -> None:
    cache = TTLCache(ttl=60)
    _seed(cache, ("mail", 1), ("mail", 2), ("dashboard", "today"))
    cache.invalidate_prefix(("mail",))
    assert _cached_keys(cache) == {("dashboard", "today")}


def test_invalidate_prefix_string_keys() -> None:
    cache = TTLCache(ttl=60)
    _seed(cache, "mail:1", "mail:2", "dashboard:today")
    cache.invalidate_prefix("mail:")
    assert _cached_keys(cache) == {"dashboard:today"}


def test_invalidate_prefix_string_prefix_matches_tuple_head() -> None:
    cache = TTLCache(ttl=60)
    _seed(cache, ("mail", 1), ("mailbox", 2), ("calendar", 3))
    cache.invalidate_prefix("mail")
    assert _cached_keys(cache) == {("calendar", 3)}


def test_invalidate_prefix_equality_fallback() -> None:
    cache = TTLCache(ttl=60)
    _seed(cache, 42, 43)
    cache.invalidate_prefix(42)
    assert _cached_keys(cache) == {43}


def test_clear_drops_everything() -> None:
    cache = TTLCache(ttl=60)
    _seed(cache, ("a",), ("b",), "c")
    cache.clear()
    assert _cached_keys(cache) == set()


def test_invalidated_key_reruns_factory() -> None:
    cache = TTLCache(ttl=60)
    calls = 0

    def factory() -> int:
        nonlocal calls
        calls += 1
        return calls

    assert _run(cache.get_or_set(("mail", 1), factory)) == 1
    cache.invalidate_prefix(("mail",))
    assert _run(cache.get_or_set(("mail", 1), factory)) == 2


# ---------------------------------------------------------------------------
# ETag responses
# ---------------------------------------------------------------------------


def test_etag_response_sets_headers_on_response() -> None:
    from fastapi import Response

    response = Response()
    payload = {"items": [1, 2, 3]}
    result = etag_response(payload, if_none_match=None, response=response)
    assert result is payload
    assert response.headers["ETag"].startswith('"')
    assert response.headers["Cache-Control"] == "private, max-age=120"
    assert response.headers["Vary"] == "If-None-Match"


def test_etag_response_returns_304_on_match() -> None:
    from fastapi import Response

    response = Response()
    payload = {"items": [1, 2, 3]}
    etag_response(payload, if_none_match=None, response=response)
    etag = response.headers["ETag"]

    result = etag_response(payload, if_none_match=etag)
    from fastapi import Response as FastAPIResponse

    assert isinstance(result, FastAPIResponse)
    assert result.status_code == 304
    assert result.headers["ETag"] == etag


def test_etag_response_matches_weak_and_wildcard() -> None:
    from fastapi import Response

    response = Response()
    payload = {"a": 1}
    etag_response(payload, if_none_match=None, response=response)
    etag = response.headers["ETag"]

    weak = etag_response(payload, if_none_match=f"W/{etag}")
    wildcard = etag_response(payload, if_none_match="*")
    assert getattr(weak, "status_code", None) == 304
    assert getattr(wildcard, "status_code", None) == 304


def test_etag_response_mismatch_returns_payload() -> None:
    payload = {"a": 1}
    result = etag_response(payload, if_none_match='"different"')
    assert result is payload


def test_etag_is_stable_for_equal_payloads() -> None:
    from fastapi import Response

    first, second = Response(), Response()
    etag_response({"b": 2, "a": 1}, if_none_match=None, response=first)
    etag_response({"a": 1, "b": 2}, if_none_match=None, response=second)
    assert first.headers["ETag"] == second.headers["ETag"]
