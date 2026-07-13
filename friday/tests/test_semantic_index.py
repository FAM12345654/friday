"""Tests for the local semantic index with a fake embedder."""

from __future__ import annotations

import math

import pytest

from friday.app.semantic_index import (
    OllamaEmbedder,
    index_documents,
    index_stats,
    semantic_search,
)
from friday.storage.database import initialize_database


class FakeEmbedder:
    """Deterministic bag-of-words embedder over a small vocabulary."""

    VOCAB = ("rechnung", "termin", "einkauf", "urlaub", "anna", "zahnarzt")

    def embed(self, texts):
        vectors = []
        for text in texts:
            lowered = text.casefold()
            vector = [float(lowered.count(word)) for word in self.VOCAB]
            vectors.append(vector)
        return vectors


DOCS = [
    {"source": "mail", "source_id": "1", "title": "Rechnung Juli", "text": "Ihre Rechnung von Anna"},
    {"source": "task", "source_id": "2", "title": "Einkauf", "text": "Milch kaufen"},
    {"source": "whatsapp", "source_id": "3", "title": "Anna", "text": "Zahnarzt Termin morgen"},
]


def _db(tmp_path):
    db_file = tmp_path / "friday.db"
    initialize_database(db_file)
    return db_file


def test_index_and_search_ranks_by_similarity(tmp_path) -> None:
    db = _db(tmp_path)
    count = index_documents(DOCS, FakeEmbedder(), db_path=db)
    assert count == 3

    hits = semantic_search("rechnung anna", FakeEmbedder(), db_path=db)
    assert hits[0].source == "mail"
    assert hits[0].similarity > 0.5
    sources = [hit.source for hit in hits]
    assert "task" not in sources  # no overlap with 'einkauf' document


def test_reindex_upserts_instead_of_duplicating(tmp_path) -> None:
    db = _db(tmp_path)
    index_documents(DOCS, FakeEmbedder(), db_path=db)
    index_documents(DOCS, FakeEmbedder(), db_path=db)
    stats = index_stats(db_path=db)
    assert stats["total"] == 3
    assert stats["per_source"] == {"mail": 1, "task": 1, "whatsapp": 1}


def test_updated_document_gets_new_embedding(tmp_path) -> None:
    db = _db(tmp_path)
    index_documents(DOCS, FakeEmbedder(), db_path=db)
    changed = [{"source": "task", "source_id": "2", "title": "Urlaub", "text": "Urlaub planen"}]
    index_documents(changed, FakeEmbedder(), db_path=db)

    hits = semantic_search("urlaub", FakeEmbedder(), db_path=db)
    assert len(hits) == 1
    assert hits[0].source_id == "2"
    assert hits[0].title == "Urlaub"


def test_empty_query_and_empty_docs(tmp_path) -> None:
    db = _db(tmp_path)
    assert semantic_search("", FakeEmbedder(), db_path=db) == []
    assert index_documents([], FakeEmbedder(), db_path=db) == 0
    assert index_documents(
        [{"source": "task", "source_id": "9", "title": "", "text": "   "}],
        FakeEmbedder(),
        db_path=db,
    ) == 0


def test_limit_and_min_similarity(tmp_path) -> None:
    db = _db(tmp_path)
    index_documents(DOCS, FakeEmbedder(), db_path=db)
    hits = semantic_search("anna", FakeEmbedder(), db_path=db, limit=1)
    assert len(hits) == 1
    none = semantic_search("anna", FakeEmbedder(), db_path=db, min_similarity=0.999)
    assert all(hit.similarity > 0.999 for hit in none)


def test_hit_to_dict_shape(tmp_path) -> None:
    db = _db(tmp_path)
    index_documents(DOCS, FakeEmbedder(), db_path=db)
    payload = semantic_search("zahnarzt", FakeEmbedder(), db_path=db)[0].to_dict()
    assert payload["source"] == "whatsapp"
    assert 0 < payload["similarity"] <= 1
    assert "Termin" in payload["snippet"]


def test_ollama_embedder_refuses_external_urls() -> None:
    embedder = OllamaEmbedder(base_url="https://example.com")
    with pytest.raises(RuntimeError, match="127.0.0.1"):
        embedder.embed(["text"])


def test_ollama_embedder_parses_response() -> None:
    import io
    import json as jsonlib

    class FakeResponse:
        def __init__(self, payload: bytes) -> None:
            self._payload = payload

        def read(self) -> bytes:
            return self._payload

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_opener(req, timeout):
        body = jsonlib.loads(req.data.decode("utf-8"))
        assert body["model"]
        vectors = [[1.0, 0.0] for _ in body["input"]]
        return FakeResponse(jsonlib.dumps({"embeddings": vectors}).encode("utf-8"))

    embedder = OllamaEmbedder(base_url="http://localhost:11434", opener=fake_opener)
    assert embedder.embed(["a", "b"]) == [[1.0, 0.0], [1.0, 0.0]]
