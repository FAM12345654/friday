"""Read-only Forget Person preview model for Friday."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from friday.app.contact_context_preview import normalize_contact_name


FORGET_PERSON_APPROVAL_TOKEN = "PERSON VERGESSEN"


@dataclass(frozen=True)
class ForgetPersonPreviewContact:
    """A non-sensitive contact context match shown before a local forget write."""

    contact_id: str
    display_name: str
    contact_type: str


@dataclass(frozen=True)
class ForgetPersonPreview:
    """Side-effect-free Forget Person preview."""

    person_identifier: str
    normalized_person_identifier: str
    db_path: str
    target_table: str
    matched_contacts: tuple[ForgetPersonPreviewContact, ...]
    candidate_count: int
    allowed: bool
    blocked_reasons: tuple[str, ...]
    requires_token: str
    backup_required: bool
    transaction_required: bool
    rollback_required: bool
    sensitive_content_hidden: bool
    writes_performed: bool
    deletes_performed: bool
    schema_changed: bool
    external_lookup_used: bool
    obsidian_write_performed: bool


def _blocked_preview(
    *,
    person_identifier: str,
    db_path: Path,
    blocked_reasons: tuple[str, ...],
) -> ForgetPersonPreview:
    normalized_identifier = normalize_contact_name(person_identifier)
    return ForgetPersonPreview(
        person_identifier=person_identifier,
        normalized_person_identifier=normalized_identifier,
        db_path=str(db_path),
        target_table="contact_contexts",
        matched_contacts=(),
        candidate_count=0,
        allowed=False,
        blocked_reasons=blocked_reasons,
        requires_token=FORGET_PERSON_APPROVAL_TOKEN,
        backup_required=True,
        transaction_required=True,
        rollback_required=True,
        sensitive_content_hidden=True,
        writes_performed=False,
        deletes_performed=False,
        schema_changed=False,
        external_lookup_used=False,
        obsidian_write_performed=False,
    )


def _connect_read_only(db_path: Path) -> sqlite3.Connection:
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _contact_contexts_table_exists(connection: sqlite3.Connection) -> bool:
    row = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        LIMIT 1
        """,
        ("contact_contexts",),
    ).fetchone()
    return row is not None


def _find_matching_contacts(
    connection: sqlite3.Connection,
    *,
    person_identifier: str,
    normalized_person_identifier: str,
) -> tuple[ForgetPersonPreviewContact, ...]:
    rows = connection.execute(
        """
        SELECT contact_id, display_name, contact_type
        FROM contact_contexts
        WHERE contact_id = ?
           OR normalized_name = ?
        ORDER BY normalized_name, contact_id
        """,
        (person_identifier, normalized_person_identifier),
    ).fetchall()
    return tuple(
        ForgetPersonPreviewContact(
            contact_id=str(row["contact_id"]),
            display_name=str(row["display_name"]),
            contact_type=str(row["contact_type"]),
        )
        for row in rows
    )


def build_forget_person_preview(
    *,
    db_path: Path | str,
    person_identifier: str,
) -> ForgetPersonPreview:
    """Build a read-only preview for locally forgetting one person.

    The preview opens an existing SQLite database read-only, matches by
    contact id or normalized display name, and never writes files, deletes
    rows, changes schema, touches Obsidian, or calls external services.
    """

    selected_identifier = (person_identifier or "").strip()
    resolved_db_path = Path(db_path)
    if not selected_identifier:
        return _blocked_preview(
            person_identifier=selected_identifier,
            db_path=resolved_db_path,
            blocked_reasons=("missing_person_identifier",),
        )

    if not resolved_db_path.exists() or not resolved_db_path.is_file():
        return _blocked_preview(
            person_identifier=selected_identifier,
            db_path=resolved_db_path,
            blocked_reasons=("database_missing",),
        )

    normalized_identifier = normalize_contact_name(selected_identifier)
    try:
        with _connect_read_only(resolved_db_path) as connection:
            if not _contact_contexts_table_exists(connection):
                return _blocked_preview(
                    person_identifier=selected_identifier,
                    db_path=resolved_db_path,
                    blocked_reasons=("contact_contexts_table_missing",),
                )

            matched_contacts = _find_matching_contacts(
                connection,
                person_identifier=selected_identifier,
                normalized_person_identifier=normalized_identifier,
            )
    except sqlite3.Error:
        return _blocked_preview(
            person_identifier=selected_identifier,
            db_path=resolved_db_path,
            blocked_reasons=("database_unreadable",),
        )

    return ForgetPersonPreview(
        person_identifier=selected_identifier,
        normalized_person_identifier=normalized_identifier,
        db_path=str(resolved_db_path),
        target_table="contact_contexts",
        matched_contacts=matched_contacts,
        candidate_count=len(matched_contacts),
        allowed=True,
        blocked_reasons=(),
        requires_token=FORGET_PERSON_APPROVAL_TOKEN,
        backup_required=True,
        transaction_required=True,
        rollback_required=True,
        sensitive_content_hidden=True,
        writes_performed=False,
        deletes_performed=False,
        schema_changed=False,
        external_lookup_used=False,
        obsidian_write_performed=False,
    )
