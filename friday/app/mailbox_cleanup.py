"""Deterministic Gmail inbox cleanup guard and selector."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from friday import config
from friday.app.imap_mail_account_store import ImapMailAccount, list_imap_mail_accounts
from friday.app.imap_mail_writer import GMAIL_CLEANUP_LABEL
from friday.storage.repositories import normalize_blocked_sender_key

MAILBOX_CLEANUP_TOKEN = "POSTFACH AUFRAEUMEN"
OBVIOUS_NOISE_TERMS: tuple[str, ...] = (
    "instagram",
    "linkedin",
    "newsletter",
    "no-reply",
    "noreply",
    "marketing",
    "werbung",
    "angebot",
    "promo",
    "promotion",
    "unsubscribe",
)
CONTACT_PROTECTED_TYPES: tuple[str, ...] = (
    "kunde",
    "customer",
    "arbeit",
    "work",
    "familie",
    "family",
    "freund",
    "friend",
    "dienstleister",
)


@dataclass(frozen=True)
class MailboxCleanupCandidate:
    """One deterministic reversible Gmail cleanup candidate."""

    local_id: int
    account_id: str
    provider_message_id: str
    sender: str
    subject: str
    reason: str
    to_label: str = GMAIL_CLEANUP_LABEL
    source: str = "imap_mail"

    def to_dict(self) -> dict:
        return {
            "local_id": self.local_id,
            "account_id": self.account_id,
            "provider_message_id": self.provider_message_id,
            "sender": self.sender,
            "subject": self.subject,
            "reason": self.reason,
            "to_label": self.to_label,
            "source": self.source,
        }


@dataclass(frozen=True)
class MailboxCleanupActivationGate:
    """Guard result for enabling reversible Gmail inbox organization."""

    allowed: bool
    persisted: bool
    status: str
    message: str
    approval_token_required: str
    scanner_smoke_passed: bool
    account_connected: bool
    last_test_ok: bool
    mail_organize_enabled: bool
    real_email_enabled: bool
    external_send_enabled: bool
    blocked_reasons: tuple[str, ...]


def _email_from_text(value: str | None) -> str:
    match = re.search(r"[\w.!#$%&'*+/=?^`{|}~-]+@[\w.-]+", str(value or ""))
    return match.group(0).strip().lower() if match else ""


def _text_blob(message: dict) -> str:
    return " ".join(
        str(message.get(key) or "")
        for key in ("sender", "subject", "snippet", "body_full")
    ).casefold()


def _blocked_sender_keys(blocked_senders: Iterable[dict]) -> set[str]:
    keys: set[str] = set()
    for item in blocked_senders:
        if str(item.get("source") or "").strip().lower() != "imap_mail":
            continue
        key = str(item.get("sender_key") or "").strip().lower()
        if key:
            keys.add(key)
    return keys


def _contact_keys(contacts: Iterable[dict]) -> set[str]:
    keys: set[str] = set()
    for item in contacts:
        contact_type = str(item.get("contact_type") or "").strip().lower()
        if contact_type and contact_type not in CONTACT_PROTECTED_TYPES:
            continue
        for field in ("email_address", "name", "whatsapp_target"):
            raw = str(item.get(field) or "").strip()
            if not raw:
                continue
            keys.add(" ".join(raw.casefold().split()))
            email = _email_from_text(raw)
            if email:
                keys.add(email)
    return keys


def _sender_is_contact(sender: str, contact_keys: set[str]) -> bool:
    normalized = " ".join(str(sender or "").casefold().split())
    email = _email_from_text(sender)
    return bool((email and email in contact_keys) or (normalized and normalized in contact_keys))


def _is_obvious_noise(message: dict) -> bool:
    blob = _text_blob(message)
    return any(term in blob for term in OBVIOUS_NOISE_TERMS)


def select_obvious_mailbox_cleanup_candidates(
    messages: Iterable[dict],
    *,
    blocked_senders: Iterable[dict] = (),
    contacts: Iterable[dict] = (),
    limit: int = 25,
) -> tuple[MailboxCleanupCandidate, ...]:
    """Select only deterministic, reversible Gmail cleanup candidates."""
    safe_limit = max(1, min(int(limit), 100))
    blocked_keys = _blocked_sender_keys(blocked_senders)
    protected_contacts = _contact_keys(contacts)
    selected: list[MailboxCleanupCandidate] = []
    seen: set[str] = set()

    for message in messages:
        if len(selected) >= safe_limit:
            break
        if str(message.get("source") or "").strip().lower() != "imap_mail":
            continue
        provider_message_id = str(message.get("provider_message_id") or "").strip()
        if not provider_message_id or provider_message_id in seen:
            continue
        sender = str(message.get("sender") or "").strip()
        sender_key = normalize_blocked_sender_key("imap_mail", sender)
        blocked = sender_key in blocked_keys or int(message.get("is_spam") or 0) == 1
        if not blocked and _sender_is_contact(sender, protected_contacts):
            continue
        method = str(message.get("relevance_method") or "").strip().lower()
        reason = str(message.get("relevance_reason") or "").strip().lower()
        if method == "ki" or reason in {"unsicher", "customer", "kunde", "customer_betreuer_philip"}:
            continue
        if blocked:
            candidate_reason = "blocked_sender"
        elif _is_obvious_noise(message):
            candidate_reason = "deterministic_noise"
        else:
            continue
        selected.append(
            MailboxCleanupCandidate(
                local_id=int(message.get("id") or 0),
                account_id=str(message.get("account_id") or "default"),
                provider_message_id=provider_message_id,
                sender=sender,
                subject=str(message.get("subject") or "").strip(),
                reason=candidate_reason,
            )
        )
        seen.add(provider_message_id)
    return tuple(selected)


def build_mailbox_cleanup_activation_gate(
    *,
    approval_token: str,
    scanner_smoke_passed: bool,
    accounts: Iterable[ImapMailAccount] | None = None,
) -> MailboxCleanupActivationGate:
    """Build a no-write activation decision for Gmail cleanup."""
    known_accounts = tuple(accounts if accounts is not None else list_imap_mail_accounts())
    account_connected = bool(known_accounts)
    last_test_ok = any(bool(account.last_test_ok) for account in known_accounts)
    blocked: list[str] = []
    if approval_token != MAILBOX_CLEANUP_TOKEN:
        blocked.append("approval_token_required")
    if not scanner_smoke_passed:
        blocked.append("scanner_smoke_required")
    if not account_connected:
        blocked.append("gmail_account_required")
    if not last_test_ok:
        blocked.append("gmail_login_test_required")
    if config.ENABLE_REAL_EMAIL:
        blocked.append("real_email_send_must_stay_disabled")
    allowed = not blocked
    return MailboxCleanupActivationGate(
        allowed=allowed,
        persisted=False,
        status="ready" if allowed else "blocked",
        message=(
            "Gmail-Aufraeumen kann aktiviert werden."
            if allowed
            else "Gmail-Aufraeumen bleibt blockiert."
        ),
        approval_token_required=MAILBOX_CLEANUP_TOKEN,
        scanner_smoke_passed=bool(scanner_smoke_passed),
        account_connected=account_connected,
        last_test_ok=last_test_ok,
        mail_organize_enabled=config.ENABLE_MAIL_ORGANIZE,
        real_email_enabled=config.ENABLE_REAL_EMAIL,
        external_send_enabled=config.ENABLE_REAL_EMAIL,
        blocked_reasons=tuple(blocked),
    )


def _replace_gate_flag(source: str) -> str:
    if "ENABLE_MAIL_ORGANIZE = False" not in source:
        raise ValueError("Config-Flag wurde nicht gefunden.")
    return source.replace("ENABLE_MAIL_ORGANIZE = False", "ENABLE_MAIL_ORGANIZE = True", 1)


def apply_mailbox_cleanup_activation_to_config(
    *,
    config_path: Path,
    approval_token: str,
    scanner_smoke_passed: bool,
    execute_write: bool,
    post_write_validation=None,
    accounts: Iterable[ImapMailAccount] | None = None,
) -> MailboxCleanupActivationGate:
    """Enable Gmail cleanup flag only after the hard local safety gate."""
    gate = build_mailbox_cleanup_activation_gate(
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        accounts=accounts,
    )
    if not execute_write or not gate.allowed:
        return gate
    path = Path(config_path)
    source = path.read_text(encoding="utf-8")
    try:
        updated = _replace_gate_flag(source)
    except ValueError:
        return MailboxCleanupActivationGate(
            **{
                **gate.__dict__,
                "allowed": False,
                "status": "blocked",
                "message": "Config-Flag wurde nicht gefunden.",
                "blocked_reasons": ("config_flag_missing",),
            }
        )
    path.write_text(updated, encoding="utf-8")
    if post_write_validation is not None and not post_write_validation(path):
        path.write_text(source, encoding="utf-8")
        return MailboxCleanupActivationGate(
            **{
                **gate.__dict__,
                "allowed": False,
                "status": "blocked",
                "message": "Post-write Validation fehlgeschlagen.",
                "blocked_reasons": ("post_write_validation_failed",),
            }
        )
    return MailboxCleanupActivationGate(
        **{
            **gate.__dict__,
            "persisted": True,
            "status": "enabled",
            "message": "Gmail-Aufraeumen wurde aktiviert.",
            "mail_organize_enabled": True,
        }
    )
