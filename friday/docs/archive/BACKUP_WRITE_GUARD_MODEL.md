# Backup Write Guard / Model

## Ziel

Lokales Guard-Modell fuer spaetere Backup Writes.

## Umfang

- prueft Backup Preview
- prueft Zielpfad
- prueft Scanner-Smoke-Status
- prueft harten Token `BACKUP ERSTELLEN`
- prueft ausgeschlossene Sektionen
- schreibt kein Backup
- kopiert keine Dateien
- erzeugt kein ZIP
- kopiert keine DB
- fuehrt keinen Restore aus

## Zentrale Regel

Backup Write ist nur erlaubt, wenn:

1. Backup Preview vorhanden ist.
2. Zielpfad unter `local_data/backups/` liegt.
3. Scanner Smoke Script PASS ist.
4. Nutzer exakt `BACKUP ERSTELLEN` eingibt.
5. Secrets, `.env`, Caches und Obsidian Vault ausgeschlossen bleiben.

`BACKUP ERSTELLEN` ueberstimmt keine Excludes.

## Implementierte Bausteine

- `BACKUP_WRITE_APPROVAL_TOKEN`
- `BackupWriteGuardResult`
- `check_backup_write_allowed`

## Blockiergruende

- `missing_preview`
- `invalid_token`
- `target_outside_backups`
- `scanner_smoke_failed`
- `excluded_section_present`

## Safety

- preview_only=True
- persisted=False
- external_lookup_used=False
- keine Dateioperation
- keine DB-Kopie
- kein ZIP
- kein Restore
- kein Netzwerk
- keine Cloud
- kein Obsidian-Vault-Backup

## Tests

- `test_backup_write_guard.py`

## Empfehlung

Naechster sinnvoller Schritt:

Backup Write Guard Readiness Gate.
