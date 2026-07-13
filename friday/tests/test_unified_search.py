"""Tests for the unified local search ranking."""

from __future__ import annotations

from friday.app.unified_search import UnifiedSearchResult, search_unified


TASKS = [
    {"id": 1, "title": "Rechnung an Anna senden", "notes": "PDF vorbereiten", "status": "open"},
    {"id": 2, "title": "Einkauf", "notes": "Milch und Brot", "status": "open"},
]
CONTACTS = [
    {"id": 7, "name": "Anna Beispiel", "notes": "Kundin", "email_address": "anna@example.com"},
]
MESSAGES = [
    {"id": 3, "sender": "Ben", "text": "Hast du die Rechnung schon geschickt?", "received_at": "2026-07-10"},
]
WHATSAPP = [
    {"id": 9, "sender_name": "Anna", "body": "Danke für die Rechnung!", "received_at": "2026-07-11"},
]
MAIL = [
    {
        "id": 4,
        "subject": "Rechnung Juli",
        "sender": "billing@example.com",
        "snippet": "Ihre Rechnung im Anhang",
        "received_at": "2026-07-12",
    },
]


def _search(query: str, **kwargs) -> list[UnifiedSearchResult]:
    return search_unified(
        query,
        tasks=TASKS,
        contacts=CONTACTS,
        messages=MESSAGES,
        whatsapp_messages=WHATSAPP,
        mail_messages=MAIL,
        **kwargs,
    )


def test_empty_query_returns_nothing() -> None:
    assert _search("") == []
    assert _search("   ") == []


def test_finds_matches_across_all_sources() -> None:
    results = _search("rechnung")
    sources = {result.source for result in results}
    assert sources == {"task", "message", "whatsapp", "mail"}


def test_title_matches_rank_above_body_matches() -> None:
    results = _search("rechnung")
    title_hit = next(r for r in results if r.source == "task")
    body_hit = next(r for r in results if r.source == "message")
    assert results.index(title_hit) < results.index(body_hit)


def test_all_terms_must_match() -> None:
    results = _search("rechnung anna")
    # Only rows containing BOTH terms match: the task mentions Anna in the
    # title, the WhatsApp message pairs sender "Anna" with "Rechnung".
    assert {r.source for r in results} == {"task", "whatsapp"}


def test_contact_search_by_name_and_email() -> None:
    assert [r.item_id for r in _search("beispiel")] == [7]
    assert [r.item_id for r in _search("anna@example.com")] == [7]


def test_case_insensitive() -> None:
    assert {r.item_id for r in _search("RECHNUNG")} == {1, 3, 9, 4}


def test_limit_is_applied() -> None:
    results = _search("rechnung", limit=2)
    assert len(results) == 2


def test_snippet_contains_match_context() -> None:
    results = _search("milch")
    assert len(results) == 1
    assert "Milch" in results[0].snippet


def test_to_dict_shape() -> None:
    result = _search("einkauf")[0]
    payload = result.to_dict()
    assert payload["source"] == "task"
    assert payload["id"] == 2
    assert isinstance(payload["score"], float)
