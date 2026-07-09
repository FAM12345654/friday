"""Simple terminal text menu for Friday."""

from typing import List, Tuple


MENU_TITLE = "Hauptmenü von Friday"

MENU_OPTIONS: List[Tuple[str, str]] = [
    ("1", "Aufgaben verwalten"),
    ("2", "Nachrichten anzeigen"),
    ("3", "Kalender-Vorschläge anzeigen"),
    ("4", "Morgenübersicht anzeigen"),
    ("5", "Sicherheitsstatus anzeigen"),
    ("6", "Vorschläge prüfen / freigeben"),
    ("7", "Beenden"),
    ("8", "Hilfe / Übersicht"),
    ("9", "Kontakt-Kontext anzeigen"),
    ("10", "Obsidian Brain Preview"),
    ("11", "Backup / Restore"),
    ("12", "Privacy Dashboard"),
    ("13", "E-Mail-Entwurf Preview"),
    ("14", "Konten"),
]

ACCOUNT_MENU_OPTIONS: List[Tuple[str, str]] = [
    ("1", "E-Mail-Konto Status anzeigen"),
    ("2", "E-Mail-Konto verbinden"),
    ("3", "E-Mail-Verbindung testen"),
    ("4", "E-Mail-Konto löschen"),
    ("5", "E-Mail-Aktivierung prüfen"),
    ("6", "WhatsApp Read-Bridge Status anzeigen"),
    ("7", "WhatsApp Read-Bridge Aktivierung prüfen"),
    ("8", "Zurück zum Hauptmenü"),
]

TASK_MENU_OPTIONS: List[Tuple[str, str]] = [
    ("1", "Offene Aufgaben anzeigen"),
    ("2", "Neue Aufgabe erstellen"),
    ("3", "Aufgabe bearbeiten"),
    ("4", "Aufgabe als erledigt markieren"),
    ("5", "Aufgaben suchen / filtern"),
    ("6", "Aufgabe archivieren"),
    ("7", "Aufgabe dauerhaft löschen"),
    ("9", "Aufgabe schnell erfassen"),
    ("10", "Aufgaben als Markdown exportieren"),
    ("11", "Lokale Tagesplanung anzeigen"),
    ("12", "Zurück zum Hauptmenü"),
]

BACKUP_RESTORE_MENU_OPTIONS: List[Tuple[str, str]] = [
    ("1", "Backup-Vorschau anzeigen"),
    ("2", "Backup lokal erstellen"),
    ("3", "Restore-Dry-Run prüfen"),
    ("4", "Restore-Kopie erstellen"),
    ("5", "Lokaler Datenexport Vorschau anzeigen"),
    ("6", "Lokalen Datenimport prüfen"),
    ("7", "Import-Apply-Vorschau anzeigen"),
    ("8", "Import nach Freigabe anwenden"),
    ("9", "Zurück zum Hauptmenü"),
    ("10", "Backups aufraeumen"),
]

PRIVACY_DASHBOARD_MENU_OPTIONS: List[Tuple[str, str]] = [
    ("1", "Lokale Datenbereiche anzeigen"),
    ("2", "Safety-Flags anzeigen"),
    ("3", "Externe Aktionen anzeigen"),
    ("4", "Gated Actions anzeigen"),
    ("5", "Safety Scanner anzeigen"),
    ("6", "Privacy Data Management Inventory anzeigen"),
    ("7", "Privacy Cleanup Preview anzeigen"),
    ("8", "Privacy Cleanup ausführen"),
    ("9", "DB-Cleanup Preview anzeigen"),
    ("10", "DB-Cleanup ausführen"),
    ("11", "Zurück zum Hauptmenü"),
]


def show_menu() -> str:
    """Show the menu and return the selected option as stripped string."""
    print("\n" + "=" * 40)
    print(MENU_TITLE)
    print("=" * 40)
    print("Hinweis: Friday bleibt lokal. Externe Aktionen sind deaktiviert.")
    for option, label in MENU_OPTIONS:
        print(f"{option}. {label}")
    return input("Auswahl (1-14): ").strip()


def show_account_menu() -> str:
    """Show the local accounts submenu and return the selection."""
    print("\n" + "-" * 40)
    print("Konten")
    print("-" * 40)
    print("Hinweis: E-Mail bleibt deaktiviert, bis EMAIL AKTIVIEREN spaeter ausgefuehrt wird.")
    print("WhatsApp-Senden bleibt Deep-Link ueber dein Handy; Read-Bridge ist separat gegatet.")
    for option, label in ACCOUNT_MENU_OPTIONS:
        print(f"{option}. {label}")
    return input("Auswahl (1-8): ").strip()


def show_task_menu() -> str:
    """Show the task submenu and return the selected option."""
    print("\n" + "-" * 40)
    print("Aufgaben verwalten")
    print("-" * 40)
    for option, label in TASK_MENU_OPTIONS:
        print(f"{option}. {label}")
    return input("Auswahl (1-7, 9-12): ").strip()


def show_backup_restore_menu() -> str:
    """Show the read-only backup/restore submenu and return the selected option."""
    print("\n" + "-" * 40)
    print("Backup / Restore")
    print("-" * 40)
    print("Hinweis: Backup/Restore bleibt lokal und nutzt harte Freigabe-Tokens.")
    print("9 führt zurück zum Hauptmenü.")
    for option, label in BACKUP_RESTORE_MENU_OPTIONS:
        print(f"{option}. {label}")
    return input("Auswahl (1-10): ").strip()


def show_privacy_dashboard_menu() -> str:
    """Show the read-only privacy dashboard submenu and return the selection."""
    print("\n" + "-" * 40)
    print("Privacy Dashboard")
    print("-" * 40)
    print("Hinweis: Anzeigen sind read-only; Cleanup braucht harte Freigabe-Tokens.")
    print("11 führt zurück zum Hauptmenü.")
    for option, label in PRIVACY_DASHBOARD_MENU_OPTIONS:
        print(f"{option}. {label}")
    return input("Auswahl (1-11): ").strip()


def is_exit(choice: str) -> bool:
    """Return True only for the explicit exit option."""
    return choice == "7"
