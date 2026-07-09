"""Tests for local calendar view preferences."""

from __future__ import annotations

import pytest

from friday.app.calendar_view_prefs_store import (
    load_calendar_view_prefs,
    save_calendar_view_prefs,
)
from friday.storage.database import setup_local_database


def test_calendar_view_prefs_default_to_today_and_full_day(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path)

    prefs = load_calendar_view_prefs(db_path=db_path)

    assert prefs.range_preset == "heute"
    assert prefs.day_start == "00:00"
    assert prefs.day_end == "23:59"


def test_calendar_view_prefs_roundtrip_custom_range(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path)

    saved = save_calendar_view_prefs(
        range_preset="custom",
        custom_from="2026-07-15",
        custom_to="2026-07-16",
        day_start="08:00",
        day_end="18:00",
        db_path=db_path,
    )
    loaded = load_calendar_view_prefs(db_path=db_path)

    assert saved == loaded
    assert loaded.to_dict()["range_preset"] == "custom"
    assert loaded.custom_from == "2026-07-15"
    assert loaded.custom_to == "2026-07-16"
    assert loaded.day_start == "08:00"
    assert loaded.day_end == "18:00"


def test_calendar_view_prefs_reject_invalid_custom_range(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path)

    with pytest.raises(ValueError):
        save_calendar_view_prefs(
            range_preset="custom",
            custom_from="2026-07-15",
            custom_to=None,
            db_path=db_path,
        )
