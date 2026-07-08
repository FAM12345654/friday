"""Tests for the read-only privacy data management inventory."""

from __future__ import annotations

from friday.app.privacy_data_management import (
    build_privacy_data_management_inventory,
)


def test_privacy_data_management_inventory_is_read_only(tmp_path) -> None:
    inventory = build_privacy_data_management_inventory(
        local_data_dir=tmp_path / "local_data",
        database_path=tmp_path / "local_data" / "friday.db",
    )

    assert inventory.app_name == "Friday"
    assert inventory.local_mode is True
    assert inventory.sqlite_storage is True
    assert inventory.writes_performed is False
    assert inventory.deletes_performed is False
    assert inventory.exports_performed is False
    assert inventory.external_lookup_used is False


def test_privacy_data_management_does_not_create_paths(tmp_path) -> None:
    local_data_dir = tmp_path / "local_data"
    database_path = local_data_dir / "friday.db"

    build_privacy_data_management_inventory(
        local_data_dir=local_data_dir,
        database_path=database_path,
    )

    assert not local_data_dir.exists()
    assert not database_path.exists()


def test_privacy_data_management_lists_expected_areas(tmp_path) -> None:
    inventory = build_privacy_data_management_inventory(local_data_dir=tmp_path)
    area_names = {area.name for area in inventory.areas}

    assert area_names == {
        "Aufgaben",
        "Kontakt-Kontexte",
        "Review-Vorschlaege",
        "Exporte",
        "Backups",
        "Restore-Kopien",
        "Import-Reviews",
        "Obsidian-Previews/Writes",
        "Safety-Scanner",
    }


def test_privacy_data_management_hides_sensitive_details(tmp_path) -> None:
    inventory = build_privacy_data_management_inventory(local_data_dir=tmp_path)

    assert inventory.areas
    assert all(area.sensitive_details_hidden is True for area in inventory.areas)


def test_privacy_data_management_has_no_management_writes_or_deletes(tmp_path) -> None:
    inventory = build_privacy_data_management_inventory(local_data_dir=tmp_path)

    assert all(area.management_write_available is False for area in inventory.areas)
    assert all(area.management_delete_available is False for area in inventory.areas)


def test_privacy_data_management_accepts_summary_counts(tmp_path) -> None:
    inventory = build_privacy_data_management_inventory(
        local_data_dir=tmp_path,
        task_count=1,
        contact_context_count=2,
        review_suggestion_count=3,
        export_count=4,
        backup_count=5,
        restore_copy_count=6,
        import_review_count=7,
        obsidian_note_count=8,
        scanner_count=9,
    )
    counts = {area.name: area.count_label for area in inventory.areas}

    assert counts["Aufgaben"] == "1"
    assert counts["Kontakt-Kontexte"] == "2"
    assert counts["Review-Vorschlaege"] == "3"
    assert counts["Exporte"] == "4"
    assert counts["Backups"] == "5"
    assert counts["Restore-Kopien"] == "6"
    assert counts["Import-Reviews"] == "7"
    assert counts["Obsidian-Previews/Writes"] == "8"
    assert counts["Safety-Scanner"] == "9"


def test_privacy_data_management_blocks_risky_actions(tmp_path) -> None:
    inventory = build_privacy_data_management_inventory(local_data_dir=tmp_path)
    blocked_names = {action.name for action in inventory.blocked_actions}

    assert "Datenbereich direkt loeschen" in blocked_names
    assert "Aktive SQLite-Datenbank ersetzen" in blocked_names
    assert "Secrets oder .env exportieren" in blocked_names
    assert "Obsidian Vault scannen" in blocked_names
    assert "Externe Provider pruefen" in blocked_names


def test_privacy_data_management_paths_are_overridable(tmp_path) -> None:
    local_data_dir = tmp_path / "custom_data"
    database_path = local_data_dir / "custom.db"
    inventory = build_privacy_data_management_inventory(
        local_data_dir=local_data_dir,
        database_path=database_path,
    )
    paths = {area.name: area.path for area in inventory.areas}

    assert inventory.local_data_dir == str(local_data_dir)
    assert inventory.database_path == str(database_path)
    assert paths["Aufgaben"] == str(database_path)
    assert paths["Exporte"] == str(local_data_dir / "exports")
    assert paths["Backups"] == str(local_data_dir / "backups")
    assert paths["Restore-Kopien"] == str(local_data_dir / "restores")
