# Local Data Import/Export Final Acceptance Gate

## Ziel

Dieses Gate nimmt den lokalen Datenexport-/Import-Review-/Apply-Preview-Block final an.

Der Abschluss betrifft nur den bereits vorhandenen lokalen Runtime-Stand:

- lokaler Datenexport,
- read-only Import-Review,
- read-only Import-Dry-Run,
- read-only Import-Apply-Vorschau,
- Nutzer-Doku und Matrix-Dokumentation.

Es wird kein echter Import freigegeben.

## Gepruefte Bereiche

| Bereich | Status | Ergebnis |
|---|---|---|
| Local Data Export Preview | abgeschlossen | Vorschau ohne externe Aktion |
| Local Data Export Guard | abgeschlossen | Token, Zielpfad, Safety Smoke und Excludes geprueft |
| Local Data Export Writer | abgeschlossen | schreibt nur guard-basiert unter `local_data/exports/` |
| Local Data Export CLI Approval | abgeschlossen | CLI-Export nur mit `DATEN EXPORTIEREN` |
| Local Data Import Manifest Reader | abgeschlossen | liest `manifest.json` read-only |
| Local Data Import Dry-Run | abgeschlossen | prueft Exportdateien read-only |
| Local Data Import Review CLI | abgeschlossen | zeigt Manifest und Dry-Run ohne Import |
| Local Data Import Apply Preview Model | abgeschlossen | erzeugt Apply-Vorschau ohne Write |
| Local Data Import Apply Preview CLI | abgeschlossen | zeigt Apply-Vorschau read-only |
| Local Data Import/Export Runtime Finalization | abgeschlossen | Runtime-Stand dokumentiert |
| Local Data Import/Export User Guide Finalization | abgeschlossen | Nutzer-Doku finalisiert |

## Finales Annahmeergebnis

Freigegeben ist:

- lokaler Datenexport unter `local_data/exports/`,
- Export nur mit Safety Smoke, Guard und hartem Token `DATEN EXPORTIEREN`,
- read-only Import-Review,
- read-only Manifest Reader,
- read-only Import-Dry-Run,
- read-only Import-Apply-Vorschau,
- Anzeige von Warnungen, Blockiergruenden und geplanten Sektionen.

Nicht freigegeben ist:

- echter Import in aktive Friday-Daten,
- aktiver SQLite-Write durch Import,
- In-Place-Restore,
- automatisches Zusammenfuehren,
- Konfliktloesung mit Schreibeffekt,
- Abfrage von `IMPORT ANWENDEN`,
- Import von Secrets,
- Import privater Roh-Nachrichten,
- Import sensibler Kontakt-Freitexte,
- externe Provider oder Netzwerkaktionen.

## Abgesicherte harte Tokens

| Token | Status |
|---|---|
| `BACKUP ERSTELLEN` | freigegeben fuer lokalen Backup Write |
| `RESTORE AUSFUEHREN` | freigegeben fuer Restore-Kopie in separaten Zielordner |
| `DATEN EXPORTIEREN` | freigegeben fuer lokalen Datenexport |
| `IMPORT ANWENDEN` | nicht freigegeben, wird nicht abgefragt |

## Teststatus

Aktueller Abschlussstand:

- `python -m pytest friday/tests` -> `642 passed`
- `python -m compileall friday` -> erfolgreich
- `python scripts/friday_safety_smoke.py` -> `Overall: PASS`
- `git diff --check` -> sauber

Relevante Testbereiche:

- `test_local_data_export_preview.py`
- `test_local_data_export_guard.py`
- `test_local_data_export_writer.py`
- `test_local_data_import_manifest_reader.py`
- `test_local_data_import_dry_run.py`
- `test_local_data_import_apply_preview.py`
- `test_interface_main_menu_e2e.py`
- `test_menu.py`

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Cloud- oder Provider-Aufrufe.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.
- Echter Import bleibt nicht freigegeben.

## Final Gate Entscheidung

Der lokale Datenexport-/Import-Review-/Apply-Preview-Block ist final angenommen.

Friday darf lokal exportieren, wenn der harte Token `DATEN EXPORTIEREN` verwendet wird. Friday darf lokale Exportordner read-only pruefen und eine Apply-Vorschau anzeigen.

Friday darf noch keinen echten Import ausfuehren.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Write Plan.

Dieser naechste Schritt sollte weiterhin plan-only bleiben und klaeren, unter welchen Bedingungen ein spaeterer echter Import ueberhaupt sicher waere.
