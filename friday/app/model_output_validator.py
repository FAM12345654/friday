"""Validate local model output before any future product use."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping


@dataclass(frozen=True)
class ModelOutputValidationResult:
    """Result for model-output validation."""

    is_valid: bool
    data: dict[str, Any]
    errors: list[str]
    preview_only: bool
    external_call_used: bool
    product_flow_connected: bool


TYPE_ALIASES: dict[str, tuple[type, ...]] = {
    "str": (str,),
    "string": (str,),
    "bool": (bool,),
    "boolean": (bool,),
    "int": (int,),
    "integer": (int,),
    "float": (int, float),
    "number": (int, float),
    "dict": (dict,),
    "object": (dict,),
    "list": (list,),
    "array": (list,),
}


def _error_result(errors: list[str]) -> ModelOutputValidationResult:
    return ModelOutputValidationResult(
        is_valid=False,
        data={},
        errors=errors,
        preview_only=True,
        external_call_used=False,
        product_flow_connected=False,
    )


def _parse_output(output: Mapping[str, Any] | str | None) -> tuple[dict[str, Any], list[str]]:
    if output is None:
        return {}, ["Modellantwort ist leer."]
    if isinstance(output, str):
        if not output.strip():
            return {}, ["Modellantwort ist leer."]
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError:
            return {}, ["Modellantwort ist kein gültiges JSON."]
        if not isinstance(parsed, dict):
            return {}, ["Modellantwort muss ein JSON-Objekt sein."]
        return parsed, []
    if isinstance(output, Mapping):
        data = dict(output)
        if not data:
            return {}, ["Modellantwort ist leer."]
        return data, []
    return {}, ["Modellantwort muss ein JSON-Objekt sein."]


def _matches_expected_type(value: Any, expected: Any) -> bool:
    if isinstance(expected, str):
        allowed = TYPE_ALIASES.get(expected.strip().lower())
        if allowed is None:
            return False
        if expected.strip().lower() in {"float", "number"}:
            return isinstance(value, allowed) and not isinstance(value, bool)
        if expected.strip().lower() in {"int", "integer"}:
            return isinstance(value, int) and not isinstance(value, bool)
        return isinstance(value, allowed)
    if isinstance(expected, type):
        if expected is float:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if expected is int:
            return isinstance(value, int) and not isinstance(value, bool)
        return isinstance(value, expected)
    return True


def reject_unknown_fields(schema: Mapping[str, Any], data: Mapping[str, Any]) -> list[str]:
    """Return validation errors for fields not declared in the schema."""
    allow_unknown = bool(schema.get("allow_unknown_fields", False))
    if allow_unknown:
        return []

    properties = schema.get("properties", {})
    allowed_fields = set(properties.keys()) if isinstance(properties, Mapping) else set()
    required = schema.get("required", [])
    if isinstance(required, list):
        allowed_fields.update(str(field) for field in required)

    unknown_fields = sorted(set(data.keys()) - allowed_fields)
    return [f"Unbekanntes Feld: {field}" for field in unknown_fields]


def require_confidence(data: Mapping[str, Any], min_confidence: float) -> list[str]:
    """Return validation errors when confidence is missing or too low."""
    confidence = data.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        return ["Confidence fehlt oder ist keine Zahl."]
    if float(confidence) < min_confidence:
        return [f"Confidence ist zu niedrig: {confidence}"]
    return []


def validate_model_json(
    schema: Mapping[str, Any],
    output: Mapping[str, Any] | str | None,
) -> ModelOutputValidationResult:
    """Validate JSON-like local model output against a small schema subset."""
    data, parse_errors = _parse_output(output)
    if parse_errors:
        return _error_result(parse_errors)

    errors: list[str] = []
    required = schema.get("required", [])
    if isinstance(required, list):
        for field in required:
            if str(field) not in data:
                errors.append(f"Pflichtfeld fehlt: {field}")

    properties = schema.get("properties", {})
    if isinstance(properties, Mapping):
        for field, expected_type in properties.items():
            if field in data and not _matches_expected_type(data[field], expected_type):
                errors.append(f"Feld hat falschen Typ: {field}")

    errors.extend(reject_unknown_fields(schema, data))

    min_confidence = schema.get("min_confidence")
    if min_confidence is not None:
        try:
            errors.extend(require_confidence(data, float(min_confidence)))
        except (TypeError, ValueError):
            errors.append("Minimale Confidence ist ungültig.")

    return ModelOutputValidationResult(
        is_valid=not errors,
        data=data,
        errors=errors,
        preview_only=True,
        external_call_used=False,
        product_flow_connected=False,
    )
