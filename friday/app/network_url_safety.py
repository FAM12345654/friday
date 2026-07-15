"""Validation helpers for server-side fetches of user-configured URLs."""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable
from typing import Any
from urllib import request
from urllib.parse import urlsplit


Resolver = Callable[..., list[tuple[Any, ...]]]


def validate_external_https_url(
    value: str,
    *,
    resolve_dns: bool = False,
    resolver: Resolver | None = None,
) -> str:
    """Return a normalized public HTTPS URL or raise ``ValueError``.

    Network callers must use ``resolve_dns=True`` immediately before opening
    the connection. Storage callers use the syntax-only mode so encrypted
    configuration remains testable without making DNS requests.
    """
    clean = str(value or "").strip()
    try:
        parsed = urlsplit(clean)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("ICS-URL ist ungültig.") from exc

    if parsed.scheme.lower() != "https":
        raise ValueError("ICS-URL muss HTTPS verwenden.")
    if not parsed.hostname:
        raise ValueError("ICS-URL enthält keinen Hostnamen.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("ICS-URL darf keine eingebetteten Zugangsdaten enthalten.")
    if port not in (None, 443):
        raise ValueError("ICS-URL darf nur HTTPS-Port 443 verwenden.")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"}:
        raise ValueError("ICS-URL darf nicht auf lokale Dienste zeigen.")

    literal_address: ipaddress.IPv4Address | ipaddress.IPv6Address | None = None
    try:
        literal_address = ipaddress.ip_address(hostname)
    except ValueError:
        pass
    if literal_address is not None and not literal_address.is_global:
        raise ValueError("ICS-URL darf nicht auf private oder lokale Netze zeigen.")

    if resolve_dns:
        active_resolver = resolver or socket.getaddrinfo
        try:
            records = active_resolver(hostname, 443, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise ValueError("ICS-Hostname konnte nicht sicher aufgelöst werden.") from exc
        addresses = {str(record[4][0]).split("%", 1)[0] for record in records if record[4]}
        if not addresses:
            raise ValueError("ICS-Hostname lieferte keine Netzwerkadresse.")
        try:
            parsed_addresses = [ipaddress.ip_address(address) for address in addresses]
        except ValueError as exc:
            raise ValueError("ICS-Hostname lieferte eine ungültige Netzwerkadresse.") from exc
        if any(not address.is_global for address in parsed_addresses):
            raise ValueError("ICS-Hostname verweist auf private oder lokale Netze.")

    return clean


class SafeHttpsRedirectHandler(request.HTTPRedirectHandler):
    """Re-validate every redirect target before urllib follows it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        safe_url = validate_external_https_url(newurl, resolve_dns=True)
        return super().redirect_request(req, fp, code, msg, headers, safe_url)
