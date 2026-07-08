"""Tests for the read-only review activity detail view model."""

from __future__ import annotations

from friday.app.review_activity_detail_view import build_review_activity_detail_view


def test_review_activity_detail_view_lists_message_suggestions() -> None:
    view = build_review_activity_detail_view(
        message_suggestions=[
            {
                "id": 1,
                "status": "pending",
                "sender": "Chef",
                "text": "Kannst du morgen den Termin bestaetigen?",
                "updated_at": "2026-07-06T09:00:00",
            }
        ],
        task_suggestions=[],
    )

    assert len(view.message_items) == 1
    item = view.message_items[0]
    assert item.suggestion_type == "message"
    assert item.suggestion_id == 1
    assert item.status == "pending"
    assert item.primary_label == "Chef"
    assert item.excerpt == "Kannst du morgen den Termin bestaetigen?"
    assert item.created_task_id is None


def test_review_activity_detail_view_lists_task_suggestions() -> None:
    view = build_review_activity_detail_view(
        message_suggestions=[],
        task_suggestions=[
            {
                "id": "12",
                "status": "converted",
                "title": "Rechnung pruefen",
                "notes": "Bitte lokal pruefen.",
                "created_task_id": "99",
                "updated_at": "2026-07-06T10:00:00",
            }
        ],
    )

    assert len(view.task_items) == 1
    item = view.task_items[0]
    assert item.suggestion_type == "task"
    assert item.suggestion_id == 12
    assert item.status == "converted"
    assert item.primary_label == "Rechnung pruefen"
    assert item.excerpt == "Bitte lokal pruefen."
    assert item.created_task_id == 99


def test_review_activity_detail_view_sorts_all_items_by_updated_at_then_id() -> None:
    view = build_review_activity_detail_view(
        message_suggestions=[
            {"id": 1, "status": "approved", "sender": "A", "updated_at": "2026-07-06T08:00:00"},
            {"id": 3, "status": "approved", "sender": "C", "updated_at": "2026-07-06T10:00:00"},
        ],
        task_suggestions=[
            {"id": 2, "status": "pending", "title": "B", "updated_at": "2026-07-06T09:00:00"},
            {"id": 4, "status": "pending", "title": "D", "updated_at": "2026-07-06T10:00:00"},
        ],
    )

    assert [item.suggestion_id for item in view.all_items] == [4, 3, 2, 1]


def test_review_activity_detail_view_shortens_long_excerpts() -> None:
    view = build_review_activity_detail_view(
        message_suggestions=[
            {
                "id": 1,
                "status": "pending",
                "sender": "Chef",
                "text": "Das ist ein sehr langer lokaler Text fuer die Vorschau.",
            }
        ],
        task_suggestions=[],
        excerpt_limit=24,
    )

    assert view.message_items[0].excerpt == "Das ist ein sehr lang..."
    assert len(view.message_items[0].excerpt) <= 24


def test_review_activity_detail_view_handles_missing_fields_safely() -> None:
    view = build_review_activity_detail_view(
        message_suggestions=[{}],
        task_suggestions=[{}],
    )

    assert view.message_items[0].suggestion_id is None
    assert view.message_items[0].primary_label == "Unbekannt"
    assert view.message_items[0].status == ""
    assert view.task_items[0].suggestion_id is None
    assert view.task_items[0].primary_label == "Ohne Titel"
    assert view.task_items[0].status == ""


def test_review_activity_detail_view_has_safe_read_only_flags() -> None:
    view = build_review_activity_detail_view(
        message_suggestions=None,
        task_suggestions=None,
    )

    assert view.message_items == ()
    assert view.task_items == ()
    assert view.all_items == ()
    assert view.preview_only is True
    assert view.persisted is False
    assert view.external_action_used is False
