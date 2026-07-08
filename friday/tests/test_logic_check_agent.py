"""Tests for the preview-only logic check agent."""

from __future__ import annotations

from friday.app.logic_check_agent import LogicCheckAgent
from friday.app.model_output_validator import validate_model_json


def _validated(data: dict):
    return validate_model_json(
        schema={
            "required": ["summary", "confidence"],
            "properties": {"summary": "string", "confidence": "number"},
            "allow_unknown_fields": True,
            "min_confidence": 0.1,
        },
        output=data,
    )


def test_logic_check_accepts_simple_valid_summary() -> None:
    agent = LogicCheckAgent()
    result = agent.check_validated_output(
        _validated({"summary": "Lokale Zusammenfassung.", "confidence": 0.9}),
        purpose="summary",
    )

    assert result.is_plausible is True
    assert result.risk_level == "low"
    assert result.warnings == []
    assert result.preview_only is True
    assert result.external_call_used is False
    assert result.product_flow_connected is False


def test_logic_check_blocks_invalid_validation_result() -> None:
    agent = LogicCheckAgent()
    invalid = validate_model_json(schema={"required": ["summary"]}, output={})

    result = agent.check_validated_output(invalid, purpose="summary")

    assert result.is_plausible is False
    assert result.risk_level == "blocked"
    assert "Validierung ist fehlgeschlagen." in result.warnings


def test_validator_and_logic_fail_closed_with_preview_safety_flags() -> None:
    validation = validate_model_json(schema={"required": ["summary"]}, output="[]")

    assert validation.is_valid is False
    assert validation.preview_only is True
    assert validation.external_call_used is False
    assert validation.product_flow_connected is False

    logic = LogicCheckAgent().check_validated_output(validation, purpose="summary")

    assert logic.is_plausible is False
    assert logic.risk_level == "blocked"
    assert logic.preview_only is True
    assert logic.external_call_used is False
    assert logic.product_flow_connected is False


def test_logic_check_warns_about_sensitive_contact_terms() -> None:
    agent = LogicCheckAgent()
    validation = _validated(
        {
            "summary": "Kontakt erwaehnt Gesundheit und Diagnose.",
            "confidence": 0.8,
        }
    )

    result = agent.check_validated_output(validation, purpose="contact_context")

    assert result.is_plausible is False
    assert result.risk_level == "medium"
    assert any("Sensibler Begriff erkannt" in warning for warning in result.warnings)


def test_logic_check_flags_risky_action() -> None:
    agent = LogicCheckAgent()
    validation = validate_model_json(
        schema={
            "required": ["summary", "confidence", "action"],
            "properties": {"summary": "string", "confidence": "number", "action": "string"},
            "min_confidence": 0.1,
        },
        output={"summary": "Bitte senden.", "confidence": 0.9, "action": "send_email"},
    )

    result = agent.check_validated_output(validation, purpose="review")

    assert result.is_plausible is False
    assert result.risk_level == "high"
    assert "Riskante Aktion erkannt: send_email" in result.warnings


def test_logic_check_flags_model_triggered_obsidian_write() -> None:
    agent = LogicCheckAgent()
    validation = validate_model_json(
        schema={
            "required": ["summary", "confidence", "action"],
            "properties": {"summary": "string", "confidence": "number", "action": "string"},
            "min_confidence": 0.1,
        },
        output={
            "summary": "Obsidian Write soll ausgefuehrt werden.",
            "confidence": 0.9,
            "action": "obsidian_write",
        },
    )

    result = agent.check_validated_output(validation, purpose="obsidian")

    assert result.is_plausible is False
    assert result.risk_level == "high"
    assert "Riskante Aktion erkannt: obsidian_write" in result.warnings


def test_logic_check_warns_about_low_confidence() -> None:
    agent = LogicCheckAgent()
    result = agent.check_validated_output(
        _validated({"summary": "Unsicher.", "confidence": 0.2}),
        purpose="summary",
    )

    assert result.is_plausible is False
    assert result.risk_level == "low"
    assert "Confidence ist fuer Plausibilitaet niedrig." in result.warnings


def test_logic_check_warns_about_missing_task_context() -> None:
    agent = LogicCheckAgent()
    result = agent.check_validated_output(
        _validated({"summary": "Allgemein.", "confidence": 0.9}),
        purpose="task",
    )

    assert result.is_plausible is True
    assert result.risk_level == "low"


def test_logic_check_task_requires_title_or_summary() -> None:
    agent = LogicCheckAgent()
    validation = validate_model_json(
        schema={
            "required": ["confidence"],
            "properties": {"confidence": "number"},
            "allow_unknown_fields": False,
        },
        output={"confidence": 0.9},
    )

    result = agent.check_validated_output(validation, purpose="task")

    assert result.is_plausible is False
    assert "Task-Ausgabe enthaelt keinen Titel oder keine Zusammenfassung." in result.warnings
