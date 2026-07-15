"""Tests for the read-only Microsoft Graph mail provider."""

from __future__ import annotations

import json

from friday.app.ms_mail_provider import (
    MS_MAIL_SCOPES,
    build_authorization_url,
    ensure_fresh_access_token,
    exchange_auth_response,
    list_messages,
    test_connection as graph_test_connection,
)


class _FakePublicClient:
    def __init__(self, client_id, authority):
        self.client_id = client_id
        self.authority = authority

    def initiate_auth_code_flow(self, scopes, redirect_uri, state):
        assert scopes == list(MS_MAIL_SCOPES)
        assert "Mail.Send" not in scopes
        return {
            "auth_uri": f"https://login.test/auth?client_id={self.client_id}&redirect_uri={redirect_uri}&state={state}",
            "state": state,
            "code_verifier": "private-pkce-verifier",
        }

    def acquire_token_by_auth_code_flow(self, auth_flow, auth_response, scopes):
        assert auth_flow["state"] == "secure-state"
        assert auth_response["code"] == "abc"
        assert auth_response["state"] == "secure-state"
        assert scopes == list(MS_MAIL_SCOPES)
        return {"access_token": "runtime-token", "refresh_token": "refresh-token"}

    def acquire_token_by_refresh_token(self, refresh_token, scopes):
        assert scopes == list(MS_MAIL_SCOPES)
        assert "Mail.Send" not in scopes
        if refresh_token == "expired":
            return {"error": "invalid_grant", "error_description": "expired"}
        return {"access_token": "fresh-token", "refresh_token": "new-refresh-token"}


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
        authorization_response="http://localhost/?code=abc&state=secure-state",
        auth_flow={"state": "secure-state", "code_verifier": "private-pkce-verifier"},
        msal_module=_FakeMsal,
    )

    assert result.ok is True
    assert result.token_bundle == {"access_token": "runtime-token", "refresh_token": "refresh-token"}
    assert result.external_call_used is True


def test_exchange_auth_response_rejects_mismatched_state() -> None:
    result = exchange_auth_response(
        client_id="client-1",
        authorization_response="http://localhost/?code=abc&state=attacker",
        auth_flow={"state": "secure-state", "code_verifier": "private-pkce-verifier"},
        msal_module=_FakeMsal,
    )

    assert result.ok is False
    assert "oauth_state_invalid" in result.blocked_reasons
    assert result.external_call_used is False


def test_ensure_fresh_access_token_refreshes_stored_bundle() -> None:
    result = ensure_fresh_access_token(
        client_id="client-1",
        tenant="common",
        token_bundle={"access_token": "old-token", "refresh_token": "refresh-token"},
        msal_module=_FakeMsal,
    )

    assert result.ok is True
    assert result.token_bundle is not None
    assert result.token_bundle["access_token"] == "fresh-token"
    assert result.token_bundle["refresh_token"] == "new-refresh-token"
    assert result.external_call_used is True
    assert result.scopes == MS_MAIL_SCOPES
    assert "Mail.Send" not in result.scopes


def test_ensure_fresh_access_token_requests_reconnect_on_invalid_refresh() -> None:
    result = ensure_fresh_access_token(
        client_id="client-1",
        tenant="common",
        token_bundle={"access_token": "old-token", "refresh_token": "expired"},
        msal_module=_FakeMsal,
    )

    assert result.ok is False
    assert "reconnect_required" in result.blocked_reasons
    assert "token_refresh_failed" in result.blocked_reasons
    assert result.external_call_used is True


def test_ensure_fresh_access_token_keeps_access_token_without_refresh_token() -> None:
    result = ensure_fresh_access_token(
        client_id="client-1",
        tenant="common",
        token_bundle={"access_token": "still-usable"},
        msal_module=_FakeMsal,
    )

    assert result.ok is True
    assert result.token_bundle == {"access_token": "still-usable"}
    assert result.external_call_used is False


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
                        "body": {"contentType": "html", "content": "<p>Hallo <b>Philip</b></p><p>Bitte prüfen.</p>"},
                    }
                ]
            }
        )

    result = list_messages(token_bundle={"access_token": "token"}, top=25, urlopen=_urlopen)

    assert result.ok is True
    assert result.messages[0]["message_id"] == "graph-1"
    assert result.messages[0]["sender"] == "kunde@example.test"
    assert len(result.messages[0]["snippet"]) == 500
    assert result.messages[0]["body_full"] == "Hallo Philip\nBitte prüfen."
    assert "body" not in result.messages[0]


def test_list_messages_formats_sender_with_display_name_and_address() -> None:
    def _urlopen(_request, timeout=20):
        return _Response(
            {
                "value": [
                    {
                        "id": "graph-1",
                        "from": {
                            "emailAddress": {
                                "name": "Kunde Eins",
                                "address": "kunde@example.test",
                            }
                        },
                        "subject": "Hallo",
                    }
                ]
            }
        )

    result = list_messages(token_bundle={"access_token": "token"}, urlopen=_urlopen)

    assert result.ok is True
    assert result.messages[0]["sender"] == "Kunde Eins <kunde@example.test>"


def test_list_messages_uses_display_name_for_internal_x500_sender() -> None:
    def _urlopen(_request, timeout=20):
        return _Response(
            {
                "value": [
                    {
                        "id": "graph-1",
                        "from": {
                            "emailAddress": {
                                "name": "Alex Intern",
                                "address": "/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP",
                            }
                        },
                    }
                ]
            }
        )

    result = list_messages(token_bundle={"access_token": "token"}, urlopen=_urlopen)

    assert result.ok is True
    assert result.messages[0]["sender"] == "Alex Intern"


def test_list_messages_shortens_internal_x500_sender_without_name() -> None:
    def _urlopen(_request, timeout=20):
        return _Response(
            {
                "value": [
                    {
                        "id": "graph-1",
                        "from": {
                            "emailAddress": {
                                "address": "/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP",
                            }
                        },
                    }
                ]
            }
        )

    result = list_messages(token_bundle={"access_token": "token"}, urlopen=_urlopen)

    assert result.ok is True
    assert result.messages[0]["sender"].startswith("Intern ")
    assert result.messages[0]["sender"] != "?"


def test_list_messages_falls_back_to_sender_field_and_maps_recipients() -> None:
    def _urlopen(_request, timeout=20):
        return _Response(
            {
                "value": [
                    {
                        "id": "graph-1",
                        "sender": {
                            "emailAddress": {
                                "name": "Fallback Sender",
                                "address": "fallback@example.test",
                            }
                        },
                        "toRecipients": [
                            {"emailAddress": {"name": "Philip", "address": "philip@example.test"}}
                        ],
                        "ccRecipients": [
                            {"emailAddress": {"name": "Alex", "address": "alex@example.test"}}
                        ],
                    }
                ]
            }
        )

    result = list_messages(token_bundle={"access_token": "token"}, urlopen=_urlopen)

    assert result.ok is True
    assert result.messages[0]["sender"] == "Fallback Sender <fallback@example.test>"
    assert result.messages[0]["recipients"] == [
        {"type": "to", "name": "Philip", "address": "philip@example.test", "label": "Philip <philip@example.test>"},
        {"type": "cc", "name": "Alex", "address": "alex@example.test", "label": "Alex <alex@example.test>"},
    ]


def test_list_messages_blocks_missing_access_token() -> None:
    result = list_messages(token_bundle={}, top=25, urlopen=lambda *_args, **_kwargs: None)

    assert result.ok is False
    assert "graph_messages_read_failed" in result.blocked_reasons
