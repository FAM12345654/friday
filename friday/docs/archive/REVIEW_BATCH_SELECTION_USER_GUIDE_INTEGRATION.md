# Review Batch Selection User Guide Integration

## Ziel

Dieses Dokument beschreibt die Nutzer-Doku-Ergaenzung fuer die lokale Batch-Auswahl im Review-Bereich.

Der Step ist dokumentationsorientiert:

- keine Produktlogik-Aenderung,
- keine neuen Tests,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Aktualisierte Nutzer-Doku

`README_USER.md` wurde um einen Abschnitt **Batch-Auswahl im Review-Bereich** erweitert.

Der Abschnitt erklaert:

- wo die Batch-Auswahl zu finden ist,
- wie die Auswahl eingegeben wird,
- dass zuerst immer eine Vorschau erscheint,
- welche lokalen Aktionen moeglich sind,
- welche harten Tokens erforderlich sind,
- dass keine echten Nachrichten gesendet werden,
- dass keine echten Kalendertermine erstellt werden.

## Dokumentierte Tokens

| Aktion | Token |
|---|---|
| Nachrichten-Vorschlaege lokal freigeben | `BATCH FREIGEBEN` |
| Vorschlaege lokal ablehnen | `BATCH ABLEHNEN` |
| Aufgaben lokal erstellen | `BATCH AUFGABEN ERSTELLEN` |

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Batch-Apply bleibt durch Preview, Safety Smoke, Guard und harte Tokens geschuetzt.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Validierung

Empfohlene Checks:

```bash
python -m pytest friday/tests/test_interface_combined_review.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Batch Selection Final Acceptance Gate**.

Ziel:

- Parser, Preview, Guard, Apply-Modell, CLI-Integration, User Guide und Tests zusammen final abnehmen,
- keine neue Produktlogik.
