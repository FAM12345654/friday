# Local Data Import Dry-Run Model

## Ziel

Dieser Schritt ergaenzt ein isoliertes read-only Dry-Run-Modell fuer lokale Datenexporte.

Der Dry-Run prueft Exportdateien nur als Vorschau und fuehrt keinen Import oder Restore aus.

## Umgesetzte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/local_data_import_dry_run.py` | Read-only Import-Dry-Run-Modell |
| `friday/tests/test_local_data_import_dry_run.py` | Fokus-Tests fuer gueltige und blockierte Dry-Run-Faelle |
| `friday/docs/LOCAL_DATA_IMPORT_DRY_RUN_MODEL.md` | Dokumentation dieses Bausteins |

## Abgesicherte Verhaltensweisen

- Dry-Run blockiert, wenn der Manifest Reader blockiert.
- Exportordner muss unter `local_data/exports` liegen.
- Fehlende erwartete Exportdateien blockieren.
- Ungueltige JSON-Dateien blockieren.
- Sensible Kontaktfelder blockieren.
- Rohe private Review-/Nachrichtentexte blockieren.
- Aktivierte externe Safety-Flags blockieren.
- `external_lookup_used=True` blockiert.
- Gueltige Exporte werden read-only geprueft.
- Dry-Run schreibt keine Dateien.
- Dry-Run oeffnet keine aktive SQLite-Datenbank.

## Gepruefte Exportdateien

| Datei | Zweck |
|---|---|
| `manifest.json` | Manifest aus dem Export Writer |
| `tasks/tasks.json` | lokale Aufgaben-Zusammenfassung |
| `tasks/tasks.md` | lokale Aufgaben-Markdown-Zusammenfassung |
| `contacts/contact_contexts.json` | erlaubte Kontakt-Kontext-Felder |
| `review/review_suggestions.json` | erlaubte Review-/Vorschlagsfelder |
| `safety/safety_status.json` | lokale Safety-Flags |
| `docs/export_notes.md` | Export-Hinweis |

## Nicht freigegeben

Weiterhin nicht freigegeben sind:

- Import,
- Restore,
- aktiver DB-Write,
- In-Place-Restore,
- Merge aktiver Daten,
- CLI-Import,
- Cloud-Sync,
- externe Provider.

## Safety-Bewertung

- Keine externen Aktionen.
- Kein Import.
- Kein Restore.
- Kein Datei-Write.
- Keine Datenbankschema-Aenderung.
- Keine aktive SQLite-Datenbank wird geoeffnet.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte `Local Data Import Dry-Run Readiness Gate` folgen.

Dieser Schritt sollte pruefen und dokumentieren:

- Dry-Run ist read-only,
- Dry-Run ist scanner-clean,
- Dry-Run ist kompatibel mit Export Writer und Manifest Reader,
- Import/Restore bleiben nicht freigegeben.
