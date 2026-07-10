"""Tests for local Microsoft mail preview repository."""

from __future__ import annotations

from friday.storage.database import setup_local_database
from friday.storage.repositories import BlockedSenderRepository, ContactRepository, MsMailMessageRepository


def test_ms_mail_repository_upserts_and_deduplicates(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)

    repo.upsert_messages(
        [
            {
                "message_id": "graph-1",
                "sender": "kunde@example.test",
                "subject": "Bitte Philip prüfen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Kurz",
            }
        ]
    )
    repo.upsert_messages(
        [
            {
                "message_id": "graph-1",
                "sender": "kunde@example.test",
                "subject": "Bitte Philip prüfen aktualisiert",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Kurz",
            }
        ]
    )

    items = repo.list_messages(include_all=True)

    assert len(items) == 1
    assert items[0]["subject"] == "Bitte Philip prüfen aktualisiert"
    assert "body" not in items[0]


def test_ms_mail_repository_stores_full_body_and_recipients(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)

    stored = repo.upsert_messages(
        [
            {
                "message_id": "graph-body",
                "sender": "info@example.test",
                "subject": "Bitte Philip prüfen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Kurz",
                "body_full": "Voller lokaler Mailtext.",
                "recipients": [{"type": "to", "name": "Philip", "address": "philip@example.test"}],
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )[0]
    detail = repo.get_message_by_id(stored["id"])

    assert detail is not None
    assert detail["body_full"] == "Voller lokaler Mailtext."
    assert detail["body_fetched_at"]
    assert '"Philip"' in detail["recipients"]
    assert detail["recipients"] == detail["recipients_json"]
    assert stored["relevance_method"] == "recipient"


def test_ms_mail_repository_marks_processed(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)
    item = repo.upsert_messages([{"message_id": "graph-1", "subject": "A"}])[0]

    repo.mark_processed(item["id"], suggestion_created=True)

    assert repo.get_unprocessed_messages() == []
    assert repo.list_messages()[0]["suggestion_created"] == 1


def test_ms_mail_repository_keeps_same_graph_id_per_account(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)

    repo.upsert_messages(
        [{"message_id": "graph-1", "subject": "Office"}],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )
    repo.upsert_messages(
        [{"message_id": "graph-1", "subject": "Philip"}],
        account_id="philip_familienhelden_at",
        account_username="philip@familienhelden.at",
    )

    items = repo.list_messages(include_all=True)

    assert len(items) == 2
    assert {item["account_id"] for item in items} == {
        "office_familienhelden_at",
        "philip_familienhelden_at",
    }
    assert {item["provider_message_id"] for item in items} == {"graph-1"}
    assert len(repo.list_messages(account_id="office_familienhelden_at", include_all=True)) == 1


def test_ms_mail_repository_hides_non_relevant_office_mail_by_default(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)

    repo.upsert_messages(
        [
            {
                "message_id": "graph-office-alex",
                "sender": "info@example.test",
                "subject": "Allgemeine Info",
                "snippet": "Bitte an Alex weitergeben.",
                "recipients": [{"name": "Alex", "address": "alex@familienhelden.at"}],
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )

    assert repo.list_messages() == []
    all_items = repo.list_messages(include_all=True)
    assert len(all_items) == 1
    assert all_items[0]["relevant_for_user"] == 0
    assert all_items[0]["relevance_reason"] == "not_relevant"
    assert all_items[0]["relevance_method"] == "deterministic"


def test_ms_mail_repository_uses_ai_decider_for_full_body_office_relevance(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)

    def _ai_decider(body_full, _context):
        assert "Nur Alex" in body_full
        return {"relevant": False, "reason": "KI: nur Alex", "confidence": 0.9}

    repo = MsMailMessageRepository(db_path, ai_relevance_decider=_ai_decider)

    repo.upsert_messages(
        [
            {
                "message_id": "graph-office-ai",
                "sender": "info@example.test",
                "subject": "Allgemeine Info",
                "snippet": "Bitte lesen.",
                "body_full": "Nur Alex ist betroffen.",
                "recipients": [{"name": "Alex", "address": "alex@familienhelden.at"}],
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )

    assert repo.list_messages() == []
    item = repo.list_messages(include_all=True)[0]
    assert item["relevant_for_user"] == 0
    assert item["relevance_reason"] == "KI: nur Alex"
    assert item["relevance_method"] == "ki"


def test_ms_mail_repository_fallback_keeps_unclear_office_mail_visible(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(
        db_path,
        ai_relevance_decider=lambda _body, _context: {"invalid": "shape"},
    )

    repo.upsert_messages(
        [
            {
                "message_id": "graph-office-fallback",
                "sender": "info@example.test",
                "subject": "Allgemeine Info",
                "snippet": "Bitte lesen.",
                "body_full": "Unklarer voller Text.",
                "recipients": [{"name": "Alex", "address": "alex@familienhelden.at"}],
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )

    item = repo.list_messages()[0]
    assert item["relevant_for_user"] == 1
    assert item["relevance_reason"] == "unsicher"
    assert item["relevance_method"] == "unsicher"


def test_ms_mail_repository_does_not_call_ai_by_default_for_unclear_office_body(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)

    repo.upsert_messages(
        [
            {
                "message_id": "graph-office-no-ai",
                "sender": "info@example.test",
                "subject": "Allgemeine Info",
                "snippet": "Bitte lesen.",
                "body_full": "Unklarer voller Text.",
                "recipients": [{"name": "Alex", "address": "alex@familienhelden.at"}],
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )

    item = repo.list_messages()[0]
    assert item["relevant_for_user"] == 1
    assert item["relevance_reason"] == "unsicher"
    assert item["relevance_method"] == "unsicher"


def test_ms_mail_repository_keeps_philip_relevant_office_mail_visible(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)

    repo.upsert_messages(
        [
            {
                "message_id": "graph-office-philip",
                "sender": "info@example.test",
                "subject": "Neue Anfrage",
                "snippet": "Bitte prüfen.",
                "recipients": [{"name": "Philip Zeitler", "address": "philip@familienhelden.at"}],
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )

    items = repo.list_messages()
    assert len(items) == 1
    assert items[0]["relevant_for_user"] == 1
    assert items[0]["relevance_reason"] == "recipient"


def test_ms_mail_repository_keeps_personal_mailbox_visible(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)

    repo.upsert_messages(
        [
            {
                "message_id": "graph-personal",
                "sender": "newsletter@example.test",
                "subject": "Newsletter",
                "snippet": "Allgemeines Update.",
            }
        ],
        account_id="philip_familienhelden_at",
        account_username="philip@familienhelden.at",
    )

    items = repo.list_messages()
    assert len(items) == 1
    assert items[0]["relevance_reason"] == "personal_mailbox"


def test_ms_mail_repository_matches_customer_betreuer_philip(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    ContactRepository(db_path).create_contact(
        name="Kunde Eins",
        contact_type="kunde",
        email_address="kunde@example.test",
        betreuer="philip",
    )
    repo = MsMailMessageRepository(db_path)

    repo.upsert_messages(
        [
            {
                "message_id": "graph-kunde",
                "sender": "Kunde Eins <kunde@example.test>",
                "subject": "Bitte Angebot vorbereiten",
                "snippet": "Danke.",
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )

    items = repo.list_messages()
    assert len(items) == 1
    assert items[0]["relevance_reason"] == "betreuer"


def test_ms_mail_repository_hides_spam_by_default_and_restores_on_unblock(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    mail_repo = MsMailMessageRepository(db_path)
    block_repo = BlockedSenderRepository(db_path)

    blocked = block_repo.block_sender(
        source="ms_mail",
        sender="spam@example.test",
        label="Spam Sender",
    )
    stored = mail_repo.upsert_messages(
        [
            {
                "message_id": "graph-spam",
                "sender": "Spam <spam@example.test>",
                "subject": "Unerwünscht",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Werbung",
            }
        ]
    )[0]

    assert stored["is_spam"] == 1
    assert mail_repo.list_messages() == []
    assert mail_repo.list_messages(include_spam=True)[0]["subject"] == "Unerwünscht"

    block_repo.unblock_sender(blocked["id"])

    restored = mail_repo.list_messages()
    assert len(restored) == 1
    assert restored[0]["is_spam"] == 0


def test_ms_mail_repository_stores_imap_mail_source_in_unified_table(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)

    stored = repo.upsert_messages(
        [
            {
                "message_id": "gmail-1",
                "source": "imap_mail",
                "sender": "Kollegin <kollegin@example.test>",
                "subject": "Bitte Philip Rechnung pruefen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Bitte pruefen.",
            }
        ],
        account_id="gmail_philip07102000_gmail_com",
        account_username="philip07102000@gmail.com",
    )[0]

    item = repo.get_message_by_id(stored["id"])
    assert item is not None
    assert item["source"] == "imap_mail"
    assert item["account_username"] == "philip07102000@gmail.com"
    assert item["relevance_reason"] == "personal_mailbox"


def test_blocked_imap_mail_sender_syncs_as_spam(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    mail_repo = MsMailMessageRepository(db_path)
    block_repo = BlockedSenderRepository(db_path)

    block_repo.block_sender(source="imap_mail", sender="Spam <spam@example.test>", label="Spam")
    stored = mail_repo.upsert_messages(
        [
            {
                "message_id": "gmail-spam",
                "source": "imap_mail",
                "sender": "Spam <spam@example.test>",
                "subject": "Werbung",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Nicht relevant.",
            }
        ],
        account_id="gmail_philip07102000_gmail_com",
        account_username="philip07102000@gmail.com",
    )[0]

    assert stored["is_spam"] == 1
    assert mail_repo.list_messages() == []
    spam_view = mail_repo.list_messages(include_spam=True)
    assert len(spam_view) == 1
    assert spam_view[0]["source"] == "imap_mail"


def test_unblocking_imap_mail_sender_restores_local_messages(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    mail_repo = MsMailMessageRepository(db_path)
    block_repo = BlockedSenderRepository(db_path)

    blocked = block_repo.block_sender(source="imap_mail", sender="spam@example.test", label="Spam")
    mail_repo.upsert_messages(
        [
            {
                "message_id": "gmail-spam-restore",
                "source": "imap_mail",
                "sender": "spam@example.test",
                "subject": "Bitte Philip pruefen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Bitte erledigen.",
            }
        ],
        account_id="gmail_philip07102000_gmail_com",
        account_username="philip07102000@gmail.com",
    )

    block_repo.unblock_sender(blocked["id"])

    restored = mail_repo.list_messages()
    assert len(restored) == 1
    assert restored[0]["is_spam"] == 0
    assert restored[0]["source"] == "imap_mail"
