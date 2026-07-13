"""Tests for optional bearer-token auth and runtime metrics."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from perf import RequestMetrics, TTLCache, register_timing
from security import register_auth


def _build_app() -> FastAPI:
    app = FastAPI()
    register_auth(app)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/tasks")
    def tasks() -> dict[str, Any]:
        return {"items": []}

    return app


def test_no_token_configured_allows_everything(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FRIDAY_API_TOKEN", raising=False)
    client = TestClient(_build_app())
    assert client.get("/api/tasks").status_code == 200
    assert client.get("/health").status_code == 200


def test_token_required_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRIDAY_API_TOKEN", "secret-token")
    client = TestClient(_build_app())

    denied = client.get("/api/tasks")
    assert denied.status_code == 401
    assert denied.headers["WWW-Authenticate"] == "Bearer"

    wrong = client.get("/api/tasks", headers={"Authorization": "Bearer nope"})
    assert wrong.status_code == 401

    ok = client.get("/api/tasks", headers={"Authorization": "Bearer secret-token"})
    assert ok.status_code == 200

    header_ok = client.get("/api/tasks", headers={"X-Friday-Token": "secret-token"})
    assert header_ok.status_code == 200


def test_health_and_docs_stay_open(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRIDAY_API_TOKEN", "secret-token")
    client = TestClient(_build_app())
    assert client.get("/health").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_preflight_options_not_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRIDAY_API_TOKEN", "secret-token")
    client = TestClient(_build_app())
    response = client.options(
        "/api/tasks",
        headers={
            "Origin": "http://localhost:19006",
            "Access-Control-Request-Method": "GET",
        },
    )
    # The auth layer must not return 401 for preflight requests.
    assert response.status_code != 401


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def test_cache_stats_track_hits_and_misses() -> None:
    import asyncio

    cache = TTLCache(ttl=60)

    async def scenario() -> None:
        await cache.get_or_set("k", lambda: "v")
        await cache.get_or_set("k", lambda: "v")
        await cache.get_or_set("other", lambda: "w")

    asyncio.run(scenario())
    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 2
    assert stats["entries"] == 2
    assert stats["hit_rate"] == round(1 / 3, 4)


def test_request_metrics_records_counts_and_latency() -> None:
    metrics = RequestMetrics()
    metrics.record("/api/tasks", "GET", 200, 12.5)
    metrics.record("/api/tasks", "GET", 200, 7.5)
    metrics.record("/api/tasks", "GET", 500, 100.0)

    snapshot = metrics.snapshot()
    entry = snapshot["GET /api/tasks"]
    assert entry["count"] == 3
    assert entry["errors"] == 1
    assert entry["avg_ms"] == 40.0
    assert entry["max_ms"] == 100.0


def test_timing_middleware_feeds_request_metrics() -> None:
    import perf

    app = FastAPI()
    register_timing(app)

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"pong": "yes"}

    client = TestClient(app)
    before = perf.request_metrics.snapshot().get("GET /ping", {}).get("count", 0)
    assert client.get("/ping").status_code == 200
    after = perf.request_metrics.snapshot()["GET /ping"]["count"]
    assert after == before + 1
