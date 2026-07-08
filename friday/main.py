"""Start Friday locally from the command line."""

from __future__ import annotations

from friday.app.interface import FridayInterface
from friday.storage.database import setup_local_database


def main() -> None:
    """Start Friday and open the simple terminal interface."""
    # Prepare local database tables and demo data before showing the UI.
    setup_local_database()
    # Friendly startup line requested in the specification.
    print("Friday local assistant started.")

    app = FridayInterface()
    app.run()


if __name__ == "__main__":
    main()
