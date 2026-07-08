"""Read-only preview renderer for review batch selections."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from friday.app.review_batch_selection_parser import (
    REVIEW_BATCH_SELECTION_INVALID_MESSAGE,
    ReviewBatchSelectionParseResult,
)


REVIEW_BATCH_SELECTION_PREVIEW_TITLE = "Batch-Auswahl-Vorschau"
REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE = (
    "Es wurde noch nichts freigegeben, abgelehnt oder gesendet."
)


def _suggestion_id(suggestion: Mapping[str, Any]) -> int | None:
    raw_id = suggestion.get("id")
    if isinstance(raw_id, int):
        return raw_id
    if isinstance(raw_id, str) and raw_id.isdecimal():
        return int(raw_id)
    return None


def _suggestion_text(suggestion: Mapping[str, Any]) -> str:
    sender = str(suggestion.get("sender") or "").strip()
    for key in ("title", "text", "suggested_text", "summary"):
        value = str(suggestion.get(key) or "").strip()
        if value:
            return f"{sender}: {value}" if sender else value

    suggestion_id = _suggestion_id(suggestion)
    if suggestion_id is not None:
        return f"Vorschlag {suggestion_id}"
    return "Vorschlag ohne ID"


def _visible_suggestions_by_id(
    visible_suggestions: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    suggestions_by_id: dict[int, Mapping[str, Any]] = {}
    for suggestion in visible_suggestions:
        suggestion_id = _suggestion_id(suggestion)
        if suggestion_id is not None and suggestion_id not in suggestions_by_id:
            suggestions_by_id[suggestion_id] = suggestion
    return suggestions_by_id


def _render_selected_suggestions(
    selected_ids: tuple[int, ...],
    visible_suggestions: Sequence[Mapping[str, Any]],
) -> list[str]:
    suggestions_by_id = _visible_suggestions_by_id(visible_suggestions)
    lines: list[str] = []

    for suggestion_id in selected_ids:
        suggestion = suggestions_by_id.get(suggestion_id)
        if suggestion is not None:
            lines.append(f"- {suggestion_id}: {_suggestion_text(suggestion)}")

    if not lines:
        return ["Keine sichtbaren Vorschläge ausgewählt."]

    return ["Ausgewählte Vorschläge:", *lines]


def render_review_batch_selection_preview(
    parsed_selection: ReviewBatchSelectionParseResult,
    visible_suggestions: Sequence[Mapping[str, Any]],
) -> str:
    """Render a German, read-only preview for a parsed batch selection."""
    lines = [REVIEW_BATCH_SELECTION_PREVIEW_TITLE, ""]

    if parsed_selection.status in ("selected", "all"):
        lines.extend(
            _render_selected_suggestions(
                parsed_selection.selected_ids,
                visible_suggestions,
            )
        )
    elif parsed_selection.status == "none":
        lines.append("Keine Vorschläge ausgewählt.")
    elif parsed_selection.status == "back":
        lines.append("Zurück zum Review-Bereich.")
    elif parsed_selection.status == "empty":
        lines.append("Keine Batch-Auswahl eingegeben.")
    else:
        lines.append(parsed_selection.message or REVIEW_BATCH_SELECTION_INVALID_MESSAGE)

    lines.extend(["", REVIEW_BATCH_SELECTION_NO_ACTION_MESSAGE])
    return "\n".join(lines)
