"""Tests for local learning questions and learned rules."""

from __future__ import annotations

from friday.app.routine_detector import RoutineCandidate
from friday.storage.database import get_connection, setup_local_database
from friday.storage.learning_repository import LearningRepository
from friday.storage.repositories import ContactRepository


def _candidate() -> RoutineCandidate:
    return RoutineCandidate(
        kind="frequent_unknown_sender",
        subject_ref="sender:kunde@example.test",
        subject_label="Kunde Example <kunde@example.test>",
        question_text="Absender Kunde Example schreibt oft - wer ist das?",
        options=[
            {"id": "kunde_philip", "label": "Kunde - Betreuer Philip"},
            {"id": "ignorieren", "label": "Ignorieren"},
        ],
        suggestion="Kontakt einordnen",
        evidence=("2 lokale Nachrichten",),
    )


def test_candidate_becomes_one_open_question_idempotently(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file, seed_demo_data=False)
    repository = LearningRepository(db_file)

    first = repository.create_question_from_candidate(_candidate())
    second = repository.create_question_from_candidate(_candidate())

    assert first["id"] == second["id"]
    assert repository.list_open_questions()[0]["question_text"].startswith("Absender")


def test_answer_unknown_sender_creates_rule_and_contact(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file, seed_demo_data=False)
    repository = LearningRepository(db_file)
    question = repository.create_question_from_candidate(_candidate())

    result = repository.answer_question(question["id"], "kunde_philip")

    assert result["applied"] is True
    assert result["rule"]["kind"] == "sender_contact"
    assert result["rule"]["value"]["contact_type"] == "kunde"
    assert result["rule"]["value"]["betreuer"] == "philip"
    contacts = ContactRepository(db_file).get_contacts()
    assert contacts[0]["email_address"] == "kunde@example.test"


def test_answer_updates_hidden_ms_mail_relevance_for_philip_customer(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file, seed_demo_data=False)
    with get_connection(db_file) as connection:
        connection.execute(
            """
            INSERT INTO ms_mail_messages (
                account_id, message_id, sender, subject, snippet, processed,
                relevant_for_user, relevance_reason, relevance_method
            )
            VALUES ('office', 'm-1', 'Kunde Example <kunde@example.test>', 'Bitte Angebot',
                    'Bitte vorbereiten', 0, 0, 'office_not_relevant', 'deterministic')
            """
        )
    repository = LearningRepository(db_file)
    question = repository.create_question_from_candidate(_candidate())

    repository.answer_question(question["id"], "kunde_philip")

    with get_connection(db_file) as connection:
        row = connection.execute("SELECT relevant_for_user, relevance_method FROM ms_mail_messages").fetchone()
    assert row["relevant_for_user"] == 1
    assert row["relevance_method"] == "learned"


def test_dismiss_question_keeps_no_rule(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file, seed_demo_data=False)
    repository = LearningRepository(db_file)
    question = repository.create_question_from_candidate(_candidate())

    result = repository.dismiss_question(question["id"])

    assert result["question"]["status"] == "dismissed"
    assert repository.list_rules() == []


def test_rule_can_be_disabled(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file, seed_demo_data=False)
    repository = LearningRepository(db_file)
    question = repository.create_question_from_candidate(_candidate())
    rule = repository.answer_question(question["id"], "kunde_philip")["rule"]

    disabled = repository.set_rule_enabled(rule["id"], False)

    assert disabled["enabled"] is False
    assert repository.list_rules(include_disabled=False) == []
