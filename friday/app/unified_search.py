"""Unified local search across tasks, contacts, messages, WhatsApp and mail.

Pure ranking logic without any I/O: callers pass already-loaded rows from the
local repositories/stores and get back one ranked, source-tagged result list.
Nothing here talks to the network or the database.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

TITLE_WEIGHT = 2.0
BODY_WEIGHT = 1.0
EXACT_WORD_BONUS = 0.5
SNIPPET_LENGTH = 120

VALID_SOURCES: tuple[str, ...] = ("task", "contact", "message", "whatsapp", "mail")


@dataclass(frozen=True)
class UnifiedSearchResult:
    """One ranked hit from the unified search."""

    source: str
    item_id: Any
    title: str
    snippet: str
    score: float
    received_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "id": self.item_id,
            "title": self.title,
            "snippet": self.snippet,
            "score": round(self.score, 3),
            "received_at": self.received_at,
        }


def _terms(query: str) -> tuple[str, ...]:
    return tuple(term for term in query.strip().casefold().split() if term)


def _field_score(terms: Sequence[str], text: str, weight: float) -> float:
    """Score one field: every matched term adds weight, exact words add bonus."""
    if not text:
        return 0.0
    lowered = text.casefold()
    words = set(lowered.split())
    score = 0.0
    for term in terms:
        if term in lowered:
            score += weight
            if term in words:
                score += EXACT_WORD_BONUS
    return score


def _all_terms_present(terms: Sequence[str], *fields: str) -> bool:
    combined = " ".join(field.casefold() for field in fields if field)
    return all(term in combined for term in terms)


def _snippet(terms: Sequence[str], text: str) -> str:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return ""
    lowered = cleaned.casefold()
    position = min(
        (lowered.find(term) for term in terms if lowered.find(term) >= 0),
        default=0,
    )
    start = max(0, position - SNIPPET_LENGTH // 3)
    excerpt = cleaned[start : start + SNIPPET_LENGTH]
    prefix = "…" if start > 0 else ""
    suffix = "…" if start + SNIPPET_LENGTH < len(cleaned) else ""
    return f"{prefix}{excerpt}{suffix}"


def _text(row: Mapping[str, Any], key: str) -> str:
    value = row.get(key)
    return str(value) if value is not None else ""


def _score_row(
    terms: Sequence[str],
    *,
    source: str,
    item_id: Any,
    title: str,
    body: str,
    received_at: str | None,
) -> UnifiedSearchResult | None:
    if not _all_terms_present(terms, title, body):
        return None
    score = _field_score(terms, title, TITLE_WEIGHT) + _field_score(terms, body, BODY_WEIGHT)
    if score <= 0:
        return None
    snippet = _snippet(terms, body) or _snippet(terms, title)
    return UnifiedSearchResult(
        source=source,
        item_id=item_id,
        title=title or "(ohne Titel)",
        snippet=snippet,
        score=score,
        received_at=received_at,
    )


def search_unified(
    query: str,
    *,
    tasks: Iterable[Mapping[str, Any]] = (),
    contacts: Iterable[Mapping[str, Any]] = (),
    messages: Iterable[Mapping[str, Any]] = (),
    whatsapp_messages: Iterable[Mapping[str, Any]] = (),
    mail_messages: Iterable[Mapping[str, Any]] = (),
    limit: int = 50,
) -> list[UnifiedSearchResult]:
    """Rank rows from all local sources for the query (AND across terms)."""
    terms = _terms(query)
    if not terms:
        return []
    safe_limit = max(1, min(int(limit or 50), 200))

    results: list[UnifiedSearchResult] = []

    for row in tasks:
        hit = _score_row(
            terms,
            source="task",
            item_id=row.get("id"),
            title=_text(row, "title"),
            body=" ".join((_text(row, "notes"), _text(row, "category"), _text(row, "status"))),
            received_at=_text(row, "due_date") or None,
        )
        if hit:
            results.append(hit)

    for row in contacts:
        hit = _score_row(
            terms,
            source="contact",
            item_id=row.get("id"),
            title=_text(row, "name"),
            body=" ".join(
                (_text(row, "notes"), _text(row, "email_address"), _text(row, "contact_type"))
            ),
            received_at=None,
        )
        if hit:
            results.append(hit)

    for row in messages:
        hit = _score_row(
            terms,
            source="message",
            item_id=row.get("id"),
            title=_text(row, "sender"),
            body=_text(row, "text"),
            received_at=_text(row, "received_at") or None,
        )
        if hit:
            results.append(hit)

    for row in whatsapp_messages:
        hit = _score_row(
            terms,
            source="whatsapp",
            item_id=row.get("id"),
            title=_text(row, "sender_name"),
            body=_text(row, "body"),
            received_at=_text(row, "received_at") or None,
        )
        if hit:
            results.append(hit)

    for row in mail_messages:
        hit = _score_row(
            terms,
            source="mail",
            item_id=row.get("id"),
            title=_text(row, "subject") or _text(row, "sender"),
            body=" ".join((_text(row, "sender"), _text(row, "snippet"))),
            received_at=_text(row, "received_at") or None,
        )
        if hit:
            results.append(hit)

    results.sort(key=lambda item: (-item.score, str(item.received_at or ""), str(item.item_id)))
    return results[:safe_limit]
