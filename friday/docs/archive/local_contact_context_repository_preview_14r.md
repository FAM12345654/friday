# Local Contact Context Repository Preview 14R

## Ziel

Lokale Repository-Abstraktion für Kontakt-Kontext als technische Vorschau ohne Produktintegration.

14R ergänzt die Datenhaltung vorläufig als Preview, weiterhin ohne produktive CLI-Kopplung.

## Scope

- Reine Repository-Ebene + Tests.
- SQLite-Storage auf lokaler Datei.
- Keine CLI-Anbindung.
- Keine automatische Aktivierung in Review/Task-Flow.
- Keine zusätzlichen externen Integrationen.

## Implementierte Repository-API (Preview)

Geplant und umgesetzt in `friday/storage/contact_context_repository.py`:

- `create_contact_context(...)`
- `get_contact_context(contact_id)`
- `find_contact_by_normalized_name(normalized_name)`
- `list_contact_contexts()`
- `update_contact_context(...)`
- `delete_contact_context(contact_id)`

## Tabelle (Preview-Stand)

Neu eingeführt im lokalen Setup:

```sql
CREATE TABLE IF NOT EXISTS contact_contexts (
    contact_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    contact_type TEXT NOT NULL,
    nickname TEXT,
    relationship_context TEXT,
    source_context TEXT NOT NULL,
    user_approved_persistence INTEGER NOT NULL DEFAULT 0,
    sensitivity_checked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

## Abgedeckte Testfälle

- Erstellung:
  - leere Felder blockieren, Normalisierung, Default-Werte
  - dedupliziert durch `contact_id`
- Auslesen:
  - `get_contact_context`
  - `find_contact_by_normalized_name`
  - `list_contact_contexts`
- Änderung:
  - einzelne Felder gezielt editieren
  - boolesche Flags korrekt speichern (`0/1`)
- Löschung:
  - gültige ID löscht
  - unbekannte ID bleibt unkritisch

## Dokumentation der Nicht-Ziele

- Keine Persistenz-Freigabe in dieser Schicht.
- Keine Review-/CLI-Trigger auf diesem Schritt.
- Keine Produktionslogikänderung.

## Sicherheit

- Nur lokale SQLite.
- Keine externen Aktionen.
- Keine Netzwerkroutinen.
- Delete-Policy bleibt unverändert.
