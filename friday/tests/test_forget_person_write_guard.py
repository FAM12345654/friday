"""Tests for the Forget Person write guard."""

from __future__ import annotations

import pytest

from friday.app.forget_person_preview import (
    FORGET_PERSON_APPROVAL_TOKEN,
    build_forget_person_preview,
)
from friday.app.forget_person_write_guard import check_forget_person_write_allowed
from friday.storage.contact_context_repository import ContactContextRepository
from friday.storage.database import initialize_database


def _preview_with_contact(tmp_path):
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    repository = ContactContextRepository(db_path)
    repository.create_contact_context(contact_id="contact-01", display_name="Max Mustermann")
    return build_forget_person_preview(db_path=db_path, person_identifier="contact-01")


def test_forget_person_guard_allows_exact_hard_token(tmp_path) -> None:
    preview = _preview_with_contact(tmp_path)

    result = check_forget_person_write_allowed(
        preview=preview,
        approval_token=FORGET_PERSON_APPROVAL_TOKEN,
        backup_available=True,
        transaction_available=True,
        rollback_available=True,
        scanner_smoke_passed=True,
    )

    assert result.allowed is True
    assert result.required_token == FORGET_PERSON_APPROVAL_TOKEN
    assert result.target_contact_ids == ("contact-01",)
    assert result.candidate_count == 1
    assert result.local_only is True
    assert result.external_action_used is False
    assert result.obsidian_write_performed is False
    assert result.schema_changed is False


@pytest.mark.parametrize(
    "approval_token",
    (
        "",
        "ja",
        "JA",
        "ok",
        "löschen",
        "SPEICHERN",
        "KONTAKT LÖSCHEN",
        " PERSON VERGESSEN ",
    ),
)
def test_forget_person_guard_blocks_soft_or_old_tokens(tmp_path, approval_token) -> None:
    preview = _preview_with_contact(tmp_path)

    result = check_forget_person_write_allowed(
        preview=preview,
        approval_token=approval_token,
        backup_available=True,
        transaction_available=True,
        rollback_available=True,
        scanner_smoke_passed=True,
    )

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons


@pytest.mark.parametrize(
    ("kwargs", "reason"),
    (
        ({"backup_available": False}, "missing_backup"),
        ({"transaction_available": False}, "transaction_unavailable"),
        ({"rollback_available": False}, "rollback_unavailable"),
        ({"scanner_smoke_passed": False}, "scanner_smoke_failed"),
        ({"external_actions_enabled": True}, "external_actions_enabled"),
        ({"obsidian_write_requested": True}, "obsidian_write_requested"),
    ),
)
def test_forget_person_guard_blocks_missing_safety_conditions(tmp_path, kwargs, reason) -> None:
    preview = _preview_with_contact(tmp_path)
    options = {
        "backup_available": True,
        "transaction_available": True,
        "rollback_available": True,
        "scanner_smoke_passed": True,
        "external_actions_enabled": False,
        "obsidian_write_requested": False,
    }
    options.update(kwargs)

    result = check_forget_person_write_allowed(
        preview=preview,
        approval_token=FORGET_PERSON_APPROVAL_TOKEN,
        **options,
    )

    assert result.allowed is False
    assert reason in result.blocked_reasons


def test_forget_person_guard_blocks_empty_preview_candidates(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    preview = build_forget_person_preview(db_path=db_path, person_identifier="missing")

    result = check_forget_person_write_allowed(
        preview=preview,
        approval_token=FORGET_PERSON_APPROVAL_TOKEN,
        backup_available=True,
        transaction_available=True,
        rollback_available=True,
        scanner_smoke_passed=True,
    )

    assert result.allowed is False
    assert "no_forget_candidates" in result.blocked_reasons
