"""Contact context agent: classifies local contacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from friday.config import DATA_DIR, USE_SQLITE_STORAGE, get_database_path
from friday.app.contact_category_classifier import normalize_contact_category
from friday.storage.repositories import ContactRepository


class ContactContextAgent:
    """Load local contacts and return their class labels."""

    VALID_TYPES = {"customer", "friend", "family", "work", "other", "familie", "arbeit", "freund", "kunde", "dienstleister", "sonstiges", "unbekannt"}

    def __init__(self, db_path: Path | None = None) -> None:
        # Contacts come only from local data for this skeleton.
        self.db_path = db_path or get_database_path()
        self.contact_repository = ContactRepository(self.db_path) if USE_SQLITE_STORAGE else None

    def load_contacts(self) -> List[Dict[str, Any]]:
        """Load contact list from local sample data."""
        if self.contact_repository is None:
            with (DATA_DIR / "sample_contacts.json").open("r", encoding="utf-8") as file:
                return json.load(file)
        return self.contact_repository.get_contacts()

    def create_contact(
        self,
        name: str,
        contact_type: str | None = "work",
        notes: str | None = "",
        email_address: str | None = None,
        whatsapp_target: str | None = None,
        betreuer: str | None = None,
    ) -> Dict[str, Any]:
        """Create a local contact entry."""
        if self.contact_repository is None:
            raise ValueError("Contact storage is not available in sample mode.")
        return self.contact_repository.create_contact(
            name=name,
            contact_type=contact_type,
            notes=notes,
            email_address=email_address,
            whatsapp_target=whatsapp_target,
            betreuer=betreuer,
        )

    def update_contact(
        self,
        contact_id: int,
        *,
        name: str | None = None,
        contact_type: str | None = None,
        notes: str | None = None,
        email_address: str | None = None,
        whatsapp_target: str | None = None,
        betreuer: str | None = None,
    ) -> Dict[str, Any] | None:
        """Update a local contact entry."""
        if self.contact_repository is None:
            raise ValueError("Contact storage is not available in sample mode.")
        return self.contact_repository.update_contact(
            contact_id,
            name=name,
            contact_type=contact_type,
            notes=notes,
            email_address=email_address,
            whatsapp_target=whatsapp_target,
            betreuer=betreuer,
        )

    def get_category_for_sender(self, sender: str) -> str:
        """Find the stored category for a sender name."""
        if self.contact_repository is None:
            sender_lower = sender.lower()
            for contact in self.load_contacts():
                if str(contact.get("name", "")).lower() == sender_lower:
                    category = str(contact.get("contact_type") or contact.get("category", "other")).lower()
                    return normalize_contact_category(category)
            return "sonstiges"
        return self.contact_repository.get_contact_type_by_name(sender)

    def find_contact_for_sender(self, sender: str) -> Dict[str, Any] | None:
        """Find a stored contact for a local sender identifier."""
        if self.contact_repository is None:
            sender_lower = sender.lower()
            for contact in self.load_contacts():
                if str(contact.get("name", "")).lower() == sender_lower:
                    return contact
            return None
        return self.contact_repository.find_contact_for_sender(sender)
