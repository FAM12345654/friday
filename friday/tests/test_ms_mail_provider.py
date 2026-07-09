"""Tests for the read-only Microsoft Graph mail provider."""

from __future__ import annotations

import json

from friday.app.ms_mail_provider import (
    MS_MAIL_SCOPES,
    build_authorization_url,
    exchange_auth_response,
    list_messages,
    test_connection as graph_test_connection,
)


class _FakePublicClient:
    def __init__(self, client_id, authority):
        self.client_id = client_id
        self.authority = authority

    def get_authorization_request_url(self, scopes, redirect_uri, state):
        assert scopes == list(MS_MAIL_SCOPES)
        assert "Mail.Send" not in scopes
        return f"https://login.test/auth?client_id={self.client_id}&redirect_uri={redirect_uri}&state={state}"

    def acquire_token_by_authorization_code(self, code, scopes, redirect_uri):
        assert code == "abc"
        assert scopes == list(MS_MAIL_SCOPES)
        assert redirect_uri == "http://localhost"
        return {"access_token": "runtime-token", "refresh_token": "refresh-token"}


class _FakeMsal:
    PublicClientApplication = _FakePublicClient


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_build_authorization_url_uses_read_only_scopes() -> None:
    result = build_authorization_url(
        client_id="client-1",
        tenant="common",
        msal_module=_FakeMsal,
    )

    assert result.ok is True
    assert result.authorization_url is not None
    assert "Mail.Send" not in result.authorization_url
    assert result.external_call_used is False


def test_exchange_auth_response_returns_token_bundle_without_logging_secret() -> None:
    result = exchange_auth_response(
        client_id="client-1",
        authorization_response="http://localhost/?code=abc&state=ok",
        msal_module=_FakeMsal,
    )

    assert result.ok is True
    assert result.token_bundle == {"access_token": "runtime-token", "refresh_token": "refresh-token"}
    assert result.external_call_used is True


def test_test_connection_reads_profile_with_mocked_urlopen() -> None:
    def _urlopen(_request, timeout):
        assert timeout == 20
        return _Response({"displayName": "Friday", "userPrincipalName": "mail@familienhelden.at"})

    result = graph_test_connection(token_bundle={"access_token": "token"}, urlopen=_urlopen)

    assert result.ok is True
    assert result.username == "mail@familienhelden.at"
    assert result.external_call_used is True


def test_list_messages_maps_only_preview_fields() -> None:
    def _urlopen(_request, timeout):
        return _Response(
            {
                "value": [
                    {
                        "id": "graph-1",
                        "from": {"emailAddress": {"address": "kunde@example.test"}},
                        "subject": "Bitte Philip Rechnung prüfen",
                        "receivedDateTime": "2026-07-09T10:00:00Z",
                        "bodyPreview": "Kurzvorschau" * 80,
                    }
                ]
            }
        )

    result = list_messages(token_bundle={"access_token": "token"}, top=25, urlopen=_urlopen)

    assert result.ok is True
    assert result.messages[0]["message_id"] == "graph-1"
    assert result.messages[0]["sender"] == "kunde@example.test"
    assert len(result.messages[0]["snippet"]) == 500
    assert "body" not in result.messages[0]


def test_list_messages_blocks_missing_access_token() -> None:
    result = list_messages(token_bundle={}, top=25, urlopen=lambda *_args, **_kwargs: None)

    assert result.ok is False
    assert "graph_messages_read_failed" in result.blocked_reasons
