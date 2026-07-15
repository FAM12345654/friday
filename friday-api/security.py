"""Bearer-token protection for network access to the Friday API.

When the ``FRIDAY_API_TOKEN`` environment variable is set (non-empty), every
request must present the token via ``Authorization: Bearer <token>`` or an
``X-Friday-Token`` header. Root, health, and CORS preflight requests stay
reachable without a token. Without a configured token, only direct loopback
requests are accepted; forwarded, LAN, tunnel, and public requests fail closed.
"""

from __future__ import annotations

import hmac
import os
from typing import Any, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

EXEMPT_PATHS: frozenset[str] = frozenset({"/", "/health"})
LOOPBACK_HOSTS: frozenset[str] = frozenset({"127.0.0.1", "::1", "localhost", "testclient"})
FORWARDED_CLIENT_HEADERS: tuple[str, ...] = (
    "cf-connecting-ip",
    "forwarded",
    "true-client-ip",
    "x-forwarded-for",
    "x-real-ip",
)
MIN_TOKEN_LENGTH = 32


def _configured_token() -> str:
    return os.getenv("FRIDAY_API_TOKEN", "").strip()


def _provided_token(request: Request) -> str:
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        return authorization[len("Bearer ") :].strip()
    return request.headers.get("X-Friday-Token", "").strip()


def _is_direct_loopback_request(request: Request) -> bool:
    client_host = str(request.client.host if request.client else "").strip().lower()
    if client_host not in LOOPBACK_HOSTS:
        return False
    return not any(request.headers.get(name, "").strip() for name in FORWARDED_CLIENT_HEADERS)


def register_auth(app: Any) -> None:
    """Register the optional token check as HTTP middleware."""

    @app.middleware("http")
    async def _auth_middleware(
        request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        token = _configured_token()
        if request.method == "OPTIONS" or request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        if not token:
            if _is_direct_loopback_request(request):
                return await call_next(request)
            return JSONResponse(
                status_code=503,
                content={
                    "detail": (
                        "FRIDAY_API_TOKEN fehlt. Netzwerkzugriff wurde aus "
                        "Sicherheitsgründen blockiert."
                    )
                },
            )

        if len(token) < MIN_TOKEN_LENGTH:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": (
                        f"FRIDAY_API_TOKEN muss mindestens {MIN_TOKEN_LENGTH} Zeichen lang sein."
                    )
                },
            )

        provided = _provided_token(request)
        if provided and hmac.compare_digest(provided, token):
            return await call_next(request)

        return JSONResponse(
            status_code=401,
            content={"detail": "Missing or invalid API token."},
            headers={"WWW-Authenticate": "Bearer"},
        )
