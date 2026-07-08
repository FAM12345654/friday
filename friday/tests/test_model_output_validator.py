"""Tests for local model output validation."""

from __future__ import annotations

from friday.app.model_output_validator import (
    reject_unknown_fields,
    require_confidence,
    validate_model_json,
)


def test_validate_model_json_accepts_valid_dict() -> None:
    result = validate_model_json(
        schema={
            "required": ["summary", "confidence"],
            "properties": {"summary": "string", "confidence": "number"},
            "min_confidence": 0.6,
        },
        output={"summary": "Alles lokal.", "confidence": 0.9},
    )

    assert result.is_valid is True
    assert result.data["summary"] == "Alles lokal."
    assert result.errors == []
    assert result.preview_only is True
    assert result.external_call_used is False
    assert result.product_flow_connected is False


def test_validate_model_json_accepts_valid_json_string() -> None:
    result = validate_model_json(
        schema={"required": ["summary"], "properties": {"summary": "string"}},
        output='{"summary": "JSON ok"}',
    )

    assert result.is_valid is True
    assert result.data == {"summary": "JSON ok"}


def test_validate_model_json_rejects_invalid_json() -> None:
    result = validate_model_json(
        schema={"required": ["summary"]},
        output="{not-json",
    )

    assert result.is_valid is False
    assert "Modellantwort ist kein gültiges JSON." in result.errors


def test_validate_model_json_rejects_missing_required_field() -> None:
    result = validate_model_json(
        schema={"required": ["summary"], "properties": {"summary": "string"}},
        output={"confidence": 0.8},
    )

    assert result.is_valid is False
    assert "Pflichtfeld fehlt: summary" in result.errors


def test_validate_model_json_rejects_unknown_fields_by_default() -> None:
    result = validate_model_json(
        schema={"required": ["summary"], "properties": {"summary": "string"}},
        output={"summary": "ok", "hallucinated_action": "send_email"},
    )

    assert result.is_valid is False
    assert "Unbekanntes Feld: hallucinated_action" in result.errors


def test_validate_model_json_allows_unknown_fields_when_explicit() -> None:
    result = validate_model_json(
        schema={
            "required": ["summary"],
            "properties": {"summary": "string"},
            "allow_unknown_fields": True,
        },
        output={"summary": "ok", "extra": "erlaubt"},
    )

    assert result.is_valid is True


def test_validate_model_json_rejects_wrong_type() -> None:
    result = validate_model_json(
        schema={"required": ["summary"], "properties": {"summary": "string"}},
        output={"summary": 123},
    )

    assert result.is_valid is False
    assert "Feld hat falschen Typ: summary" in result.errors


def test_validate_model_json_rejects_empty_response() -> None:
    result = validate_model_json(schema={}, output="")

    assert result.is_valid is False
    assert "Modellantwort ist leer." in result.errors


def test_require_confidence_rejects_missing_or_low_confidence() -> None:
    assert require_confidence({}, 0.7) == ["Confidence fehlt oder ist keine Zahl."]
    assert require_confidence({"confidence": 0.4}, 0.7) == ["Confidence ist zu niedrig: 0.4"]
    assert require_confidence({"confidence": 0.9}, 0.7) == []


def test_reject_unknown_fields_reports_extra_fields() -> None:
    errors = reject_unknown_fields(
        schema={"properties": {"summary": "string"}},
        data={"summary": "ok", "send": True},
    )

    assert errors == ["Unbekanntes Feld: send"]
