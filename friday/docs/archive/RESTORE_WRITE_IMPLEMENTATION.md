# Restore Write Implementation

## Ziel

Guarded local Restore Copy fuer Friday.

Der Restore Write kopiert erlaubte Backup-Sektionen nur in einen separaten Restore-Ordner. Er ersetzt niemals die aktive Friday-Datenbank.

## Implementierte Bausteine

| Baustein | Zweck |
|---|---|
| `RestoreWrittenFile` | beschreibt eine in den Restore-Zielordner kopierte Datei |
| `RestoreWriteResult` | beschreibt das Ergebnis des Restore-Copy-Versuchs |
| `write_local_restore_copy(...)` | schreibt nur unter Restore Write Guard in einen separaten Zielordner |

## Zielordner

Restore Writes landen nur unter:

```text
local_data/restores/friday_restore_<timestamp>/
```

Moegliche Unterordner:

```text
database/
exports/
safety/
RESTORE_MANIFEST.json
README_RESTORE.md
```

## Safety-Regeln

- Restore Write nutzt `check_restore_write_allowed(...)`.
- Token muss exakt `RESTORE AUSFUEHREN` sein.
- Dry-Run muss erlaubt sein.
- Backup muss unter `local_data/backups/` liegen.
- Aktive Datenbankkonflikte blockieren.
- Zielordner darf nicht existieren.
- `.env`, Secrets und Obsidian Vault blockieren.
- Die aktive Datenbank wird nicht ersetzt.

## Nicht enthalten

- Kein Restore in aktive Projektpfade.
- Kein Ersetzen von `friday.db`.
- Kein Restore aus ZIP.
- Kein Obsidian Vault Restore.
- Keine externen Speicherorte.
- Kein Netzwerk.
- Keine Provider.
- Keine CLI-Restore-Write-Anbindung.

## Tests

- `friday/tests/test_restore_writer.py`

## Empfehlung

Naechster sinnvoller Build Step:

Restore Write Readiness Gate.
