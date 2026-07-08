# Obsidian Guard Integration Plan

## Ziel

Plan fuer die Integration des Sensitive Contact Context Guard vor Obsidian-Write-Pfaden.

## Ausgangslage

Friday besitzt:

- Obsidian Note Preview
- Obsidian Brain Preview
- Obsidian Dry-Run
- Obsidian Write-Gate
- Token `OBSIDIAN SCHREIBEN`
- Sensitive Contact Context Guard
- Scanner Smoke Script

## Zentrale Regel

Ein Obsidian Write darf spaeter nur erfolgen, wenn:

1. `OBSIDIAN_VAULT_PATH` gesetzt ist.
2. `OBSIDIAN_WRITE_ENABLED = True` ist.
3. Nutzer exakt `OBSIDIAN SCHREIBEN` eingibt.
4. Sensitive Guard alle relevanten Freitexte erlaubt.
5. Pfad-Safety den Zielpfad erlaubt.

`OBSIDIAN SCHREIBEN` ueberstimmt den Guard nicht.

## Zu pruefende Inhalte

| Inhalt | Guard |
|---|---|
| `relationship_context` | ja |
| `notes` | ja |
| Obsidian Note Body | ja |
| Obsidian Frontmatter-Freitext | ja |
| Task Contact Snapshot | ja, falls Freitext |
| kontrollierte Kontaktart | nein |
| Dateiname | Pfad-Safety statt Sensitive Guard |

## Blockierverhalten

Wenn der Guard blockiert:

- kein Write
- kein partieller Write
- keine Datei anlegen
- keine Datei aendern
- sichere lokale Fehlermeldung
- keine sensible Passage wiederholen

Meldung:

`Obsidian-Notiz wurde nicht geschrieben, weil ein sensibler Freitext erkannt wurde.`

## Nicht-Ziele

- Keine Implementierung in diesem Step.
- Keine Produktlogik.
- Keine Obsidian-Schreiblogik.
- Keine DB-Migration.
- Keine externen Aktionen.
- Keine Modellaufrufe.

## Spaetere Teststrategie

Ein spaeterer technischer Step sollte pruefen:

- harmlose Kontakt-Notiz darf geschrieben werden, wenn alle Gates erfuellt sind.
- sensible Kontakt-Notiz wird blockiert.
- `OBSIDIAN SCHREIBEN` ueberstimmt den Guard nicht.
- blockierter Write erzeugt keine Datei.
- blockierter Update veraendert keine bestehende Datei.
- Dry-Run bleibt ohne Write.
- Scanner Smoke Script bleibt PASS.

## Empfehlung

Naechster technischer Schritt:

Obsidian Guard Integration in Write Gate.
