# Restore Write Guard Model

## Ziel

Isoliertes Guard-Modell fuer einen spaeteren echten Restore Write.

Der Guard entscheidet nur, ob ein Restore Write theoretisch erlaubt waere. Er schreibt nichts zurueck, kopiert nichts und ueberschreibt keine Dateien.

## Implementierte Bausteine

| Baustein | Zweck |
|---|---|
| `RESTORE_WRITE_APPROVAL_TOKEN` | harter Token `RESTORE AUSFUEHREN` |
| `RestoreWriteGuardResult` | strukturierte Guard-Entscheidung |
| `check_restore_write_allowed(...)` | prueft Dry-Run, Token, Pfade und Konflikte |

## Gepruefte Regeln

| Fall | Verhalten |
|---|---|
| gueltiger Dry-Run + exakter Token | erlaubt theoretisch |
| fehlender Dry-Run | blockiert |
| fehlgeschlagener Dry-Run | blockiert |
| falscher Token | blockiert |
| `JA` / `ja` | blockiert |
| `BACKUP ERSTELLEN` | blockiert |
| Backup ausserhalb `local_data/backups/` | blockiert |
| `.env` / Secrets / Obsidian Vault im Backup | blockiert |
| aktive lokale Datenbank existiert | blockiert |

## Safety

- Kein Restore.
- Kein Restore Write.
- Kein Ueberschreiben.
- Kein Kopieren.
- Kein Loeschen.
- Keine CLI-Integration.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Ergebnis bleibt `preview_only=True`.
- Ergebnis bleibt `persisted=False`.

## Tests

- `friday/tests/test_restore_write_guard.py`

## Empfehlung

Naechster sinnvoller Build Step:

Restore Write Guard Readiness Gate.
