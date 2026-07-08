# Local Data Import/Export User Guide Finalization

## Ziel

Dieses Dokument finalisiert die Nutzer-Doku fuer den lokalen Import-/Export-Block von Friday.

Der Stand bleibt bewusst lokal und sicher:

- lokaler Datenexport ist hart gegatet,
- Import-Review ist read-only,
- Import-Apply bleibt nur Vorschau,
- echter Import ist nicht freigegeben.

## Nutzerpfade

| Menuepunkt | Zweck | Schreibt Daten? |
|---|---|---|
| `5. Lokaler Datenexport Vorschau anzeigen` | Export-Zusammenfassungen lokal vorbereiten und bei hartem Token schreiben | Nur mit `DATEN EXPORTIEREN` |
| `6. Lokalen Datenimport pruefen` | Einen Exportordner read-only ueber Manifest und Exportdateien pruefen | Nein |
| `7. Import-Apply-Vorschau anzeigen` | Anzeigen, was ein spaeterer Import theoretisch vorbereiten wuerde | Nein |
| `8. Zurueck zum Hauptmenue` | Backup-/Restore-Bereich verlassen | Nein |

## Harte Tokens

| Token | Bedeutung | Aktueller Status |
|---|---|---|
| `BACKUP ERSTELLEN` | Lokales Backup schreiben | freigegeben |
| `RESTORE AUSFUEHREN` | Restore-Kopie in separaten Zielordner schreiben | freigegeben |
| `DATEN EXPORTIEREN` | Lokalen Datenexport unter `local_data/exports/` schreiben | freigegeben |
| `IMPORT ANWENDEN` | Spaeterer echter Import | nicht freigegeben, wird nicht abgefragt |

## Was freigegeben ist

- Lokaler Datenexport unter `local_data/exports/`.
- Export nur nach Safety Smoke, Guard und hartem Token `DATEN EXPORTIEREN`.
- Read-only Import-Review ueber `manifest.json`.
- Read-only Import-Dry-Run fuer Exportdateien.
- Read-only Import-Apply-Vorschau.
- Anzeige von Status, geplanten Sektionen, Warnungen und Blockiergruenden.

## Was nicht freigegeben ist

- Kein echter Import in aktive Friday-Daten.
- Kein In-Place-Restore in aktive Projektdateien.
- Kein automatisches Ueberschreiben der aktiven SQLite-Datenbank.
- Kein Schreiben aus der Import-Review.
- Kein Schreiben aus der Import-Apply-Vorschau.
- Kein Abfragen des Tokens `IMPORT ANWENDEN`.
- Kein Export von `.env`, Secrets, API-Keys, Obsidian Vault, Cache-Dateien, privaten Roh-Nachrichten oder sensiblen Kontakt-Freitexten.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Cloud- oder Provider-Aufrufe.
- Lokale SQLite-Datenhaltung bleibt unveraendert.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.
- Datenbankschema bleibt unveraendert.

## Verweise

- `LOCAL_DATA_IMPORT_EXPORT_RUNTIME_FINALIZATION_GATE.md`
- `LOCAL_DATA_IMPORT_APPLY_RUNTIME_READINESS_SUMMARY.md`
- `LOCAL_DATA_IMPORT_RUNTIME_READINESS_SUMMARY.md`
- `LOCAL_DATA_EXPORT_RUNTIME_READINESS_SUMMARY.md`
- `README_USER.md`

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import/Export Final Acceptance Gate.
