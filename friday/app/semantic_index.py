"""Local semantic search over mail, messages, tasks and notes.

Embeddings come from local Ollama only (same localhost-only guard as the
generation runtime); vectors are stored as JSON in the local SQLite database.
The embedder is injectable so tests never touch the network, and cosine
ranking is plain Python — no extra dependencies, nothing leaves the machine.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Protocol
from urllib import error, request

from friday import config
from friday.app.local_ollama_runtime import is_local_ollama_url
from friday.storage.database import get_connection, setup_local_database

DEFAULT_EMBED_MODEL = "nomic-embed-text"
MAX_TEXT_LENGTH = 2000


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text."""


@dataclass(frozen=True)
class SemanticHit:
    """One ranked semantic search result."""

    source: str
    source_id: str
    title: str
    text: str
    similarity: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "id": self.source_id,
            "title": self.title,
            "snippet": self.text[:200],
            "similarity": round(self.similarity, 4),
        }


class OllamaEmbedder:
    """Embedding client for local Ollama with the localhost-only guard."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
        opener: Callable[..., Any] | None = None,
    ) -> None:
        self.base_url = (base_url or config.OLLAMA_BASE_URL).strip().rstrip("/")
        self.model = (model or getattr(config, "OLLAMA_EMBED_MODEL", DEFAULT_EMBED_MODEL)).strip()
        self.timeout_seconds = timeout_seconds or config.OLLAMA_TIMEOUT_SECONDS
        self._opener = opener or request.urlopen

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not is_local_ollama_url(self.base_url):
            raise RuntimeError("Embeddings erlauben nur 127.0.0.1 oder localhost.")
        payload = json.dumps({"model": self.model, "input": texts}).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/embed",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._opener(req, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (OSError, error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"Ollama-Embedding fehlgeschlagen: {exc}") from exc
        embeddings = body.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise RuntimeError("Ollama-Embedding-Antwort hat ein unerwartetes Format.")
        return [[float(v) for v in vector] for vector in embeddings]


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _clip(text: str) -> str:
    cleaned = " ".join(str(text or "").split())
    return cleaned[:MAX_TEXT_LENGTH]


def index_documents(
    documents: Iterable[Mapping[str, Any]],
    embedder: Embedder,
    *,
    db_path: Path | str | None = None,
) -> int:
    """Upsert documents ({source, source_id, title, text}) into the index."""
    setup_local_database(db_path)
    rows = [
        {
            "source": str(doc["source"]),
            "source_id": str(doc["source_id"]),
            "title": _clip(doc.get("title", "")),
            "text": _clip(doc.get("text", "")),
        }
        for doc in documents
        if _clip(doc.get("text", "")) or _clip(doc.get("title", ""))
    ]
    if not rows:
        return 0

    vectors = embedder.embed([f"{row['title']} {row['text']}".strip() for row in rows])
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as connection:
        for row, vector in zip(rows, vectors):
            connection.execute(
                """
                INSERT INTO semantic_index (source, source_id, title, text, embedding_json, updated_at)
                VALUES (:source, :source_id, :title, :text, :embedding, :updated_at)
                ON CONFLICT (source, source_id) DO UPDATE SET
                    title = excluded.title,
                    text = excluded.text,
                    embedding_json = excluded.embedding_json,
                    updated_at = excluded.updated_at
                """,
                {
                    **row,
                    "embedding": json.dumps(vector),
                    "updated_at": now,
                },
            )
    return len(rows)


def semantic_search(
    query: str,
    embedder: Embedder,
    *,
    db_path: Path | str | None = None,
    limit: int = 10,
    min_similarity: float = 0.0,
) -> list[SemanticHit]:
    """Rank indexed documents by cosine similarity to the query."""
    cleaned = _clip(query)
    if not cleaned:
        return []
    safe_limit = max(1, min(int(limit or 10), 100))
    query_vector = embedder.embed([cleaned])[0]

    setup_local_database(db_path)
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT source, source_id, title, text, embedding_json FROM semantic_index"
        ).fetchall()

    hits: list[SemanticHit] = []
    for row in rows:
        try:
            vector = json.loads(row["embedding_json"])
        except (TypeError, ValueError):
            continue
        similarity = _cosine(query_vector, vector)
        if similarity <= min_similarity:
            continue
        hits.append(
            SemanticHit(
                source=row["source"],
                source_id=row["source_id"],
                title=row["title"],
                text=row["text"],
                similarity=similarity,
            )
        )
    hits.sort(key=lambda hit: -hit.similarity)
    return hits[:safe_limit]


def index_stats(*, db_path: Path | str | None = None) -> dict[str, Any]:
    """Return per-source document counts for the semantic index."""
    setup_local_database(db_path)
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT source, COUNT(*) AS count FROM semantic_index GROUP BY source ORDER BY source"
        ).fetchall()
    per_source = {row["source"]: int(row["count"]) for row in rows}
    return {"total": sum(per_source.values()), "per_source": per_source}
