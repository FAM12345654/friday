"""Shared performance helpers for the Friday FastAPI service."""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
import threading
import time
from dataclasses import asdict, is_dataclass
from typing import Any, Callable

from fastapi import Request, Response


logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)


def _json_default(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, (set, tuple)):
        return list(value)
    return str(value)


def _etag_for_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    ).encode("utf-8")
    return f'"{hashlib.sha256(encoded).hexdigest()}"'


def _etag_matches(if_none_match: Any, etag: str) -> bool:
    if not isinstance(if_none_match, str) or not if_none_match:
        return False
    candidates = {item.strip() for item in if_none_match.split(",")}
    return "*" in candidates or etag in candidates or f"W/{etag}" in candidates


def etag_response(
    payload: dict[str, Any],
    *,
    if_none_match: Any = None,
    response: Response | None = None,
    cache_control: str = "private, max-age=120",
) -> dict[str, Any] | Response:
    """Attach ETag headers and return 304 when the client already has the payload."""
    etag = _etag_for_payload(payload)
    headers = {
        "ETag": etag,
        "Cache-Control": cache_control,
        "Vary": "If-None-Match",
    }
    if _etag_matches(if_none_match, etag):
        return Response(status_code=304, headers=headers)
    if response is not None:
        for name, value in headers.items():
            response.headers[name] = value
    return payload


class _Flight:
    def __init__(self) -> None:
        self.done = threading.Event()
        self.value: Any = None
        self.error: BaseException | None = None


class TTLCache:
    """Small in-memory TTL cache with per-key single-flight miss protection."""

    def __init__(self, ttl: float = 120) -> None:
        self.ttl = float(ttl)
        self._items: dict[Any, tuple[float, Any]] = {}
        self._flights: dict[Any, _Flight] = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    async def get_or_set(self, key: Any, factory: Callable[[], Any]) -> Any:
        """Return cached value or run exactly one in-flight factory for a missing key."""
        now = time.monotonic()
        with self._lock:
            cached = self._items.get(key)
            if cached is not None and cached[0] > now:
                self._hits += 1
                return cached[1]
            self._misses += 1
            if cached is not None:
                self._items.pop(key, None)

            flight = self._flights.get(key)
            owner = flight is None
            if owner:
                flight = _Flight()
                self._flights[key] = flight

        assert flight is not None
        if not owner:
            await asyncio.to_thread(flight.done.wait)
            if flight.error is not None:
                raise flight.error
            return flight.value

        try:
            value = factory()
            if inspect.isawaitable(value):
                value = await value
        except BaseException as exc:
            with self._lock:
                flight.error = exc
                self._flights.pop(key, None)
                flight.done.set()
            raise

        with self._lock:
            self._items[key] = (time.monotonic() + self.ttl, value)
            flight.value = value
            self._flights.pop(key, None)
            flight.done.set()
        return value

    def invalidate(self, key: Any) -> None:
        """Drop one cached entry by exact key."""
        with self._lock:
            self._items.pop(key, None)

    def invalidate_prefix(self, prefix: Any) -> None:
        """Drop cached entries whose key starts with prefix.

        Friday currently uses tuple keys, while some call sites and tests may use
        plain string keys. Support both forms without mutating the key iterator.
        """
        with self._lock:
            for key in tuple(self._items):
                if isinstance(key, tuple) and isinstance(prefix, tuple):
                    if key[: len(prefix)] == prefix:
                        self._items.pop(key, None)
                elif isinstance(key, str) and isinstance(prefix, str):
                    if key.startswith(prefix):
                        self._items.pop(key, None)
                elif isinstance(key, tuple) and isinstance(prefix, str):
                    first = key[0] if key else None
                    if isinstance(first, str) and first.startswith(prefix):
                        self._items.pop(key, None)
                elif key == prefix:
                    self._items.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def stats(self) -> dict[str, Any]:
        """Return hit/miss counters and current entry count."""
        with self._lock:
            total = self._hits + self._misses
            return {
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / total, 4) if total else None,
                "entries": len(self._items),
                "ttl_seconds": self.ttl,
            }


class RequestMetrics:
    """Thread-safe per-endpoint request counters for the /metrics endpoint."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._endpoints: dict[str, dict[str, float]] = {}

    def record(self, endpoint: str, method: str, status: int, duration_ms: float) -> None:
        key = f"{method} {endpoint}"
        with self._lock:
            entry = self._endpoints.setdefault(
                key,
                {"count": 0, "errors": 0, "total_ms": 0.0, "max_ms": 0.0},
            )
            entry["count"] += 1
            if status >= 500:
                entry["errors"] += 1
            entry["total_ms"] += duration_ms
            entry["max_ms"] = max(entry["max_ms"], duration_ms)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            result: dict[str, Any] = {}
            for key, entry in sorted(self._endpoints.items()):
                count = int(entry["count"])
                result[key] = {
                    "count": count,
                    "errors": int(entry["errors"]),
                    "avg_ms": round(entry["total_ms"] / count, 2) if count else 0.0,
                    "max_ms": round(entry["max_ms"], 2),
                }
            return result


request_metrics = RequestMetrics()


def register_timing(app: Any) -> None:
    """Register request timing logs and Server-Timing headers on a FastAPI app."""

    @app.middleware("http")
    async def _timing_middleware(request: Request, call_next: Callable[[Request], Any]) -> Response:
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - started_at) * 1000
            route = request.scope.get("route")
            endpoint = getattr(route, "path", request.url.path)
            request_metrics.record(endpoint, request.method, 500, duration_ms)
            logger.exception(
                "request endpoint=%s method=%s status=500 duration_ms=%.2f",
                endpoint,
                request.method,
                duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - started_at) * 1000
        route = request.scope.get("route")
        endpoint = getattr(route, "path", request.url.path)
        request_metrics.record(endpoint, request.method, response.status_code, duration_ms)
        response.headers["Server-Timing"] = f"app;dur={duration_ms:.2f}"
        logger.info(
            "request endpoint=%s method=%s status=%s duration_ms=%.2f",
            endpoint,
            request.method,
            response.status_code,
            duration_ms,
        )
        return response
