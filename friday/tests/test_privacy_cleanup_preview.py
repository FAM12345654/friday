"""Tests for the read-only privacy cleanup preview model."""

from __future__ import annotations

from friday.app.privacy_cleanup_preview import build_privacy_cleanup_preview


def test_privacy_cleanup_preview_is_read_only() -> None:
    preview = build_privacy_cleanup_preview()

    assert preview.writes_performed is False
    assert preview.deletes_performed is False
    assert preview.external_lookup_used is False


def test_privacy_cleanup_preview_lists_default_allowed_areas() -> None:
    preview = build_privacy_cleanup_preview()
    area_names = {item.area_name for item in preview.items}

    assert area_names == {
        "Exporte",
        "Backups",
        "Restore-Kopien",
        "Review-Vorschlaege",
        "Kontakt-Kontexte",
    }
    assert all(item.allowed is True for item in preview.items)


def test_privacy_cleanup_preview_accepts_explicit_counts() -> None:
    preview = build_privacy_cleanup_preview(
        export_count=1,
        backup_count=2,
        restore_copy_count=3,
        review_cleanup_count=4,
        contact_cleanup_count=5,
    )
    counts = {item.area_name: item.count_label for item in preview.items}

    assert counts["Exporte"] == "1"
    assert counts["Backups"] == "2"
    assert counts["Restore-Kopien"] == "3"
    assert counts["Review-Vorschlaege"] == "4"
    assert counts["Kontakt-Kontexte"] == "5"


def test_privacy_cleanup_preview_marks_required_tokens() -> None:
    preview = build_privacy_cleanup_preview()
    tokens = {item.area_name: item.requires_token for item in preview.items}

    assert tokens["Exporte"] == "EXPORT AUFRAEUMEN"
    assert tokens["Backups"] == "BACKUP AUFRAEUMEN"
    assert tokens["Restore-Kopien"] == "RESTORE AUFRAEUMEN"
    assert tokens["Review-Vorschlaege"] == "REVIEW AUFRAEUMEN"
    assert tokens["Kontakt-Kontexte"] == "KONTAKT LÖSCHEN"


def test_privacy_cleanup_preview_blocks_outside_allowed_roots() -> None:
    preview = build_privacy_cleanup_preview(
        target_paths={"Exporte": "C:/Users/Phili/Desktop/export"},
    )
    item = {entry.area_name: entry for entry in preview.items}["Exporte"]

    assert item.allowed is False
    assert item.blocked_reasons == ("outside_allowed_root",)
    assert "outside_allowed_root" in preview.blocked_actions


def test_privacy_cleanup_preview_blocks_active_database_and_secrets() -> None:
    preview = build_privacy_cleanup_preview(
        requested_areas=("aktive SQLite-DB", ".env / Secrets"),
    )
    items = {item.area_name: item for item in preview.items}

    assert items["aktive SQLite-DB"].allowed is False
    assert items["aktive SQLite-DB"].blocked_reasons == ("active_database_blocked",)
    assert items[".env / Secrets"].allowed is False
    assert items[".env / Secrets"].blocked_reasons == ("secrets_blocked",)


def test_privacy_cleanup_preview_blocks_obsidian_vault_and_global_delete() -> None:
    preview = build_privacy_cleanup_preview(
        requested_areas=("Obsidian Vault", "global"),
    )
    items = {item.area_name: item for item in preview.items}

    assert items["Obsidian Vault"].allowed is False
    assert items["Obsidian Vault"].blocked_reasons == ("obsidian_vault_blocked",)
    assert items["global"].allowed is False
    assert items["global"].blocked_reasons == ("global_delete_blocked",)


def test_privacy_cleanup_preview_blocks_unknown_area_without_future_gate() -> None:
    preview = build_privacy_cleanup_preview(requested_areas=("Unbekannt",))
    item = preview.items[0]

    assert item.allowed is False
    assert item.blocked_reasons == ("missing_future_gate",)
    assert item.requires_token == "nicht freigegeben"
