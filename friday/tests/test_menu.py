"""Tests for Friday menu constants and input handling."""

from __future__ import annotations


from friday.app import menu


def test_menu_options_and_exit_behavior() -> None:
    """MENU_OPTIONS should define the exact local German main flow."""
    assert isinstance(menu.MENU_OPTIONS, list)
    assert len(menu.MENU_OPTIONS) == 15

    assert menu.MENU_OPTIONS == [
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
        ("15", "Spam / Blockiert"),
    ]

    assert menu.is_exit("7") is True
    assert menu.is_exit("6") is False
    assert menu.is_exit("9") is False
    assert menu.is_exit("10") is False
    assert menu.is_exit("11") is False
    assert menu.is_exit("12") is False
    assert menu.is_exit("13") is False
    assert menu.is_exit("14") is False
    assert menu.is_exit("15") is False
    assert menu.is_exit("1") is False


def test_task_menu_options_and_show_task_menu(monkeypatch) -> None:
    """TASK_MENU_OPTIONS should contain local task actions."""
    assert menu.TASK_MENU_OPTIONS == [
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

    prompts: list[str] = []

    def _input(prompt: str) -> str:
        prompts.append(prompt)
        return " 11 "

    monkeypatch.setattr("builtins.input", _input)
    assert menu.show_task_menu() == "11"
    assert prompts == ["Auswahl (1-7, 9-12): "]


def test_show_menu_returns_stripped_input(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: " 6 ")
    assert menu.show_menu() == "6"


def test_account_menu_options_and_show_menu(monkeypatch) -> None:
    assert menu.ACCOUNT_MENU_OPTIONS == [
        ("1", "E-Mail-Konto Status anzeigen"),
        ("2", "E-Mail-Konto verbinden"),
        ("3", "E-Mail-Verbindung testen"),
        ("4", "E-Mail-Konto löschen"),
        ("5", "E-Mail-Aktivierung prüfen"),
        ("6", "WhatsApp Read-Bridge Status anzeigen"),
        ("7", "WhatsApp Read-Bridge Aktivierung prüfen"),
        ("8", "E-Mail-Agent-Notiz bearbeiten"),
        ("9", "WhatsApp-Agent-Notiz bearbeiten"),
        ("10", "Zurück zum Hauptmenü"),
    ]

    monkeypatch.setattr("builtins.input", lambda _: " 10 ")
    assert menu.show_account_menu() == "10"


def test_backup_restore_menu_options_and_show_menu(monkeypatch) -> None:
    assert menu.BACKUP_RESTORE_MENU_OPTIONS == [
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

    monkeypatch.setattr("builtins.input", lambda _: " 3 ")
    assert menu.show_backup_restore_menu() == "3"


def test_privacy_dashboard_menu_options_and_show_menu(monkeypatch) -> None:
    assert menu.PRIVACY_DASHBOARD_MENU_OPTIONS == [
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

    monkeypatch.setattr("builtins.input", lambda _: " 2 ")
    assert menu.show_privacy_dashboard_menu() == "2"
