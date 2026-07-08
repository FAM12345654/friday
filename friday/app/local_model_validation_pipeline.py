"""Strict local model validation and logic-check composition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from friday.app.logic_check_agent import LogicCheckAgent, LogicCheckResult
from friday.app.model_output_validator import (
    ModelOutputValidationResult,
    validate_model_json,
)


@dataclass(frozen=True)
class LocalModelValidationPipelineResult:
    """Combined validation and logic-check result for local model output."""

    accepted: bool
    validation: ModelOutputValidationResult
    logic_check: LogicCheckResult
    blocked_reasons: tuple[str, ...]
    preview_only: bool
    persisted: bool
    external_call_used: bool
    product_flow_connected: bool


def validate_and_logic_check_model_output(
    *,
    schema: Mapping[str, Any],
    output: Mapping[str, Any] | str | None,
    purpose: str,
) -> LocalModelValidationPipelineResult:
    """Validate local model output and reject risky or implausible results."""

    validation = validate_model_json(schema=schema, output=output)
    logic_check = LogicCheckAgent().check_validated_output(
        validation,
        purpose=purpose,
    )

    blocked_reasons: list[str] = []
    if not validation.is_valid:
        blocked_reasons.append("validation_failed")
    if not logic_check.is_plausible:
        blocked_reasons.append("logic_check_failed")
    if logic_check.risk_level in {"high", "blocked"}:
        blocked_reasons.append(f"risk_level_{logic_check.risk_level}")

    accepted = not blocked_reasons

    return LocalModelValidationPipelineResult(
        accepted=accepted,
        validation=validation,
        logic_check=logic_check,
        blocked_reasons=tuple(dict.fromkeys(blocked_reasons)),
        preview_only=True,
        persisted=False,
        external_call_used=False,
        product_flow_connected=False,
    )
