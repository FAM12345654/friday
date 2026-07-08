# Restore Dry-Run Plan

## Ziel

Plan fuer einen spaeteren lokalen Restore-Dry-Run.

Der Dry-Run soll ein vorhandenes lokales Backup pruefen, aber keine Dateien zurueckschreiben, keine Datenbank ersetzen und keine bestehenden Daten veraendern.

## Umfang

Der Restore-Dry-Run darf spaeter:

- Backup-Ordner unter `local_data/backups/` pruefen.
- `manifest.json` lesen.
- erwartete Backup-Sektionen erkennen.
- fehlende oder unerwartete Dateien melden.
- Restore-Risiken als Text ausgeben.
- eine Restore-Vorschau erzeugen.

Der Restore-Dry-Run darf nicht:

- Dateien ueberschreiben.
- Datenbankdateien ersetzen.
- Exporte zurueckkopieren.
- Obsidian Vault schreiben.
- Secrets oder `.env` importieren.
- externe Speicherorte lesen.
- Netzwerkaktionen ausloesen.
- echte Restore-Aktionen ausfuehren.

## Geplantes Modell

### RestoreDryRunResult

Geplante Felder:

- `allowed`
- `backup_root`
- `manifest_found`
- `manifest_valid`
- `sections_checked`
- `missing_sections`
- `blocked_reasons`
- `warnings`
- `message`
- `preview_only`
- `persisted`
- `external_lookup_used`

### RestoreDryRunSection

Geplante Felder:

- `name`
- `status`
- `path`
- `file_count`
- `message`

## Geplante Pruefregeln

| Regel | Verhalten |
|---|---|
| Backup-Pfad fehlt | blockieren |
| Backup-Pfad liegt nicht unter `local_data/backups/` | blockieren |
| `manifest.json` fehlt | blockieren |
| Manifest ist kein gueltiges JSON | blockieren |
| Manifest enthaelt unerwartete externe Pfade | blockieren |
| `.env` oder Secrets im Backup | blockieren |
| Obsidian Vault im Backup | blockieren |
| erwartete Sektion fehlt | warnen oder blockieren, je nach Sektion |
| Backup sieht gueltig aus | Dry-Run-Ergebnis anzeigen, aber nichts schreiben |

## Geplante erlaubte Lesepfade

| Pfad | Status |
|---|---|
| `manifest.json` | lesen erlaubt |
| `README_BACKUP.md` | lesen erlaubt |
| `database/` | nur pruefen, nicht zurueckschreiben |
| `exports/` | nur pruefen, nicht zurueckschreiben |
| `safety/` | nur pruefen, nicht zurueckschreiben |

## Geplante verbotene Aktionen

- Kein Restore Write.
- Kein Ueberschreiben der aktiven `friday.db`.
- Kein Schreiben in `local_data/exports`.
- Kein Schreiben in Obsidian Vaults.
- Kein Lesen ausserhalb erlaubter lokaler Backup-Pfade.
- Kein Entpacken externer Archive.
- Kein Netzwerk.
- Keine Provider.
- Keine Modellaufrufe.

## Token-Policy

Fuer den Dry-Run selbst ist kein harter Write-Token geplant, weil nichts geschrieben werden darf.

Ein spaeterer echter Restore duerfte nur mit eigenem harten Token geplant werden, zum Beispiel:

`RESTORE PRUEFEN` fuer eine Pruefung mit erweiterten Warnungen.

Ein echter Restore-Write bleibt in diesem Plan nicht freigegeben.

## Teststrategie fuer spaetere Umsetzung

Geplante Tests:

- gueltiger Backup-Ordner erzeugt Dry-Run-Ergebnis.
- fehlendes Manifest blockiert.
- ungueltiges Manifest blockiert.
- Pfad ausserhalb `local_data/backups/` blockiert.
- `.env` im Backup blockiert.
- Obsidian-Vault-Struktur im Backup blockiert.
- Dry-Run schreibt keine Dateien.
- Ergebnis bleibt `preview_only=True`.
- Ergebnis bleibt `persisted=False`.
- keine externen Aktionen.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Implementierung gebaut.
- Keine Tests geaendert.
- Kein Restore ausgefuehrt.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine Netzwerkaktionen.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Restore Dry-Run Model.
