# Friday Local Product Phase 3 Write Flow Hardening Gate

## Ziel

Dieses Gate dokumentiert die lokale Haertung bestehender Write-Flows nach dem MVP-GO.

Schwerpunkt:

- Backup Rotation mit Preview, Guard, Writer und CLI-Anbindung,
- Forget Person Audit als Dokumentation der Loeschpfade,
- Obsidian Write UX und Restore Write UX als Klarheits-Review ohne Token- oder Gate-Aenderung.

## Backup Rotation

Neue lokale Bausteine:

| Datei | Zweck |
|---|---|
| `friday/app/backup_rotation_preview.py` | Read-only Vorschau alter Backup-Ordner |
| `friday/app/backup_rotation_guard.py` | Guard mit Safety Smoke und Token `BACKUP AUFRAEUMEN` |
| `friday/app/backup_rotation_writer.py` | Guarded Writer zum Loeschen alter Backup-Ordner |
| `friday/tests/test_backup_rotation.py` | Unit-Tests fuer Preview, Guard und Writer |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Test fuer Backup-Rotation |

CLI-Pfad:

```text
Hauptmenue -> Backup / Restore -> Backups aufraeumen
```

Sicherheitsregeln:

- Der neueste Backup-Ordner wird geschuetzt.
- Alte Backup-Ordner werden nur nach Vorschau ausgewaehlt.
- Safety Smoke muss PASS sein.
- Exakter Token: `BACKUP AUFRAEUMEN`.
- `JA`, `ja`, Enter oder falsche Tokens reichen nicht.
- Keine externen Aktionen.

## Forget Person Audit

Der bestehende Forget-Person-Flow bleibt unveraendert:

- Preview vor Write,
- vorhandenes lokales Backup erforderlich,
- Safety Smoke PASS erforderlich,
- Guard erforderlich,
- harter Token `PERSON VERGESSEN`,
- keine Obsidian-Dateien,
- keine Aufgaben-, Nachrichten- oder Kalenderloeschung.

## Obsidian Write UX

Der bestehende Obsidian-Write-Flow bleibt unveraendert:

- Preview/Dry-Run zuerst,
- Vault-Write nur nach Guard,
- Sensitive Guard vor Write,
- harter Token `OBSIDIAN SCHREIBEN`,
- keine Batch-Writes,
- keine externen Aktionen.

## Restore Write UX

Der bestehende Restore-Copy-Flow bleibt unveraendert:

- Restore-Dry-Run vor Write,
- Restore nur als separate Kopie unter `local_data/restores/`,
- aktive Datenbank wird nicht ersetzt,
- harter Token `RESTORE AUSFUEHREN`,
- kein In-Place-Restore.

## Validierungsstand

| Check | Ergebnis |
|---|---|
| Full Regression | `1013 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Diff Check | sauber |

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Safety-Flag-Aenderung.
- Keine bestehenden Token umbenannt oder abgeschwaecht.
- Keine Datenbankschema-Aenderung.

## Ergebnis

Phase 3 ist lokal umgesetzt: Backup Rotation ist guard-basiert im CLI verfuegbar, waehrend Forget Person, Obsidian Write und Restore Write ihre bestehenden harten Gates behalten.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Phase 4 Local AI kontrolliert.
