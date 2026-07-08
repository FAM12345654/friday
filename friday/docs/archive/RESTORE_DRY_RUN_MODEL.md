# Restore Dry-Run Model

## Ziel

Isoliertes Modell fuer lokale Restore-Pruefungen ohne Restore-Write.

Der Baustein prueft einen Backup-Ordner unter `local_data/backups/`, liest `manifest.json` und meldet Risiken, schreibt aber keine Dateien zurueck.

## Implementierte Bausteine

| Baustein | Zweck |
|---|---|
| `RestoreDryRunSection` | beschreibt eine gepruefte Backup-Sektion |
| `RestoreDryRunResult` | beschreibt das komplette Dry-Run-Ergebnis |
| `build_restore_dry_run(...)` | prueft einen lokalen Backup-Ordner ohne Schreiboperation |

## Gepruefte Regeln

| Fall | Verhalten |
|---|---|
| gueltiger Backup-Ordner | erlaubt Dry-Run |
| Backup fehlt | blockiert |
| Backup liegt ausserhalb `local_data/backups/` | blockiert |
| Manifest fehlt | blockiert |
| Manifest ist ungueltig | blockiert |
| Manifest zeigt auf externen absoluten Pfad | blockiert |
| `.env` im Backup | blockiert |
| Obsidian-Vault-Struktur im Backup | blockiert |
| inkludierte Sektion fehlt | Warnung, kein Write |

## Safety

- Kein Restore.
- Kein Ueberschreiben.
- Kein Kopieren zurueck in das Projekt.
- Kein ZIP.
- Kein Netzwerk.
- Keine Provider.
- Keine Modellaufrufe.
- Keine CLI-Integration.
- Keine Datenbankschema-Aenderung.
- Ergebnis bleibt `preview_only=True`.
- Ergebnis bleibt `persisted=False`.

## Tests

- `friday/tests/test_restore_dry_run.py`

## Empfehlung

Naechster sinnvoller Build Step:

Restore Dry-Run Readiness Gate.
