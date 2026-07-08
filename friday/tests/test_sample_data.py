"""Tests to ensure local sample JSON files are present and loadable."""

from __future__ import annotations

import json
from pathlib import Path


def _data_file(filename: str) -> Path:
    base = Path(__file__).resolve().parents[1] / "data"
    return base / filename


def test_sample_files_exist() -> None:
    """Sample data files must exist before Friday starts."""
    expected_files = [
        "sample_tasks.json",
        "sample_messages.json",
        "sample_calendar.json",
        "sample_contacts.json",
    ]
    for filename in expected_files:
        path = _data_file(filename)
        assert path.exists(), f"Fehlende Datei: {filename}"
        assert path.is_file()


def test_sample_data_loads() -> None:
    """All sample files must contain valid JSON arrays with at least one entry."""
    for filename in [
        "sample_tasks.json",
        "sample_messages.json",
        "sample_calendar.json",
        "sample_contacts.json",
    ]:
        path = _data_file(filename)
        with path.open("r", encoding="utf-8") as file:
            content = json.load(file)
        assert isinstance(content, list)
        assert len(content) >= 1, f"Datei hat keine nutzbaren Einträge: {filename}"
