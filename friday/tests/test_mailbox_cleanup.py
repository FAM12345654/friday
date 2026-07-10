from __future__ import annotations

from pathlib import Path

from friday.app.imap_mail_account_store import build_imap_mail_account
from friday.app.mailbox_cleanup import (
    MAILBOX_CLEANUP_TOKEN,
    apply_mailbox_cleanup_activation_to_config,
    build_mailbox_cleanup_activation_gate,
    select_obvious_mailbox_cleanup_candidates,
)


def test_select_obvious_newsletter_noise_only() -> None:
    messages = [
        {
            "id": 1,
            "source": "imap_mail",
            "account_id": "a",
            "provider_message_id": "m1",
            "sender": "Instagram <no-reply@mail.instagram.com>",
            "subject": "Neuer Login",
        },
        {
            "id": 2,
            "source": "imap_mail",
            "account_id": "a",
            "provider_message_id": "m2",
            "sender": "Kunde <kunde@example.com>",
            "subject": "Bitte Angebot",
        },
        {
            "id": 3,
            "source": "ms_mail",
            "account_id": "a",
            "provider_message_id": "m3",
            "sender": "LinkedIn",
            "subject": "Newsletter",
        },
    ]
    contacts = [{"name": "Kunde", "email_address": "kunde@example.com", "contact_type": "kunde"}]

    selected = select_obvious_mailbox_cleanup_candidates(messages, contacts=contacts)

    assert [item.provider_message_id for item in selected] == ["m1"]
    assert selected[0].reason == "deterministic_noise"


def test_blocked_gmail_sender_is_selected() -> None:
    messages = [
        {
            "id": 1,
            "source": "imap_mail",
            "account_id": "a",
            "provider_message_id": "m1",
            "sender": "Bad <bad@example.com>",
            "subject": "Normal",
        },
    ]
    blocked = [{"source": "imap_mail", "sender_key": "bad@example.com"}]

    selected = select_obvious_mailbox_cleanup_candidates(messages, blocked_senders=blocked)

    assert len(selected) == 1
    assert selected[0].reason == "blocked_sender"


def test_uncertain_or_ai_relevance_is_not_selected() -> None:
    messages = [
        {
            "id": 1,
            "source": "imap_mail",
            "account_id": "a",
            "provider_message_id": "m1",
            "sender": "noreply@example.com",
            "subject": "Newsletter",
            "relevance_method": "ki",
        },
        {
            "id": 2,
            "source": "imap_mail",
            "account_id": "a",
            "provider_message_id": "m2",
            "sender": "noreply2@example.com",
            "subject": "Newsletter",
            "relevance_reason": "unsicher",
        },
    ]

    assert select_obvious_mailbox_cleanup_candidates(messages) == ()


def test_activation_gate_requires_exact_token_scanner_and_tested_account() -> None:
    account = build_imap_mail_account(
        provider="gmail",
        host="imap.gmail.com",
        port=993,
        username="test@example.com",
        app_password="pw",
        last_test_ok=True,
    )

    blocked = build_mailbox_cleanup_activation_gate(
        approval_token="JA",
        scanner_smoke_passed=True,
        accounts=[account],
    )
    allowed = build_mailbox_cleanup_activation_gate(
        approval_token=MAILBOX_CLEANUP_TOKEN,
        scanner_smoke_passed=True,
        accounts=[account],
    )

    assert blocked.allowed is False
    assert "approval_token_required" in blocked.blocked_reasons
    assert allowed.allowed is True


def test_apply_activation_updates_only_mail_organize_flag(tmp_path: Path) -> None:
    config_path = tmp_path / "config.py"
    config_path.write_text("ENABLE_MAIL_ORGANIZE = False\nENABLE_REAL_EMAIL = False\n", encoding="utf-8")
    account = build_imap_mail_account(
        provider="gmail",
        host="imap.gmail.com",
        port=993,
        username="test@example.com",
        app_password="pw",
        last_test_ok=True,
    )

    gate = apply_mailbox_cleanup_activation_to_config(
        config_path=config_path,
        approval_token=MAILBOX_CLEANUP_TOKEN,
        scanner_smoke_passed=True,
        execute_write=True,
        accounts=[account],
        post_write_validation=lambda path: "ENABLE_REAL_EMAIL = False" in path.read_text(encoding="utf-8"),
    )

    assert gate.persisted is True
    text = config_path.read_text(encoding="utf-8")
    assert "ENABLE_MAIL_ORGANIZE = True" in text
    assert "ENABLE_REAL_EMAIL = False" in text
