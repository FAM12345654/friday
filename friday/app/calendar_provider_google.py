"""Google Calendar provider for Friday.

All Google imports live in this dedicated module so scanners can keep every
other module network/provider-free.
"""

from __future__ import annotations

from dataclasses import dataclass
import hmac
import os
from pathlib import Path
from typing import Any

from friday.app.calendar_google_account_store import (
    GoogleCalendarAccount,
    decrypt_google_calendar_credentials,
    load_google_calendar_account,
)
from friday.app.calendar_provider_base import CalendarProviderEvent, CalendarProviderResult
from friday.app.oauth_transaction_store import extract_oauth_state


GOOGLE_CALENDAR_SCOPES = (
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
)


def _to_rfc3339(value: str, *, end_of_day: bool = False) -> str:
    """Normalize a date or datetime string to RFC3339 for the Google Calendar API.

    Google's ``timeMin``/``timeMax`` require a full timestamp with offset. A plain
    date like ``2026-07-01`` is rejected with HTTP 400, so date-only inputs get a
    day boundary and UTC marker appended. Existing datetimes pass through unchanged.
    """
    text = str(value or "").strip()
    if not text or "T" in text:
        return text
    return f"{text}T23:59:59Z" if end_of_day else f"{text}T00:00:00Z"


@dataclass(frozen=True)
class GoogleOAuthPreview:
    """Preview data for starting a desktop OAuth flow."""

    ok: bool
    authorization_url: str | None
    message: str
    blocked_reasons: tuple[str, ...]
    external_call_used: bool


@dataclass(frozen=True)
class GoogleOAuthCredentialsPreview:
    """Preview result for exchanging a Google OAuth response for credentials."""

    ok: bool
    credentials_json: str | None
    message: str
    blocked_reasons: tuple[str, ...]
    external_call_used: bool


def _load_google_dependencies() -> dict[str, Any]:
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Google-Kalender-Bibliotheken fehlen. Installiere friday-api/requirements.txt."
        ) from exc
    return {
        "Credentials": Credentials,
        "InstalledAppFlow": InstalledAppFlow,
        "build": build,
    }


def build_google_oauth_authorization_url(
    *,
    client_secrets_path: str | Path,
    state: str,
    code_verifier: str,
) -> GoogleOAuthPreview:
    """Build an OAuth URL for the local desktop loopback flow."""
    path = Path(client_secrets_path)
    if not path.exists() or not path.is_file():
        return GoogleOAuthPreview(
            ok=False,
            authorization_url=None,
            message="Google OAuth Client-Secrets-Datei wurde nicht gefunden.",
            blocked_reasons=("client_secrets_missing",),
            external_call_used=False,
        )
    deps = _load_google_dependencies()
    if len(str(state or "")) < 32 or not 43 <= len(str(code_verifier or "")) <= 128:
        return GoogleOAuthPreview(
            ok=False,
            authorization_url=None,
            message="Google OAuth Sicherheitszustand ist ungültig.",
            blocked_reasons=("oauth_transaction_invalid",),
            external_call_used=False,
        )
    flow = deps["InstalledAppFlow"].from_client_secrets_file(
        str(path),
        scopes=list(GOOGLE_CALENDAR_SCOPES),
        redirect_uri="http://localhost",
        state=state,
        code_verifier=code_verifier,
        autogenerate_code_verifier=False,
    )
    authorization_url, returned_state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    if not hmac.compare_digest(str(returned_state or ""), str(state)):
        return GoogleOAuthPreview(
            ok=False,
            authorization_url=None,
            message="Google OAuth State konnte nicht sicher erzeugt werden.",
            blocked_reasons=("oauth_state_generation_failed",),
            external_call_used=False,
        )
    return GoogleOAuthPreview(
        ok=True,
        authorization_url=authorization_url,
        message="Google OAuth URL wurde vorbereitet. Anmeldung laeuft im Browser am PC.",
        blocked_reasons=(),
        external_call_used=False,
    )


def exchange_google_oauth_authorization_response(
    *,
    client_secrets_path: str | Path,
    authorization_response: str,
    expected_state: str,
    code_verifier: str,
) -> GoogleOAuthCredentialsPreview:
    """Exchange the browser callback URL for OAuth credentials."""
    path = Path(client_secrets_path)
    if not path.exists() or not path.is_file():
        return GoogleOAuthCredentialsPreview(
            ok=False,
            credentials_json=None,
            message="Google OAuth Client-Secrets-Datei wurde nicht gefunden.",
            blocked_reasons=("client_secrets_missing",),
            external_call_used=False,
        )
    clean_response = str(authorization_response or "").strip()
    if not clean_response:
        return GoogleOAuthCredentialsPreview(
            ok=False,
            credentials_json=None,
            message="Google OAuth Antwort-URL fehlt.",
            blocked_reasons=("authorization_response_missing",),
            external_call_used=False,
        )
    response_state = extract_oauth_state(clean_response)
    if not response_state or not hmac.compare_digest(response_state, str(expected_state or "")):
        return GoogleOAuthCredentialsPreview(
            ok=False,
            credentials_json=None,
            message="Google OAuth State ist ungültig oder abgelaufen.",
            blocked_reasons=("oauth_state_invalid",),
            external_call_used=False,
        )
    if not 43 <= len(str(code_verifier or "")) <= 128:
        return GoogleOAuthCredentialsPreview(
            ok=False,
            credentials_json=None,
            message="Google OAuth PKCE-Verifier ist ungültig.",
            blocked_reasons=("oauth_pkce_invalid",),
            external_call_used=False,
        )
    deps = _load_google_dependencies()
    flow = deps["InstalledAppFlow"].from_client_secrets_file(
        str(path),
        scopes=list(GOOGLE_CALENDAR_SCOPES),
        redirect_uri="http://localhost",
        state=expected_state,
        code_verifier=code_verifier,
        autogenerate_code_verifier=False,
    )
    previous_insecure_transport = os.environ.get("OAUTHLIB_INSECURE_TRANSPORT")
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    try:
        try:
            flow.fetch_token(authorization_response=clean_response)
        except Exception:
            return GoogleOAuthCredentialsPreview(
                ok=False,
                credentials_json=None,
                message="Google OAuth Antwort konnte nicht sicher verarbeitet werden.",
                blocked_reasons=("oauth_exchange_failed",),
                external_call_used=True,
            )
    finally:
        if previous_insecure_transport is None:
            os.environ.pop("OAUTHLIB_INSECURE_TRANSPORT", None)
        else:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = previous_insecure_transport
    return GoogleOAuthCredentialsPreview(
        ok=True,
        credentials_json=flow.credentials.to_json(),
        message="Google OAuth Antwort wurde verarbeitet.",
        blocked_reasons=(),
        external_call_used=True,
    )


class GoogleCalendarProvider:
    """Google Calendar provider backed by stored OAuth credentials."""

    provider_name = "google_calendar"

    def __init__(
        self,
        *,
        account: GoogleCalendarAccount | None = None,
        service: Any | None = None,
    ) -> None:
        self.account = account if account is not None else load_google_calendar_account()
        self._service = service

    def _build_service(self) -> Any:
        if self._service is not None:
            return self._service
        if self.account is None:
            raise RuntimeError("Kein Google-Kalender-Konto verbunden.")
        deps = _load_google_dependencies()
        credentials = deps["Credentials"].from_authorized_user_info(
            decrypt_google_calendar_credentials(self.account),
            scopes=list(GOOGLE_CALENDAR_SCOPES),
        )
        self._service = deps["build"]("calendar", "v3", credentials=credentials)
        return self._service

    @staticmethod
    def _event_from_google(raw_event: dict[str, Any], *, calendar_id: str) -> CalendarProviderEvent:
        start = raw_event.get("start", {})
        end = raw_event.get("end", {})
        return CalendarProviderEvent(
            id=raw_event.get("id"),
            provider="google_calendar",
            calendar_id=calendar_id,
            title=raw_event.get("summary") or "Termin",
            start=start.get("dateTime") or start.get("date") or "",
            end=end.get("dateTime") or end.get("date") or "",
            location=raw_event.get("location"),
            raw=raw_event,
        )

    @staticmethod
    def _event_to_google(event: CalendarProviderEvent) -> dict[str, Any]:
        body: dict[str, Any] = {
            "summary": event.title,
            "start": {"dateTime": event.start},
            "end": {"dateTime": event.end},
        }
        if event.id:
            body["id"] = str(event.id)
        if event.location:
            body["location"] = event.location
        raw = event.raw if isinstance(event.raw, dict) else {}
        description = raw.get("description")
        if isinstance(description, str) and description.strip():
            body["description"] = description.strip()
        extended_properties = raw.get("extendedProperties")
        if isinstance(extended_properties, dict):
            private = extended_properties.get("private")
            if isinstance(private, dict):
                clean_private = {
                    str(key): str(value)
                    for key, value in private.items()
                    if str(key).strip() and str(value).strip()
                }
                if clean_private:
                    body["extendedProperties"] = {"private": clean_private}
        return body

    def test_connection(self) -> CalendarProviderResult:
        try:
            service = self._build_service()
            calendar_id = self.account.calendar_id if self.account else "primary"
            service.calendarList().get(calendarId=calendar_id).execute()
            return CalendarProviderResult(
                ok=True,
                message="Google-Kalender-Verbindung OK.",
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - real provider defensive boundary
            return CalendarProviderResult(
                ok=False,
                message=f"Google-Kalender-Verbindung fehlgeschlagen: {exc}",
                blocked_reasons=("google_connection_failed",),
                external_call_used=True,
            )

    def list_events(self, *, range_start: str, range_end: str) -> CalendarProviderResult:
        try:
            service = self._build_service()
            calendar_id = self.account.calendar_id if self.account else "primary"
            response = service.events().list(
                calendarId=calendar_id,
                timeMin=_to_rfc3339(range_start),
                timeMax=_to_rfc3339(range_end, end_of_day=True),
                singleEvents=True,
                orderBy="startTime",
            ).execute()
            events = tuple(
                self._event_from_google(item, calendar_id=calendar_id)
                for item in response.get("items", [])
            )
            return CalendarProviderResult(
                ok=True,
                events=events,
                message="Google-Kalender-Events gelesen.",
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - real provider defensive boundary
            return CalendarProviderResult(
                ok=False,
                message=f"Google-Kalender-Lesen fehlgeschlagen: {exc}",
                blocked_reasons=("google_list_failed",),
                external_call_used=True,
            )

    def get_event(self, *, event_id: str, calendar_id: str) -> CalendarProviderResult:
        """Read the exact event snapshot used by the destructive-action approval."""
        try:
            clean_event_id = str(event_id or "").strip()
            if not clean_event_id:
                return CalendarProviderResult(
                    ok=False,
                    message="Google-Kalendertermin konnte nicht gelesen werden: Event-ID fehlt.",
                    blocked_reasons=("provider_event_id_missing",),
                    external_call_used=False,
                )
            service = self._build_service()
            target_calendar_id = str(calendar_id or "").strip() or (
                self.account.calendar_id if self.account else "primary"
            )
            response = service.events().get(
                calendarId=target_calendar_id,
                eventId=clean_event_id,
            ).execute()
            event = self._event_from_google(response, calendar_id=target_calendar_id)
            return CalendarProviderResult(
                ok=True,
                event=event,
                message="Google-Kalendertermin gelesen.",
                provider_event_id=clean_event_id,
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - real provider defensive boundary
            return CalendarProviderResult(
                ok=False,
                message=f"Google-Kalendertermin konnte nicht gelesen werden: {exc}",
                blocked_reasons=("google_get_failed",),
                provider_event_id=str(event_id or "").strip() or None,
                external_call_used=True,
            )

    def create_event(self, event: CalendarProviderEvent) -> CalendarProviderResult:
        try:
            service = self._build_service()
            calendar_id = event.calendar_id or (self.account.calendar_id if self.account else "primary")
            response = service.events().insert(
                calendarId=calendar_id,
                body=self._event_to_google(event),
            ).execute()
            created = self._event_from_google(response, calendar_id=calendar_id)
            return CalendarProviderResult(
                ok=True,
                event=created,
                message="Google-Kalendertermin erstellt.",
                provider_event_id=created.id,
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - real provider defensive boundary
            return CalendarProviderResult(
                ok=False,
                message=f"Google-Kalender-Schreiben fehlgeschlagen: {exc}",
                blocked_reasons=("google_create_failed",),
                external_call_used=True,
            )

    def delete_event(self, *, event_id: str, calendar_id: str) -> CalendarProviderResult:
        """Delete one Google Calendar event after an upstream guard has allowed it."""
        try:
            clean_event_id = str(event_id or "").strip()
            if not clean_event_id:
                return CalendarProviderResult(
                    ok=False,
                    message="Google-Kalendertermin wurde nicht geloescht: Event-ID fehlt.",
                    blocked_reasons=("provider_event_id_missing",),
                    external_call_used=False,
                )
            service = self._build_service()
            target_calendar_id = str(calendar_id or "").strip() or (
                self.account.calendar_id if self.account else "primary"
            )
            service.events().delete(
                calendarId=target_calendar_id,
                eventId=clean_event_id,
            ).execute()
            return CalendarProviderResult(
                ok=True,
                message="Google-Kalendertermin geloescht.",
                provider_event_id=clean_event_id,
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - real provider defensive boundary
            return CalendarProviderResult(
                ok=False,
                message=f"Google-Kalender-Loeschen fehlgeschlagen: {exc}",
                blocked_reasons=("google_delete_failed",),
                provider_event_id=str(event_id or "").strip() or None,
                external_call_used=True,
            )
