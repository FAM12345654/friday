"""Preview-only logic checks for validated local model data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from friday.app.model_output_validator import ModelOutputValidationResult


@dataclass(frozen=True)
class LogicCheckResult:
    """Result of a local logic check."""

    is_plausible: bool
    risk_level: str
    warnings: list[str]
    checked_fields: list[str]
    preview_only: bool
    external_call_used: bool
    product_flow_connected: bool


SENSITIVE_TERMS = {
    "religion",
    "politisch",
    "politik",
    "ethnie",
    "gesundheit",
    "diagnose",
    "sexuell",
    "gewerkschaft",
    "finanzen privat",
}

RISKY_ACTION_TERMS = {
    "send_email",
    "send_whatsapp",
    "send_sms",
    "create_calendar_event",
    "delete_contact",
    "obsidian_write",
}


def _base_result(
    is_plausible: bool,
    risk_level: str,
    warnings: list[str],
    checked_fields: list[str],
) -> LogicCheckResult:
    return LogicCheckResult(
        is_plausible=is_plausible,
        risk_level=risk_level,
        warnings=warnings,
        checked_fields=checked_fields,
        preview_only=True,
        external_call_used=False,
        product_flow_connected=False,
    )


def _all_text_values(data: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    for value in data.values():
        if isinstance(value, str):
            values.append(value.lower())
        elif isinstance(value, list):
            values.extend(str(item).lower() for item in value)
        elif isinstance(value, dict):
            values.extend(_all_text_values(value))
    return values


class LogicCheckAgent:
    """Local-only plausibility checker for validated model output."""

    def check_validated_output(
        self,
        validation: ModelOutputValidationResult,
        purpose: str,
    ) -> LogicCheckResult:
        """Check validated output for obvious local safety and plausibility issues."""
        if not validation.is_valid:
            return _base_result(
                is_plausible=False,
                risk_level="blocked",
                warnings=["Validierung ist fehlgeschlagen."],
                checked_fields=[],
            )

        data = validation.data
        checked_fields = sorted(data.keys())
        warnings: list[str] = []

        if not data:
            warnings.append("Keine Daten fuer Logikpruefung vorhanden.")

        text_values = _all_text_values(data)
        joined_text = " ".join(text_values)

        for term in sorted(SENSITIVE_TERMS):
            if term in joined_text:
                warnings.append(f"Sensibler Begriff erkannt: {term}")

        for field, value in data.items():
            if str(field).lower() in {"action", "next_action", "operation"}:
                action_value = str(value).strip().lower()
                if action_value in RISKY_ACTION_TERMS:
                    warnings.append(f"Riskante Aktion erkannt: {action_value}")

        confidence = data.get("confidence")
        if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
            if confidence < 0.5:
                warnings.append("Confidence ist fuer Plausibilitaet niedrig.")

        normalized_purpose = (purpose or "").strip().lower()
        if "contact" in normalized_purpose and not any(
            field in data for field in ("contact_type", "display_name", "summary")
        ):
            warnings.append("Kontakt-Kontext-Ausgabe enthaelt keinen erkennbaren Kontaktbezug.")

        if "task" in normalized_purpose and not any(field in data for field in ("title", "summary")):
            warnings.append("Task-Ausgabe enthaelt keinen Titel oder keine Zusammenfassung.")

        if any(warning.startswith("Riskante Aktion") for warning in warnings):
            risk_level = "high"
        elif any(warning.startswith("Sensibler Begriff") for warning in warnings):
            risk_level = "medium"
        elif warnings:
            risk_level = "low"
        else:
            risk_level = "low"

        return _base_result(
            is_plausible=not warnings,
            risk_level=risk_level,
            warnings=warnings,
            checked_fields=checked_fields,
        )
