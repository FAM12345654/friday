"""Local-only mock adapter for future model-readiness integration."""

from __future__ import annotations

from dataclasses import dataclass

from friday.config import (
    ENABLE_REAL_CALENDAR,
    ENABLE_REAL_EMAIL,
    ENABLE_REAL_MUSIC,
    ENABLE_REAL_SMS,
    ENABLE_REAL_WEATHER,
    ENABLE_REAL_WHATSAPP,
    REQUIRE_USER_APPROVAL,
)


@dataclass(frozen=True)
class LocalModelMockResult:
    """Deterministic response payload produced by the local mock adapter."""

    provider: str
    model: str
    prompt: str
    response: str
    is_mock: bool
    external_call_used: bool


@dataclass(frozen=True)
class LocalModelReadinessStatus:
    """Readiness flags describing local adapter activation."""

    mode_supported: bool
    provider_config_present: bool
    approval_flow_available: bool
    safety_flags_locked: bool
    fallback_path_defined: bool
    fallback_status: str


class LocalModelMockAdapter:
    """Deterministic local mock adapter for future model-readiness workflows."""

    provider = "mock-local"
    model = "mock-readiness"
    mode = "local_mock"

    def is_available(self) -> bool:
        """Return readiness for mock responses without any external call."""
        return True

    def get_readiness_status(self) -> LocalModelReadinessStatus:
        """Return local readiness signals for the mock adapter."""
        return LocalModelReadinessStatus(
            mode_supported=True,
            provider_config_present=True,
            approval_flow_available=REQUIRE_USER_APPROVAL,
            safety_flags_locked=not any(
                (
                    ENABLE_REAL_EMAIL,
                    ENABLE_REAL_WHATSAPP,
                    ENABLE_REAL_SMS,
                    ENABLE_REAL_CALENDAR,
                    ENABLE_REAL_WEATHER,
                    ENABLE_REAL_MUSIC,
                )
            ),
            fallback_path_defined=True,
            fallback_status="local_rule_based",
        )

    def get_fallback_status(self) -> str:
        """Return explicit fallback label for unsupported model cases."""
        return self.get_readiness_status().fallback_status

    def generate(self, prompt: str) -> LocalModelMockResult:
        """Return a deterministic mock response for the given prompt."""
        clean_prompt = (prompt or "").strip()

        base_message = "Lokale Mock-Antwort: keine externen Modellaufrufe."
        if clean_prompt:
            response = f"{base_message} Eingabe erkannt."
        else:
            response = f"{base_message} Leere Eingabe erkannt."

        return LocalModelMockResult(
            provider=self.provider,
            model=self.model,
            prompt=clean_prompt,
            response=response,
            is_mock=True,
            external_call_used=False,
        )
