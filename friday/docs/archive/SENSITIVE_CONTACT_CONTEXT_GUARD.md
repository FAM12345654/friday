# Sensitive Contact Context Guard

## Ziel

Lokaler deterministischer Guard fuer Kontakt-Kontext-Freitexte.

## Umfang

- prueft Kontakt-Kontext-Freitext
- blockiert sensible Kategorien
- nutzt keine Modelle
- nutzt keine externen Dienste
- schreibt keine Daten
- veraendert keine Kontakte automatisch

## Blockierte Kategorien

- Politik
- Religion
- Ethnie / Herkunft
- Gesundheit
- sexuelle Orientierung / Sexleben
- Gewerkschaftszugehoerigkeit
- strafrechtliche Details
- private Finanzdetails
- intime/private Profile

## Erlaubte Beispiele

- Projekt Alpha
- Kollege aus Buchhaltung
- Dienstleister fuer Heizung
- Kunde fuer Angebot

## Implementierte Bausteine

- SensitiveContactContextGuardResult
- normalize_sensitive_guard_text
- check_sensitive_contact_context

## Safety

- preview_only=True
- persisted=False
- external_lookup_used=False
- keine DB-Schreiboperation
- keine externen Aktionen
- keine Modellaufrufe
- keine Obsidian-Schreiboperation

## Tests

- test_sensitive_contact_context_guard.py

## Empfehlung

Der Guard sollte spaeter vor Kontakt-Speicherung, Obsidian-Write und Review-Contact-Save verwendet werden.
