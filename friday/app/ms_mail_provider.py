"""Read-only Microsoft Graph mail provider for Friday."""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
import json
from typing import Any, Callable
from urllib import error, parse, request


# offline_access wird von MSAL automatisch ergaenzt (fuer Refresh-Token) und darf
# NICHT in der Scope-Liste stehen (MSAL lehnt reservierte Scopes ab).
MS_MAIL_SCOPES: tuple[str, ...] = ("Mail.Read", "User.Read")
MS_AUTHORITY_TEMPLATE = "https://login.microsoftonline.com/{tenant}"
GRAPH_ME_URL = "https://graph.microsoft.com/v1.0/me?$select=displayName,userPrincipalName,mail"
GRAPH_MESSAGES_URL = "https://graph.microsoft.com/v1.0/me/messages"
DEFAULT_REDIRECT_URI = "http://localhost"
MAX_BODY_PREVIEW_CHARS = 500


@dataclass(frozen=True)
class MsMailProviderResult:
    """Structured result for Microsoft Graph mail provider actions."""

    ok: bool
    message: str
    blocked_reasons: tuple[str, ...] = ()
    authorization_url: str | None = None
    token_bundle: dict[str, Any] | None = None
    username: str | None = None
    display_name: str | None = None
    messages: tuple[dict[str, Any], ...] = ()
    external_call_used: bool = False
    read_only: bool = True
    scopes: tuple[str, ...] = MS_MAIL_SCOPES


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


class _HTMLToTextParser(HTMLParser):
    """Small stdlib-only HTML-to-text parser for read-only mail bodies."""

    BLOCK_TAGS = {"br", "div", "p", "li", "tr"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if data:
            self.parts.append(data)

    def get_text(self) -> str:
        raw = unescape("".join(self.parts))
        lines = [" ".join(line.strip().split()) for line in raw.splitlines()]
        return "\n".join(line for line in lines if line).strip()


def _is_x500_address(value: str | None) -> bool:
    text = str(value or "").strip().upper()
    return text.startswith("/O=") or "/OU=EXCHANGE ADMINISTRATIVE GROUP" in text


def _short_internal_address(value: str | None) -> str:
    text = _clean(value)
    if not text:
        return "unbekannt"
    return text[:48] + "..." if len(text) > 48 else text


def _authority(tenant: str | None) -> str:
    return MS_AUTHORITY_TEMPLATE.format(tenant=_clean(tenant) or "common")


def _load_msal() -> Any:
    try:
        import msal  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError("msal_not_installed") from exc
    return msal


def _public_client(client_id: str, tenant: str | None, msal_module: Any | None = None) -> Any:
    normalized_client_id = _clean(client_id)
    if not normalized_client_id:
        raise ValueError("client_id_missing")
    module = msal_module or _load_msal()
    return module.PublicClientApplication(
        client_id=normalized_client_id,
        authority=_authority(tenant),
    )


def build_authorization_url(
    *,
    client_id: str,
    tenant: str | None = "common",
    redirect_uri: str = DEFAULT_REDIRECT_URI,
    state: str = "friday-ms-mail",
    msal_module: Any | None = None,
) -> MsMailProviderResult:
    """Build a Microsoft OAuth URL without performing a network call."""
    try:
        app = _public_client(client_id, tenant, msal_module=msal_module)
        url = app.get_authorization_request_url(
            scopes=list(MS_MAIL_SCOPES),
            redirect_uri=redirect_uri,
            state=state,
        )
    except (RuntimeError, ValueError) as exc:
        return MsMailProviderResult(
            ok=False,
            message="Microsoft-Mail-Verbindung konnte nicht vorbereitet werden.",
            blocked_reasons=(str(exc),),
            external_call_used=False,
        )
    return MsMailProviderResult(
        ok=True,
        message="Microsoft OAuth-Link wurde lokal vorbereitet.",
        authorization_url=url,
        external_call_used=False,
    )


def _extract_authorization_code(authorization_response: str) -> str:
    raw = str(authorization_response or "").strip()
    if not raw:
        return ""
    parsed = parse.urlparse(raw)
    query = parse.parse_qs(parsed.query)
    if "code" in query and query["code"]:
        return query["code"][0]
    if raw.startswith("4/") or raw.startswith("0."):
        return raw
    return ""


def exchange_auth_response(
    *,
    client_id: str,
    authorization_response: str,
    tenant: str | None = "common",
    redirect_uri: str = DEFAULT_REDIRECT_URI,
    msal_module: Any | None = None,
) -> MsMailProviderResult:
    """Exchange an OAuth callback/code for a local token bundle via MSAL."""
    code = _extract_authorization_code(authorization_response)
    if not code:
        return MsMailProviderResult(
            ok=False,
            message="Microsoft OAuth-Code fehlt.",
            blocked_reasons=("authorization_code_missing",),
            external_call_used=False,
        )
    try:
        app = _public_client(client_id, tenant, msal_module=msal_module)
        token_bundle = app.acquire_token_by_authorization_code(
            code,
            scopes=list(MS_MAIL_SCOPES),
            redirect_uri=redirect_uri,
        )
    except (RuntimeError, ValueError):
        return MsMailProviderResult(
            ok=False,
            message="Microsoft OAuth-Antwort konnte nicht verarbeitet werden.",
            blocked_reasons=("token_exchange_failed",),
            external_call_used=True,
        )
    if not isinstance(token_bundle, dict) or not token_bundle.get("access_token"):
        err = str((token_bundle or {}).get("error") or "").strip()
        desc = str((token_bundle or {}).get("error_description") or "").strip()
        detail = f" [{err}] {desc[:300]}" if (err or desc) else ""
        return MsMailProviderResult(
            ok=False,
            message=f"Microsoft OAuth-Antwort enthielt kein Zugriffstoken.{detail}",
            blocked_reasons=("access_token_missing", err or "unknown_error"),
            external_call_used=True,
        )
    return MsMailProviderResult(
        ok=True,
        message="Microsoft OAuth-Token wurde erhalten.",
        token_bundle=dict(token_bundle),
        external_call_used=True,
    )


def _access_token(token_bundle: dict[str, Any] | None) -> str:
    token = str((token_bundle or {}).get("access_token") or "").strip()
    if not token:
        raise ValueError("access_token_missing")
    return token


def _graph_get_json(
    url: str,
    access_token: str,
    *,
    urlopen: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    opener = urlopen or request.urlopen
    req = request.Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
        method="GET",
    )
    with opener(req, timeout=20) as response:
        raw = response.read().decode("utf-8")
    parsed = json.loads(raw or "{}")
    return parsed if isinstance(parsed, dict) else {}


def test_connection(
    *,
    token_bundle: dict[str, Any] | None,
    urlopen: Callable[..., Any] | None = None,
) -> MsMailProviderResult:
    """Read the Graph /me profile to verify read-only access."""
    try:
        payload = _graph_get_json(GRAPH_ME_URL, _access_token(token_bundle), urlopen=urlopen)
    except (ValueError, error.URLError, OSError, json.JSONDecodeError):
        return MsMailProviderResult(
            ok=False,
            message="Microsoft-Mail-Test fehlgeschlagen.",
            blocked_reasons=("graph_read_failed",),
            external_call_used=True,
        )
    username = _clean(payload.get("mail") or payload.get("userPrincipalName"))
    return MsMailProviderResult(
        ok=bool(username),
        message="Microsoft-Mail-Test erfolgreich." if username else "Microsoft-Mail-Test ohne Benutzerkennung.",
        username=username or None,
        display_name=_clean(payload.get("displayName")) or None,
        blocked_reasons=() if username else ("username_missing",),
        external_call_used=True,
    )


def _email_address_label(email_address: dict[str, Any] | None, *, fallback: str = "Unbekannter Absender") -> str:
    if isinstance(email_address, dict):
        name = _clean(email_address.get("name"))
        address = _clean(email_address.get("address"))
        if _is_x500_address(address):
            return name or f"Intern {_short_internal_address(address)}"
        if name and address and name.casefold() != address.casefold():
            return f"{name} <{address}>"
        return address or name or fallback
    return fallback


def _message_sender(item: dict[str, Any]) -> str:
    for key in ("from", "sender"):
        sender = item.get(key) or {}
        email_address = sender.get("emailAddress") if isinstance(sender, dict) else {}
        label = _email_address_label(email_address)
        if label != "Unbekannter Absender":
            return label
    return "Unbekannter Absender"


def _recipient_list(item: dict[str, Any]) -> list[dict[str, str]]:
    recipients: list[dict[str, str]] = []
    for group_name in ("toRecipients", "ccRecipients"):
        raw_group = item.get(group_name)
        if not isinstance(raw_group, list):
            continue
        recipient_type = "cc" if group_name == "ccRecipients" else "to"
        for raw_recipient in raw_group:
            email_address = raw_recipient.get("emailAddress") if isinstance(raw_recipient, dict) else {}
            if not isinstance(email_address, dict):
                continue
            name = _clean(email_address.get("name"))
            address = _clean(email_address.get("address"))
            label = _email_address_label(email_address, fallback="Unbekannter Empfänger")
            recipients.append(
                {
                    "type": recipient_type,
                    "name": name,
                    "address": address,
                    "label": label,
                }
            )
    return recipients


def _body_text(item: dict[str, Any]) -> str:
    body = item.get("body")
    if not isinstance(body, dict):
        return ""
    content = str(body.get("content") or "")
    if not content:
        return ""
    content_type = str(body.get("contentType") or "").strip().casefold()
    if content_type == "html":
        parser = _HTMLToTextParser()
        parser.feed(content)
        return parser.get_text()
    return "\n".join(line.rstrip() for line in unescape(content).splitlines()).strip()


def _map_message(item: dict[str, Any]) -> dict[str, Any] | None:
    message_id = _clean(item.get("id"))
    if not message_id:
        return None
    return {
        "message_id": message_id,
        "sender": _message_sender(item),
        "subject": _clean(item.get("subject")),
        "received_at": _clean(item.get("receivedDateTime")),
        "snippet": str(item.get("bodyPreview") or "")[:MAX_BODY_PREVIEW_CHARS],
        "recipients": _recipient_list(item),
        "body_full": _body_text(item),
    }


def list_messages(
    *,
    token_bundle: dict[str, Any] | None,
    top: int = 25,
    urlopen: Callable[..., Any] | None = None,
) -> MsMailProviderResult:
    """Read recent messages from Microsoft Graph with full body text, read-only."""
    try:
        limit = max(1, min(int(top), 50))
    except (TypeError, ValueError):
        limit = 25
    query = parse.urlencode(
        {
            "$top": str(limit),
            "$select": "id,from,sender,toRecipients,ccRecipients,subject,receivedDateTime,bodyPreview,body",
            "$orderby": "receivedDateTime desc",
        }
    )
    url = f"{GRAPH_MESSAGES_URL}?{query}"
    try:
        payload = _graph_get_json(url, _access_token(token_bundle), urlopen=urlopen)
    except (ValueError, error.URLError, OSError, json.JSONDecodeError):
        return MsMailProviderResult(
            ok=False,
            message="Microsoft-Mail-Sync fehlgeschlagen.",
            blocked_reasons=("graph_messages_read_failed",),
            external_call_used=True,
        )
    raw_items = payload.get("value") if isinstance(payload, dict) else []
    messages = []
    if isinstance(raw_items, list):
        for item in raw_items:
            if isinstance(item, dict):
                mapped = _map_message(item)
                if mapped is not None:
                    messages.append(mapped)
    return MsMailProviderResult(
        ok=True,
        message="Microsoft-Mail-Vorschau gelesen.",
        messages=tuple(messages),
        external_call_used=True,
    )
