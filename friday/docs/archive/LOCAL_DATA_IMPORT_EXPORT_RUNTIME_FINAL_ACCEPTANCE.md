# Local Data Import/Export Runtime Final Acceptance

## Ziel

Dieses Gate fasst den gesamten lokalen Datenexport-, Import-Review- und Import-Apply-Runtime-Bereich final zusammen.

Der Bereich umfasst:

- lokalen Datenexport unter `local_data/exports/`,
- read-only Import-Manifest-Review,
- read-only Import-Dry-Run,
- read-only Import-Apply-Vorschau,
- guarded Import-Apply-Schreibpfad,
- Nutzer-Doku und Runtime-Dokumentation.

## Finaler Runtime-Status

| Bereich | Status | Schreibverhalten |
|---|---|---|
| Lokaler Datenexport | final angenommen | Schreibt nur lokal mit `DATEN EXPORTIEREN` |
| Lokaler Datenimport pruefen | final angenommen | Read-only, schreibt nie |
| Import-Apply-Vorschau | final angenommen | Read-only, schreibt nie |
| Import nach Freigabe anwenden | final angenommen | Schreibt nur lokal mit Schutzkette und `IMPORT ANWENDEN` |

## Gepruefte Hauptartefakte

| Artefakt | Zweck | Status |
|---|---|---|
| `LOCAL_DATA_EXPORT_FINAL_ACCEPTANCE_GATE.md` | Finaler Annahmestand fuer lokalen Datenexport | abgeschlossen |
| `LOCAL_DATA_EXPORT_RUNTIME_READINESS_SUMMARY.md` | Runtime-Stand fuer lokalen Datenexport | abgeschlossen |
| `LOCAL_DATA_IMPORT_REVIEW_FINAL_ACCEPTANCE_GATE.md` | Finaler Annahmestand fuer read-only Import-Review | abgeschlossen |
| `LOCAL_DATA_IMPORT_RUNTIME_READINESS_SUMMARY.md` | Runtime-Stand fuer read-only Import-Review | abgeschlossen |
| `LOCAL_DATA_IMPORT_APPLY_FINAL_ACCEPTANCE_GATE.md` | Finaler Annahmestand fuer lokalen Import-Apply | abgeschlossen |
| `LOCAL_DATA_IMPORT_EXPORT_FINAL_ACCEPTANCE_GATE.md` | Frueherer gemeinsamer Stand fuer Export, Import-Review und Apply-Vorschau | abgeschlossen |
| `LOCAL_DATA_IMPORT_EXPORT_USER_GUIDE_FINALIZATION.md` | Nutzer-Doku fuer Export/Import-Review/Apply-Vorschau | abgeschlossen |

## CLI-Menue-Status

Im Backup-/Restore-Menue sind die lokalen Datenpfade getrennt:

| Menuepunkt | Bedeutung | Status |
|---|---|---|
| `5. Lokaler Datenexport Vorschau anzeigen` | Zeigt Export-Preview und kann mit hartem Token exportieren | guarded Write |
| `6. Lokalen Datenimport pruefen` | Prueft einen Exportordner read-only | read-only |
| `7. Import-Apply-Vorschau anzeigen` | Zeigt Apply-Status read-only | read-only |
| `8. Import nach Freigabe anwenden` | Wendet gueltigen Export lokal an | guarded Write |
| `9. Zurueck zum Hauptmenue` | Rueckkehr ohne Write | read-only |

## Freigegebene lokale Schreibpfade

### Datenexport

Freigegeben nur wenn:

- Ziel unter `local_data/exports/` liegt,
- Safety Smoke PASS ist,
- Guard freigibt,
- exakt `DATEN EXPORTIEREN` eingegeben wird,
- ausgeschlossene Inhalte nicht exportiert werden.

### Import-Apply

Freigegeben nur wenn:

- Exportordner gueltig ist,
- Manifest erlaubt ist,
- Dry-Run erlaubt ist,
- lokaler Backup-Schutz vorhanden ist,
- Safety Smoke PASS ist,
- Guard freigibt,
- exakt `IMPORT ANWENDEN` eingegeben wird,
- nur erlaubte lokale Scopes geschrieben werden:
  - `tasks`,
  - `contact_contexts`,
  - `review_suggestions`.

## Nicht freigegeben

- Externe Aktionen.
- Netzwerk- oder Provider-Aufrufe.
- Cloud-Integrationen.
- Echte Nachrichten.
- Echte Kalendertermine.
- Restore in aktive Projektdateien.
- Import privater Roh-Nachrichten.
- Import sensibler Kontakt-Freitexte.
- Import von Secrets, Tokens oder `.env`-Inhalten.
- Datenbankschema-Aenderungen im Import-/Export-Runtime-Pfad.
- Automatische Writes ohne harte Tokens.

## Teststatus

Relevante Fokusbereiche:

- `friday/tests/test_local_data_export_preview.py`
- `friday/tests/test_local_data_export_guard.py`
- `friday/tests/test_local_data_export_writer.py`
- `friday/tests/test_local_data_import_manifest_reader.py`
- `friday/tests/test_local_data_import_dry_run.py`
- `friday/tests/test_local_data_import_apply_preview.py`
- `friday/tests/test_local_data_import_apply_write_guard.py`
- `friday/tests/test_local_data_import_apply_writer.py`
- `friday/tests/test_interface_main_menu_e2e.py`
- `friday/tests/test_menu.py`

Akzeptierter Full-Regression-Stand:

- `python -m pytest friday/tests` -> `677 passed`
- `python -m compileall friday` -> erfolgreich
- `python scripts/friday_safety_smoke.py` -> `Overall: PASS`
- `git diff --check` -> sauber

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Cloud-Integration.
- Keine Datenbankschema-Aenderung.
- Lokale SQLite-Datenhaltung.
- Safety-Flags unveraendert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy unveraendert:
  - `"ja"` loescht nicht,
  - `"JA"` loescht,
  - `" JA "` bleibt per `strip()` zugelassen.

## Final Acceptance Ergebnis

Der lokale Datenexport-/Import-Runtime-Bereich ist final angenommen.

Friday kann lokale Daten sicher exportieren, lokal pruefen und nach Schutzkette lokal anwenden. Alle Pfade bleiben lokal, tokenpflichtig fuer Writes und durch Safety Smoke, Guards und Tests abgesichert.

## Empfehlung fuer naechsten Build Step

Local Data Import/Export Documentation Finalization: README und zentrale Dokumentationsuebersicht final auf den komplett abgeschlossenen Runtime-Bereich synchronisieren.
