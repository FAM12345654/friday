# Sensitive Contact Context Guard Save Integration

## Ziel

Integration des Sensitive Contact Context Guard in lokale Contact-Save-Pfade.

## Regel

Kontakt-Kontext-Freitext darf nur gespeichert werden, wenn:

1. Nutzer explizit `SPEICHERN` eingibt.
2. Sensitive Contact Context Guard alle Freitexte erlaubt.

## Geschuetzte Felder

- `relationship_context`
- `notes`, falls vorhanden
- spaetere Kontakt-Kontext-Freitexte

## Blockierverhalten

Wenn der Guard blockiert:

- keine Speicherung
- keine DB-Schreiboperation
- keine teilweise Aktualisierung
- keine externe Aktion
- keine Obsidian-Schreiboperation

## Nutzertext

`Kontakt-Kontext wurde nicht gespeichert, weil ein sensibler Freitext erkannt wurde.`

## Safety

- keine Modellaufrufe
- keine Netzwerkaktionen
- keine externen APIs
- keine automatische Sanitization
- kein Override durch `SPEICHERN`

## Tests

- Save Guard Unit Tests
- Repository Save Tests
- CLI Save Tests, falls vorhanden
- Review Save Tests, falls vorhanden

## Naechster sinnvoller Schritt

Scanner-Hardening oder Guard Integration in Obsidian Write.
