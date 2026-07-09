"""Tests for local contact category normalization and preview classification."""

from __future__ import annotations

from friday.app.contact_category_classifier import (
    classify_contact_category,
    normalize_contact_category,
)
from friday.config import (
    ENABLE_REAL_CALENDAR,
    ENABLE_REAL_EMAIL,
    ENABLE_REAL_SMS,
    ENABLE_REAL_WHATSAPP,
)


def test_normalize_contact_category_accepts_german_core_categories() -> None:
    assert normalize_contact_category("familie") == "familie"
    assert normalize_contact_category("arbeit") == "arbeit"
    assert normalize_contact_category("freund") == "freund"


def test_normalize_contact_category_maps_english_aliases_to_german_categories() -> None:
    assert normalize_contact_category("family") == "familie"
    assert normalize_contact_category("work") == "arbeit"
    assert normalize_contact_category("friend") == "freund"


def test_classify_contact_category_prefers_model_raw_category_when_safe() -> None:
    preview = classify_contact_category(
        display_name="Max",
        context_text="Projekt",
        model_raw_category="arbeit",
    )

    assert preview.category == "arbeit"
    assert preview.preview_only is True
    assert preview.persisted is False
    assert preview.external_lookup_used is False


def test_classify_contact_category_uses_local_keywords_without_external_actions() -> None:
    preview = classify_contact_category(
        display_name="Anna",
        context_text="Meine Schwester kommt morgen vorbei.",
    )

    assert preview.category == "familie"
    assert ENABLE_REAL_EMAIL is False
    assert ENABLE_REAL_WHATSAPP is False
    assert ENABLE_REAL_SMS is False
    assert ENABLE_REAL_CALENDAR is False

