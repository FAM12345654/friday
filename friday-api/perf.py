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

    async def get_or_set(self, key: Any, factory: Callable[[], Any]) -> Any:
        """Return cached value or run exactly one in-flight factory for a missing key."""
        now = time.monotonic()
        with self._lock:
            cached = self._items.get(key)
            if cached is not None and cached[0] > now:
                return cached[1]
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

    def invalidate_prefix(self, prefix: Any) -> None:
        """Drop cached entries whose tuple key starts with prefix."""
        with self._lock:
            for key in tuple(self._items):
                if isinstance(key, tuple) and isinstance(prefix, tuple):
                    if key[: len(prefix)] == prefix:
                        self._items.pop(key, None)
                elif key == prefix:
                    self._items.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


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
        response.headers["Server-Timing"] = f"app;dur={duration_ms:.2f}"
        logger.info(
            "request endpoint=%s method=%s status=%s duration_ms=%.2f",
            endpoint,
            request.method,
            response.status_code,
            duration_ms,
        )
        return response
