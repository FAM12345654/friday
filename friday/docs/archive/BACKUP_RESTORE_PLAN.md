# Backup / Restore Plan

## Ziel

Plan fuer lokale Backups und spaetere Restore-Dry-Runs in Friday.

## Ausgangslage

Friday besitzt lokale Datenbereiche fuer:

- Contact Context
- Tasks
- Review
- Exporte
- Safety-/Architektur-Doku
- Obsidian Brain Preview / Write-Gate

## Backup-Prinzip

Backups bleiben lokal.

Kein Cloud-Upload.
Kein Netzwerk.
Keine externen Provider.
Keine Secrets.

## Geplante Backup-Bereiche

| Bereich | Status | Hinweis |
|---|---|---|
| SQLite-Datenbank | geplant | lokale Daten |
| lokale Exporte | geplant | `local_data/exports` |
| Safety-Doku | geplant | Matrix, Architektur, Testmatrix |
| Obsidian Vault | nicht automatisch | eigenes Gate noetig |
| `.env` / Secrets | ausgeschlossen | nie unredacted sichern |
| `.venv` / Caches | ausgeschlossen | nicht noetig |

## Geplante Backup-Struktur

```text
local_data/backups/friday_backup_<YYYYMMDD_HHMMSS>/
├── manifest.json
├── database/
├── exports/
├── safety/
└── README_BACKUP.md
```

## Geplantes Manifest

```json
{
  "friday_backup_version": 1,
  "backup_created_at": "YYYY-MM-DDTHH:MM:SS",
  "included_sections": [],
  "excluded_sections": [],
  "preview_only": false,
  "external_lookup_used": false
}
```

## Backup-Gates

Spaeterer Write nur wenn:

1. Backup Preview erstellt wurde.
2. Zielpfad unter `local_data/backups` liegt.
3. Keine Secrets enthalten sind.
4. Nutzer explizit freigibt.
5. Scanner Smoke Script PASS bleibt.

Moeglicher harter Token:

`BACKUP ERSTELLEN`

## Restore-Gates

Spaeterer Restore nur wenn:

1. Manifest gueltig ist.
2. Restore Dry-Run erfolgreich ist.
3. Keine unbekannten Pfade enthalten sind.
4. Keine Safety-Flags riskant veraendert werden.
5. Nutzer explizit freigibt.

Moeglicher harter Token:

`RESTORE AUSFÜHREN`

## Nicht-Ziele

- Keine Implementierung in diesem Step.
- Kein Backup Write.
- Kein Restore.
- Kein ZIP.
- Kein Cloud-Speicher.
- Kein Netzwerk.
- Keine externen Provider.

## Spaetere Teststrategie

- Backup Preview listet erwartete Dateien.
- Secrets werden ausgeschlossen.
- Backup Write schreibt nur unter `local_data/backups`.
- Restore Dry-Run erkennt ungueltiges Manifest.
- Restore blockiert Pfade ausserhalb des Projekts.
- Restore blockiert riskante Safety-Flag-Aenderungen.
- Scanner Smoke Script bleibt PASS.

## Empfehlung

Naechster technischer Schritt:

Backup Preview Model.
