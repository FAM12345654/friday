# Backup / Restore Final Acceptance Gate

## Ziel

Dieses Gate schliesst den lokalen Backup-/Restore-Block ab.

Der Block ist fuer lokale Nutzung freigegeben, solange die dokumentierten Safety-Grenzen gelten:

- Backup Write nur lokal und nur mit `BACKUP ERSTELLEN`.
- Restore Dry-Run ohne Seiteneffekte.
- Restore Copy nur lokal und nur mit `RESTORE AUSFUEHREN`.
- Kein echter In-Place-Restore.

## Abgeschlossene Bereiche

| Bereich | Ergebnis |
|---|---|
| Backup / Restore Plan | vorhanden |
| Backup Preview Model | umgesetzt |
| Backup Preview Readiness Gate | abgeschlossen |
| Backup Write Guard | umgesetzt |
| Backup Write Implementation | umgesetzt |
| Backup Write CLI Approval | umgesetzt |
| Restore Dry-Run Model | umgesetzt |
| Restore Dry-Run Readiness Gate | abgeschlossen |
| Restore Write Guard | umgesetzt |
| Restore Copy Implementation | umgesetzt |
| Restore Copy CLI Approval | umgesetzt |
| Restore Write CLI Readiness Gate | abgeschlossen |
| Backup / Restore Documentation Finalization | abgeschlossen |
| Backup / Restore Runtime Readiness Summary | abgeschlossen |
| Backup / Restore User Guide Integration | abgeschlossen |
| Backup/Restore Forbidden-Path Hardening | umgesetzt |

## Freigegebene lokale Funktionen

- Backup-Vorschau anzeigen.
- Backup lokal unter `local_data/backups/` erstellen.
- Restore-Dry-Run fuer lokalen Backup-Ordner ausfuehren.
- Restore-Kopie lokal unter `local_data/restores/` erstellen.
- Backup-/Restore-Menue in der CLI nutzen.
- Sensible Exportpfade, Symlinks/Junctions und Root-Escapes beim Backup Write ueberspringen.
- Restore Dry-Run bei sensiblen Backup-Inhalten, Symlinks/Junctions oder Root-Escapes blockieren.
- Backup Writer und Restore Writer validieren Quellen erneut gegen lokale Roots.

## Nicht freigegeben

- Kein Restore direkt in aktive Projektdateien.
- Kein Restore direkt nach `friday.db`.
- Kein automatisches Ueberschreiben bestehender Restore-Zielordner.
- Kein Restore aus ZIP-Dateien.
- Kein Cloud-Backup.
- Kein externer Speicherort.
- Kein Backup von `.env.*`, Secrets, Tokens, API-Keys, Credentials, Private Keys, Passwoertern, `.obsidian` oder Obsidian-Vault-Varianten.
- Kein Backup von Symlink-/Junction-Dateien oder Root-Escapes.
- Kein Obsidian-Vault-Restore.
- Kein Netzwerkzugriff.
- Kein Providerzugriff.

## Harter Approval-Stand

| Aktion | Token | Status |
|---|---|---|
| Backup Write | `BACKUP ERSTELLEN` | freigegeben |
| Restore Copy | `RESTORE AUSFUEHREN` | freigegeben |
| In-Place-Restore | kein Token freigegeben | blockiert |

## Teststatus

- Backup-/Restore-Fokus: `64 passed, 4 skipped`
- Full Regression: `930 passed, 4 skipped`
- Compilecheck: erfolgreich
- Safety Smoke: `Overall: PASS`
- `git diff --check`: sauber

## Safety-Bewertung

- Keine externen Aktionen.
- Kein Netzwerk.
- Keine Provider.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine aktive Datenbank wird ersetzt.
- Backup Write ueberspringt sensible Exportpfade, Symlinks/Junctions und Root-Escapes.
- Restore Dry-Run blockiert sensible Backup-Inhalte, Symlinks/Junctions und Root-Escapes.
- Backup Writer und Restore Writer pruefen Quellen erneut vor dem Kopieren.
- Restore Copy bleibt separate lokale Kopie.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Acceptance-Entscheidung

Der lokale Backup-/Restore-Block ist angenommen fuer:

- lokale Backups,
- lokalen Restore-Dry-Run,
- lokale Restore-Kopien,
- CLI-Nutzung mit harten Tokens.

Nicht angenommen ist:

- echter Restore in aktive Projektdateien.

## Empfehlung

Naechster sinnvoller Build Step:

Privacy Dashboard Readiness Plan.
