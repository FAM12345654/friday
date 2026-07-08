"""Tests for the read-only Forget Person preview."""

from __future__ import annotations

from friday.app.forget_person_preview import (
    FORGET_PERSON_APPROVAL_TOKEN,
    build_forget_person_preview,
)
from friday.storage.contact_context_repository import ContactContextRepository
from friday.storage.database import initialize_database


def test_forget_person_preview_matches_contact_id_read_only(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    repository = ContactContextRepository(db_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
        relationship_context="lokaler Kontext",
        user_approved_persistence=True,
        sensitivity_checked=True,
    )

    preview = build_forget_person_preview(
        db_path=db_path,
        person_identifier="contact-01",
    )

    assert preview.allowed is True
    assert preview.candidate_count == 1
    assert preview.requires_token == FORGET_PERSON_APPROVAL_TOKEN
    assert preview.matched_contacts[0].contact_id == "contact-01"
    assert preview.matched_contacts[0].display_name == "Max Mustermann"
    assert preview.target_table == "contact_contexts"
    assert preview.writes_performed is False
    assert preview.deletes_performed is False
    assert preview.schema_changed is False
    assert preview.external_lookup_used is False
    assert preview.obsidian_write_performed is False
    assert repository.get_contact_context("contact-01") is not None


def test_forget_person_preview_matches_normalized_display_name(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    repository = ContactContextRepository(db_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
    )

    preview = build_forget_person_preview(
        db_path=db_path,
        person_identifier="  MAX   MUSTERMANN  ",
    )

    assert preview.candidate_count == 1
    assert preview.matched_contacts[0].contact_id == "contact-01"


def test_forget_person_preview_missing_database_has_no_side_effects(tmp_path) -> None:
    db_path = tmp_path / "missing" / "friday.db"

    preview = build_forget_person_preview(
        db_path=db_path,
        person_identifier="contact-01",
    )

    assert preview.allowed is False
    assert preview.blocked_reasons == ("database_missing",)
    assert preview.candidate_count == 0
    assert db_path.exists() is False
    assert db_path.parent.exists() is False


def test_forget_person_preview_missing_identifier_blocks(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)

    preview = build_forget_person_preview(
        db_path=db_path,
        person_identifier=" ",
    )

    assert preview.allowed is False
    assert preview.blocked_reasons == ("missing_person_identifier",)
    assert preview.candidate_count == 0
