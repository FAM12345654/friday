"""Shared date helpers for Friday's local runtime."""

from __future__ import annotations

from datetime import date

from friday import config


def resolve_today() -> str:
    """Return Friday's effective current date as ISO string."""
    if config.USE_REAL_TODAY:
        return date.today().isoformat()
    return config.DEMO_DATE
