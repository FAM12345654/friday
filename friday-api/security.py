"""Optional bearer-token protection for the Friday API.

When the ``FRIDAY_API_TOKEN`` environment variable is set (non-empty), every
request must present the token via ``Authorization: Bearer <token>`` or an
``X-Friday-Token`` header. Health/docs endpoints and CORS preflight requests
stay reachable without a token. When the variable is unset, behavior is
unchanged (local-only setups keep working out of the box).
"""

from __future__ import annotations

import hmac
import os
from typing import Any, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

EXEMPT_PATHS: frozenset[str] = frozenset(
    {"/", "/health", "/docs", "/openapi.json", "/redoc"}
)


def _configured_token() -> str:
    return os.getenv("FRIDAY_API_TOKEN", "").strip()


def _provided_token(request: Request) -> str:
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        return authorization[len("Bearer ") :].strip()
    return request.headers.get("X-Friday-Token", "").strip()


def register_auth(app: Any) -> None:
    """Register the optional token check as HTTP middleware."""

    @app.middleware("http")
    async def _auth_middleware(
        request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        token = _configured_token()
        if (
            not token
            or request.method == "OPTIONS"
            or request.url.path in EXEMPT_PATHS
        ):
            return await call_next(request)

        provided = _provided_token(request)
        if provided and hmac.compare_digest(provided, token):
            return await call_next(request)

        return JSONResponse(
            status_code=401,
            content={"detail": "Missing or invalid API token."},
            headers={"WWW-Authenticate": "Bearer"},
        )
