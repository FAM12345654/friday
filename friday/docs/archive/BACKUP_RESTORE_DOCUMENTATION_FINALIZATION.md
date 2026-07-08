# Backup / Restore Documentation Finalization

## Ziel

Dieses Dokument fasst den aktuellen lokalen Backup-/Restore-Stand zusammen.

Es trennt bewusst:

- Backup Preview,
- Backup Write,
- Restore Dry-Run,
- Restore Write Guard,
- Restore Copy,
- CLI Approval,
- nicht freigegebenen echten In-Place-Restore.

## Aktueller Stand

| Bereich | Status | Bedeutung |
|---|---|---|
| Backup Preview | umgesetzt | zeigt geplante Backup-Inhalte ohne Write |
| Backup Write Guard | umgesetzt | prueft Token, Zielpfad, Safety Smoke und Ausschluesse |
| Backup Write | umgesetzt | schreibt lokales Backup nur mit `BACKUP ERSTELLEN` |
| Restore Dry-Run | umgesetzt | prueft lokalen Backup-Ordner ohne Zurueckschreiben |
| Restore Write Guard | umgesetzt | prueft Restore-Write-Freigabe ohne Seiteneffekt |
| Restore Copy | umgesetzt | kopiert erlaubte Backup-Inhalte nur in separaten Restore-Ordner |
| Restore Copy im CLI | umgesetzt | nur mit `RESTORE AUSFUEHREN` |
| Echter In-Place-Restore | nicht freigegeben | aktive Projektdateien und aktive DB werden nicht ersetzt |

## Backup-Regeln

- Backup bleibt lokal.
- Backup-Ziel liegt unter `local_data/backups/`.
- Backup Write erfordert exakt `BACKUP ERSTELLEN`.
- Safety Smoke muss erfolgreich sein.
- Secrets, `.env`, Cache-Dateien und externe Vaults werden nicht gesichert.
- Kein Netzwerk und keine Provider werden verwendet.

## Restore-Dry-Run-Regeln

- Restore Dry-Run liest und prueft nur einen lokalen Backup-Ordner.
- Restore Dry-Run schreibt keine Dateien zurueck.
- Restore Dry-Run ersetzt keine aktive Datenbank.
- Restore Dry-Run meldet Blockiergruende und Warnungen.
- Restore Dry-Run ist Voraussetzung fuer Restore Copy.

## Restore-Copy-Regeln

- Restore Copy schreibt nur in `local_data/restores/`.
- Restore Copy erfordert einen erfolgreichen Dry-Run.
- Restore Copy erfordert exakt `RESTORE AUSFUEHREN`.
- Restore Copy ersetzt niemals aktive Projektdateien.
- Restore Copy ersetzt niemals die aktive Friday-Datenbank.
- Bestehende Restore-Zielordner werden nicht ueberschrieben.

## CLI-Zuordnung

```text
Backup / Restore
1. Backup-Vorschau anzeigen
2. Backup lokal erstellen
3. Restore-Dry-Run pruefen
4. Restore-Kopie erstellen
5. Zurueck zum Hauptmenue
```

## Bewusst nicht freigegeben

- Kein Restore direkt nach `friday.db`.
- Kein Restore direkt in aktive Projektordner.
- Kein Restore aus ZIP-Dateien.
- Kein Obsidian-Vault-Restore.
- Kein Cloud-Backup.
- Kein externer Speicherort.
- Kein automatischer Restore ohne hartes Token.
- Kein Restore durch `JA` oder `ja`.

## Relevante Dokumente

- `BACKUP_RESTORE_PLAN.md`
- `BACKUP_PREVIEW_MODEL.md`
- `BACKUP_WRITE_GUARD_MODEL.md`
- `BACKUP_WRITE_IMPLEMENTATION.md`
- `BACKUP_WRITE_CLI_APPROVAL_IMPLEMENTATION.md`
- `RESTORE_DRY_RUN_MODEL.md`
- `RESTORE_WRITE_GUARD_MODEL.md`
- `RESTORE_WRITE_IMPLEMENTATION.md`
- `RESTORE_WRITE_CLI_APPROVAL_IMPLEMENTATION.md`
- `RESTORE_WRITE_CLI_READINESS_GATE.md`

## Testabdeckung

- `test_backup_preview_model.py`
- `test_backup_write_guard.py`
- `test_backup_writer.py`
- `test_restore_dry_run.py`
- `test_restore_write_guard.py`
- `test_restore_writer.py`
- `test_interface_main_menu_e2e.py`
- `test_menu.py`

## Safety-Bewertung

- Keine externen Aktionen.
- Kein Netzwerk.
- Keine Provider.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Aktive Friday-Datenbank bleibt unangetastet.
- Restore Copy bleibt separate lokale Kopie.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Backup / Restore Runtime Readiness Summary.
