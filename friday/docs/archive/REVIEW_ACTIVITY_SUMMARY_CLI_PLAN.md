# Review Activity Summary CLI Plan

## Ziel

Dieser Plan beschreibt die spaetere read-only CLI-Anbindung der Review Activity Summary.

Dieser Step bleibt bewusst Planung:

- keine Produktlogik-Aenderung,
- keine CLI-Implementierung,
- keine neuen Tests,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Bestehender Stand

Bereits vorhanden:

| Baustein | Status |
|---|---|
| `friday/app/review_activity_summary.py` | isoliertes read-only Summary-Modell |
| `friday/tests/test_review_activity_summary.py` | Fokus-Tests |
| `REVIEW_ACTIVITY_SUMMARY_MODEL_READINESS_GATE.md` | Modell-Gate abgeschlossen |

Noch nicht vorhanden:

- Review-Menuepunkt fuer Aktivitaetsuebersicht,
- CLI-Renderer fuer Summary-Daten,
- E2E-Test fuer Anzeige und Rueckkehr.

## Geplanter CLI-Ort

Die Review Activity Summary soll im bestehenden Review-Bereich angezeigt werden:

```text
Hauptmenue -> 6. Vorschlaege pruefen / freigeben
```

Geplante Menue-Erweiterung:

```text
6. Review-Aktivitaet anzeigen
```

Der vorhandene Bereich `5. Batch-Auswahl als Vorschau anzeigen` bleibt unveraendert.

## Geplanter Ablauf

1. Nutzer oeffnet `Vorschlaege pruefen / freigeben`.
2. Friday zeigt die bestehende Review-Uebersicht.
3. Nutzer waehlt Bereich `6`.
4. Friday laedt lokale Nachrichten- und Aufgaben-Vorschlaege ueber bestehende Repositories/Agenten.
5. Friday baut daraus eine `ReviewActivitySummary`.
6. Friday zeigt die Summary read-only an.
7. Danach kehrt Friday in die Review-Uebersicht zurueck.

## Geplante Anzeige

Beispiel:

```text
Review-Aktivitaet

Nachrichten-Vorschlaege:
- Offen: 2
- Lokal freigegeben: 3
- Abgelehnt: 1

Aufgaben-Vorschlaege:
- Offen: 1
- Abgelehnt: 0
- In Aufgaben umgewandelt: 4
- Mit lokaler Aufgabe verknuepft: 4

Zuletzt lokal geaendert:
- Nachricht-Vorschlag 12: approved
- Aufgaben-Vorschlag 7: converted -> Aufgabe 14
```

## Ruecksprungverhalten

- Die Summary fragt keinen Token ab.
- Die Summary hat keine eigene Aktion.
- Nach Anzeige bleibt der Review-Loop stabil.
- `Enter` oder `z` in der Review-Uebersicht fuehrt weiterhin zurueck zum Hauptmenue.

## Nicht-Ziele

- Keine Batch-Aktion.
- Keine Statusaenderung.
- Keine Aufgabe erstellen.
- Keine Nachricht senden.
- Keine Kalenderaktion.
- Kein Export.
- Kein Undo.
- Keine Datenbankschema-Aenderung.
- Keine externen Dienste.

## Geplante Tests fuer Implementierung

Fokus-Tests:

```bash
python -m pytest friday/tests/test_interface_combined_review.py
python -m pytest friday/tests/test_review_activity_summary.py
```

Testfaelle:

- Review-Uebersicht zeigt neuen Bereich `6. Review-Aktivitaet anzeigen`.
- Bereich `6` zeigt Nachrichten- und Aufgaben-Zahlen.
- Anzeige bleibt read-only, Vorschlaege bleiben unveraendert.
- Nach Anzeige kehrt der Review-Loop stabil zur Uebersicht zurueck.
- Ungueltige Eingaben bleiben unveraendert stabil.

Full Checks:

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Safety-Bewertung

- Geplante CLI-Anbindung bleibt read-only.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine harten Tokens noetig, weil nichts geschrieben wird.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Activity Summary CLI Implementation**.

Ziel:

- read-only Anzeige im Review-Bereich implementieren,
- vorhandenes Summary-Modell verwenden,
- Tests fuer Anzeige und Rueckkehr ergaenzen,
- keine Schreiboperation.
