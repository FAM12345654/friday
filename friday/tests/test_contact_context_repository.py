"""Tests for contact context persistence preview repository."""

from __future__ import annotations

from friday.storage.contact_context_repository import ContactContextRepository
from friday.storage.database import initialize_database
from friday.app.contact_context_save_guard import CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE


def _build_repo(tmp_path):
    db_file = tmp_path / "friday.db"
    initialize_database(db_file)
    return ContactContextRepository(db_file)


def test_create_and_get_contact_context(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    context = repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
        source_context="nachrichten_review",
        nickname="Max",
        relationship_context="Projektleiter",
    )

    assert context["contact_id"] == "contact-01"
    assert context["display_name"] == "Max Mustermann"
    assert context["normalized_name"] == "max mustermann"
    assert context["contact_type"] == "kunde"
    assert context["nickname"] == "Max"
    assert context["relationship_context"] == "Projektleiter"
    assert context["source_context"] == "nachrichten_review"
    assert context["user_approved_persistence"] == 0
    assert context["sensitivity_checked"] == 0

    fetched = repository.get_contact_context("contact-01")
    assert fetched is not None
    assert fetched["contact_id"] == "contact-01"
    assert fetched["display_name"] == "Max Mustermann"


def test_create_contact_context_rejects_empty_values(tmp_path) -> None:
    repository = _build_repo(tmp_path)

    try:
        repository.create_contact_context(contact_id="", display_name="Max")
    except ValueError as error:
        assert str(error) == "Kontakt-ID wird benötigt."
    else:
        raise AssertionError("leere Kontakt-ID darf nicht erlaubt sein")

    try:
        repository.create_contact_context(contact_id="id", display_name="   ")
    except ValueError as error:
        assert str(error) == "Anzeige-Name darf nicht leer sein."
    else:
        raise AssertionError("leerer Kontaktname darf nicht erlaubt sein")


def test_create_contact_context_uses_unknown_values(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    context = repository.create_contact_context(
        contact_id="contact-02",
        display_name="  Max   Mustermann  ",
        contact_type="Chef",
    )

    assert context["contact_type"] == "sonstiges"


def test_find_contact_by_normalized_name(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    repository.create_contact_context(contact_id="contact-01", display_name="Lena Schmitt")

    found = repository.find_contact_by_normalized_name("lena schmitt")
    assert found is not None
    assert found["contact_id"] == "contact-01"
    assert found["display_name"] == "Lena Schmitt"


def test_list_contact_contexts_is_ordered(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    repository.create_contact_context(contact_id="id-b", display_name="Zwei")
    repository.create_contact_context(contact_id="id-a", display_name="Anna")

    contacts = repository.list_contact_contexts()
    assert len(contacts) == 2
    assert contacts[0]["display_name"] == "Anna"
    assert contacts[1]["display_name"] == "Zwei"


def test_update_contact_context_changes_requested_fields(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    repository.create_contact_context(
        contact_id="contact-update",
        display_name="Noch offen",
        contact_type="kunde",
    )

    updated = repository.update_contact_context(
        contact_id="contact-update",
        display_name="Update Name",
        contact_type="kollege",
        user_approved_persistence=1,
        sensitivity_checked=True,
    )

    assert updated is not None
    assert updated["display_name"] == "Update Name"
    assert updated["normalized_name"] == "update name"
    assert updated["contact_type"] == "kollege"
    assert updated["user_approved_persistence"] == 1
    assert updated["sensitivity_checked"] == 1


def test_update_contact_context_no_changes_keeps_row(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    created = repository.create_contact_context(contact_id="contact-keep", display_name="Behalten")

    same = repository.update_contact_context(contact_id="contact-keep")
    assert same is not None
    assert same["display_name"] == created["display_name"]


def test_update_contact_context_rejects_empty_display_name(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    repository.create_contact_context(contact_id="contact-empty", display_name="Behalt")

    try:
        repository.update_contact_context(contact_id="contact-empty", display_name=" ")
    except ValueError as error:
        assert str(error) == "Anzeige-Name darf nicht leer sein."
    else:
        raise AssertionError("leerer Name bei Update darf nicht erlaubt sein")


def test_update_contact_context_unknown_id_returns_none(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    assert repository.update_contact_context("does-not-exist", display_name="No") is None


def test_delete_contact_context_removes_row(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    repository.create_contact_context(contact_id="delete-me", display_name="Löschen")

    assert repository.delete_contact_context("delete-me") is True
    assert repository.get_contact_context("delete-me") is None


def test_delete_contact_context_unknown_id_returns_false(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    assert repository.delete_contact_context("not-found") is False


def test_create_contact_context_deduplicates_contact_id(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    first = repository.create_contact_context(
        contact_id="contact-dup",
        display_name="Doppel",
        contact_type="kunde",
        source_context="manuell",
    )
    second = repository.create_contact_context(
        contact_id="contact-dup",
        display_name="Doppel2",
        contact_type="kollege",
        source_context="person_bearbeiten",
    )

    assert first["contact_id"] == second["contact_id"]
    assert first["display_name"] == second["display_name"]


def test_create_contact_context_blocks_sensitive_relationship_context(tmp_path) -> None:
    repository = _build_repo(tmp_path)

    try:
        repository.create_contact_context(
            contact_id="blocked-health",
            display_name="Sensitive Person",
            relationship_context="medizinische Diagnose erwähnt",
            user_approved_persistence=True,
            sensitivity_checked=True,
        )
    except ValueError as error:
        assert str(error) == CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE
    else:
        raise AssertionError("sensibler Kontakt-Freitext darf nicht gespeichert werden")

    assert repository.get_contact_context("blocked-health") is None


def test_update_contact_context_blocks_sensitive_relationship_context(tmp_path) -> None:
    repository = _build_repo(tmp_path)
    repository.create_contact_context(
        contact_id="safe-contact",
        display_name="Safe Person",
        relationship_context="Projekt Alpha",
    )

    try:
        repository.update_contact_context(
            contact_id="safe-contact",
            relationship_context="private Diagnose bekannt",
            user_approved_persistence=True,
            sensitivity_checked=True,
        )
    except ValueError as error:
        assert str(error) == CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE
    else:
        raise AssertionError("sensibler Kontakt-Freitext darf kein Update auslösen")

    unchanged = repository.get_contact_context("safe-contact")
    assert unchanged is not None
    assert unchanged["relationship_context"] == "Projekt Alpha"
    assert unchanged["user_approved_persistence"] == 0
    assert unchanged["sensitivity_checked"] == 0
