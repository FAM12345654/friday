"""Storage package for Friday local data.

This package keeps database setup and read helpers separate:
`database.py` creates and seeds local SQLite data,
`repositories.py` reads from those tables.
"""

from friday.storage.database import setup_local_database
from friday.storage.repositories import CalendarRepository
from friday.storage.repositories import ContactRepository
from friday.storage.repositories import MessageRepository
from friday.storage.repositories import MessageSuggestionRepository
from friday.storage.repositories import TaskSuggestionRepository
from friday.storage.repositories import TaskRepository
from friday.storage.repositories import CalendarSuggestionRepository
from friday.storage.contact_context_repository import ContactContextRepository

__all__ = [
    "setup_local_database",
    "TaskRepository",
    "MessageRepository",
    "CalendarRepository",
    "ContactRepository",
    "MessageSuggestionRepository",
    "TaskSuggestionRepository",
    "CalendarSuggestionRepository",
    "ContactContextRepository",
]
