"""Local preview helper for the model-readiness mock path."""

from __future__ import annotations

from dataclasses import dataclass

from friday.app.local_model_mock import (
    LocalModelMockAdapter,
    LocalModelMockResult,
    LocalModelReadinessStatus,
)


@dataclass(frozen=True)
class LocalModelPreview:
    """Structured preview payload for a local mock model response."""

    prompt: str
    result: LocalModelMockResult
    readiness: LocalModelReadinessStatus
    preview_only: bool
    product_flow_connected: bool


def preview_local_model_response(prompt: str) -> LocalModelPreview:
    """Return a local-only preview result for a given prompt."""
    adapter = LocalModelMockAdapter()
    result = adapter.generate(prompt)
    readiness = adapter.get_readiness_status()

    return LocalModelPreview(
        prompt=result.prompt,
        result=result,
        readiness=readiness,
        preview_only=True,
        product_flow_connected=False,
    )
