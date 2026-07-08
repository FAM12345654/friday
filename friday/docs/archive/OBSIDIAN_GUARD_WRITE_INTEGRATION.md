# Obsidian Guard Write Integration

## Ziel

Integration des Sensitive Contact Context Guard in den Obsidian-Write-Pfad.

## Zentrale Regel

Ein Obsidian Write erfolgt nur, wenn:

1. `OBSIDIAN_VAULT_PATH` gesetzt ist.
2. `OBSIDIAN_WRITE_ENABLED = True` ist.
3. Nutzer exakt `OBSIDIAN SCHREIBEN` eingibt.
4. Sensitive Guard alle relevanten Freitexte erlaubt.
5. Pfad-Safety den Zielpfad erlaubt.

`OBSIDIAN SCHREIBEN` ueberstimmt den Guard nicht.

## Blockierverhalten

Wenn der Guard blockiert:

- kein Write
- kein partieller Write
- keine Datei anlegen
- keine Datei aendern
- sichere lokale Fehlermeldung

Meldung:

`Obsidian-Notiz wurde nicht geschrieben, weil ein sensibler Freitext erkannt wurde.`

## Safety

- keine externen Aktionen
- keine Netzwerkaktionen
- keine Modellaufrufe
- keine DB-Migration
- kein automatischer Obsidian Write
- keine Aenderung an Approval-Tokens

## Tests

- `test_obsidian_guard.py`
- Obsidian Brain / Write-Gate Tests
- Scanner Smoke Script
