"""Hermetic test-suite defaults."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _disable_provider_background_schedulers(monkeypatch):
    """Prevent delayed provider reads from escaping a long-running TestClient test."""
    monkeypatch.setenv("FRIDAY_DISABLE_BACKGROUND_SCHEDULERS", "1")
