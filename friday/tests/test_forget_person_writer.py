"""Tests for the guarded Forget Person writer."""

from __future__ import annotations

from dataclasses import replace

from friday.app.forget_person_preview import (
    FORGET_PERSON_APPROVAL_TOKEN,
    build_forget_person_preview,
)
from friday.app.forget_person_write_guard import check_forget_person_write_allowed
from friday.app.forget_person_writer import apply_forget_person_write
from friday.storage.contact_context_repository import ContactContextRepository
from friday.storage.database import initialize_database


def _allowed_guard(db_path):
    preview = build_forget_person_preview(db_path=db_path, person_identifier="contact-01")
    return check_forget_person_write_allowed(
        preview=preview,
        approval_token=FORGET_PERSON_APPROVAL_TOKEN,
        backup_available=True,
        transaction_available=True,
        rollback_available=True,
        scanner_smoke_passed=True,
    )


def test_forget_person_writer_deletes_only_guard_targets(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    repository = ContactContextRepository(db_path)
    repository.create_contact_context(contact_id="contact-01", display_name="Max Mustermann")
    repository.create_contact_context(contact_id="contact-02", display_name="Erika Musterfrau")
    guard = _allowed_guard(db_path)

    result = apply_forget_person_write(db_path=db_path, guard_result=guard)

    assert result.allowed is True
    assert result.deleted_counts == {"contact_contexts": 1}
    assert result.target_contact_ids == ("contact-01",)
    assert result.transaction_used is True
    assert result.rollback_performed is False
    assert result.schema_changed is False
    assert result.external_action_used is False
    assert result.obsidian_write_performed is False
    assert result.sensitive_content_returned is False
    assert repository.get_contact_context("contact-01") is None
    assert repository.get_contact_context("contact-02") is not None


def test_forget_person_writer_blocks_when_guard_not_allowed(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    repository = ContactContextRepository(db_path)
    repository.create_contact_context(contact_id="contact-01", display_name="Max Mustermann")
    preview = build_forget_person_preview(db_path=db_path, person_identifier="contact-01")
    guard = check_forget_person_write_allowed(
        preview=preview,
        approval_token="KONTAKT LÖSCHEN",
        backup_available=True,
        transaction_available=True,
        rollback_available=True,
        scanner_smoke_passed=True,
    )

    result = apply_forget_person_write(db_path=db_path, guard_result=guard)

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons
    assert repository.get_contact_context("contact-01") is not None


def test_forget_person_writer_rolls_back_candidate_count_mismatch(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    repository = ContactContextRepository(db_path)
    repository.create_contact_context(contact_id="contact-01", display_name="Max Mustermann")
    repository.create_contact_context(contact_id="contact-02", display_name="Erika Musterfrau")
    guard = replace(
        _allowed_guard(db_path),
        target_contact_ids=("contact-01", "contact-02"),
    )

    result = apply_forget_person_write(db_path=db_path, guard_result=guard)

    assert result.allowed is False
    assert result.deleted_counts == {"contact_contexts": 2}
    assert result.blocked_reasons == ("candidate_count_mismatch",)
    assert result.transaction_used is True
    assert result.rollback_performed is True
    assert repository.get_contact_context("contact-01") is not None
    assert repository.get_contact_context("contact-02") is not None
