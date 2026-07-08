from friday.app.review_batch_selection_parser import parse_review_batch_selection
from friday.app.review_batch_selection_preview import (
    REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE,
    REVIEW_BATCH_SELECTION_PREVIEW_TITLE,
    render_review_batch_selection_preview,
)


def _visible_suggestions() -> list[dict]:
    return [
        {
            "id": 1,
            "sender": "Chef",
            "title": "Termin bestätigen",
            "text": "Kannst du den Termin morgen bestätigen?",
        },
        {
            "id": 2,
            "sender": "Team",
            "title": "Rechnung prüfen",
        },
        {
            "id": 3,
            "text": "Bitte Unterlagen vorbereiten.",
        },
    ]


def test_render_review_batch_selection_preview_shows_selected_items() -> None:
    parsed = parse_review_batch_selection("1,2", visible_ids=[1, 2, 3])

    output = render_review_batch_selection_preview(parsed, _visible_suggestions())

    assert REVIEW_BATCH_SELECTION_PREVIEW_TITLE in output
    assert "Ausgewählte Vorschläge:" in output
    assert "- 1: Chef: Termin bestätigen" in output
    assert "- 2: Team: Rechnung prüfen" in output
    assert "Bitte Unterlagen vorbereiten." not in output
    assert REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE in output


def test_render_review_batch_selection_preview_all_shows_all_visible_items() -> None:
    parsed = parse_review_batch_selection("all", visible_ids=[1, 2, 3])

    output = render_review_batch_selection_preview(parsed, _visible_suggestions())

    assert "- 1: Chef: Termin bestätigen" in output
    assert "- 2: Team: Rechnung prüfen" in output
    assert "- 3: Bitte Unterlagen vorbereiten." in output
    assert REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE in output


def test_render_review_batch_selection_preview_none_is_read_only() -> None:
    parsed = parse_review_batch_selection("none", visible_ids=[1, 2, 3])

    output = render_review_batch_selection_preview(parsed, _visible_suggestions())

    assert "Keine Vorschläge ausgewählt." in output
    assert REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE in output


def test_render_review_batch_selection_preview_back_is_read_only() -> None:
    parsed = parse_review_batch_selection("z", visible_ids=[1, 2, 3])

    output = render_review_batch_selection_preview(parsed, _visible_suggestions())

    assert "Zurück zum Review-Bereich." in output
    assert REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE in output


def test_render_review_batch_selection_preview_empty_is_read_only() -> None:
    parsed = parse_review_batch_selection("", visible_ids=[1, 2, 3])

    output = render_review_batch_selection_preview(parsed, _visible_suggestions())

    assert "Keine Batch-Auswahl eingegeben." in output
    assert REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE in output


def test_render_review_batch_selection_preview_invalid_shows_standard_message() -> None:
    parsed = parse_review_batch_selection("1,4", visible_ids=[1, 2, 3])

    output = render_review_batch_selection_preview(parsed, _visible_suggestions())

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output
    assert REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE in output


def test_render_review_batch_selection_preview_ignores_missing_selected_suggestions() -> None:
    parsed = parse_review_batch_selection("1", visible_ids=[1])

    output = render_review_batch_selection_preview(parsed, [])

    assert "Keine sichtbaren Vorschläge ausgewählt." in output
    assert REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE in output


def test_render_review_batch_selection_preview_handles_string_ids() -> None:
    parsed = parse_review_batch_selection("1", visible_ids=[1])
    suggestions = [{"id": "1", "summary": "Zusammenfassung"}]

    output = render_review_batch_selection_preview(parsed, suggestions)

    assert "- 1: Zusammenfassung" in output
    assert REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE in output


def test_render_review_batch_selection_preview_falls_back_for_missing_text() -> None:
    parsed = parse_review_batch_selection("1", visible_ids=[1])
    suggestions = [{"id": 1}]

    output = render_review_batch_selection_preview(parsed, suggestions)

    assert "- 1: Vorschlag 1" in output
    assert REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE in output
