"""Contact context agent: classifies local contacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from friday.config import DATA_DIR, USE_SQLITE_STORAGE, get_database_path
from friday.storage.repositories import ContactRepository


class ContactContextAgent:
    """Load local contacts and return their class labels."""

    VALID_TYPES = {"customer", "friend", "family", "work", "other"}

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

    def get_category_for_sender(self, sender: str) -> str:
        """Find the stored category for a sender name."""
        if self.contact_repository is None:
            sender_lower = sender.lower()
            for contact in self.load_contacts():
                if str(contact.get("name", "")).lower() == sender_lower:
                    category = str(contact.get("contact_type") or contact.get("category", "other")).lower()
                    return category if category in self.VALID_TYPES else "other"
            return "other"
        return self.contact_repository.get_contact_type_by_name(sender)
