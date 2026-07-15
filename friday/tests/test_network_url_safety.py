"""Tests for SSRF protection on user-configured calendar URLs."""

from __future__ import annotations

import socket

import pytest

from friday.app.network_url_safety import validate_external_https_url


def _records(*addresses: str):
    return [
        (socket.AF_INET6 if ":" in address else socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))
        for address in addresses
    ]


@pytest.mark.parametrize(
    "url",
    (
        "file:///etc/passwd",
        "http://calendar.example.com/feed.ics",
        "https://127.0.0.1/feed.ics",
        "https://[::1]/feed.ics",
        "https://169.254.169.254/latest/meta-data",
        "https://user:password@example.com/feed.ics",
        "https://example.com:8443/feed.ics",
    ),
)
def test_rejects_unsafe_ics_urls(url: str) -> None:
    with pytest.raises(ValueError):
        validate_external_https_url(url)


def test_accepts_public_https_url_after_public_dns_resolution() -> None:
    result = validate_external_https_url(
        "https://calendar.example.com/feed.ics",
        resolve_dns=True,
        resolver=lambda *_args, **_kwargs: _records("93.184.216.34"),
    )
    assert result == "https://calendar.example.com/feed.ics"


def test_rejects_dns_result_when_any_address_is_private() -> None:
    with pytest.raises(ValueError, match="private oder lokale Netze"):
        validate_external_https_url(
            "https://calendar.example.com/feed.ics",
            resolve_dns=True,
            resolver=lambda *_args, **_kwargs: _records("93.184.216.34", "10.0.0.4"),
        )
