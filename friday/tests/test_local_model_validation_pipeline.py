"""Tests for strict local model validation and logic-check composition."""

from __future__ import annotations

from friday.app.local_model_validation_pipeline import (
    validate_and_logic_check_model_output,
)


def _schema() -> dict:
    return {
        "required": ["summary", "confidence"],
        "properties": {"summary": "string", "confidence": "number"},
        "min_confidence": 0.6,
    }


def test_validation_pipeline_accepts_valid_low_risk_output() -> None:
    result = validate_and_logic_check_model_output(
        schema=_schema(),
        output={"summary": "Lokale Zusammenfassung.", "confidence": 0.9},
        purpose="summary",
    )

    assert result.accepted is True
    assert result.blocked_reasons == ()
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_call_used is False
    assert result.product_flow_connected is False


def test_validation_pipeline_blocks_unknown_action_field() -> None:
    result = validate_and_logic_check_model_output(
        schema=_schema(),
        output={
            "summary": "Senden.",
            "confidence": 0.9,
            "action": "send_email",
        },
        purpose="review",
    )

    assert result.accepted is False
    assert "validation_failed" in result.blocked_reasons


def test_validation_pipeline_blocks_risky_action_when_schema_allows_action() -> None:
    schema = {
        "required": ["summary", "confidence", "action"],
        "properties": {
            "summary": "string",
            "confidence": "number",
            "action": "string",
        },
        "min_confidence": 0.6,
    }

    result = validate_and_logic_check_model_output(
        schema=schema,
        output={"summary": "Senden.", "confidence": 0.9, "action": "send_email"},
        purpose="review",
    )

    assert result.accepted is False
    assert "logic_check_failed" in result.blocked_reasons
    assert "risk_level_high" in result.blocked_reasons


def test_validation_pipeline_blocks_sensitive_contact_terms() -> None:
    result = validate_and_logic_check_model_output(
        schema=_schema(),
        output={"summary": "Kontakt erwaehnt Gesundheit.", "confidence": 0.9},
        purpose="contact_context",
    )

    assert result.accepted is False
    assert "logic_check_failed" in result.blocked_reasons
