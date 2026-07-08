# Review Batch Selection CLI Apply Plan

## Ziel

Dieser Plan beschreibt, wie das bestehende guarded Review-Batch-Apply-Modell spaeter sicher im lokalen CLI-Review-Flow angebunden werden soll.

Dieser Step ist bewusst nur Planung:

- keine CLI-Implementierung,
- keine Produktlogik-Aenderung,
- keine neuen Tests,
- keine externen Aktionen,
- keine Datenbankschema-Aenderung.

## Bestehender Stand

Bereits vorhanden:

| Baustein | Status |
|---|---|
| `review_batch_selection_parser.py` | isolierter Parser fuer Batch-Auswahlen vorhanden |
| `review_batch_selection_preview.py` | read-only Preview-Renderer vorhanden |
| `review_batch_apply_guard.py` | Guard-Modell fuer erlaubte lokale Batch-Aktionen vorhanden |
| `review_batch_apply_model.py` | guarded lokales Apply-Modell vorhanden |
| `REVIEW_BATCH_SELECTION_APPLY_MODEL_READINESS_GATE.md` | Apply-Modell als isolierter lokaler Baustein abgenommen |

Noch nicht freigegeben:

- keine CLI-Apply-Option,
- keine Batch-Ausfuehrung im Review-Menue,
- keine externen Aktionen,
- keine Auto-Approvals.

## Geplanter CLI-Flow

Der spaetere CLI-Flow soll nur im bestehenden Review-Bereich sichtbar werden.

Geplanter Ablauf:

1. Nutzer oeffnet Review im Hauptmenue.
2. Nutzer waehlt Nachrichten- oder Aufgaben-Vorschlaege.
3. Friday zeigt offene Vorschlaege mit stabilen virtuellen IDs.
4. Nutzer kann eine Batch-Auswahl eingeben, zum Beispiel:
   - `1,2,3`
   - `all`
   - `none`
   - `z`
5. Friday zeigt zuerst nur eine Preview der Auswahl.
6. Nutzer waehlt eine erlaubte lokale Aktion.
7. Friday fuehrt den Apply-Guard aus.
8. Friday verlangt vor jeder lokalen Aenderung einen harten Token.
9. Nur bei exakt passendem Token wird das lokale Apply-Modell aufgerufen.
10. Danach zeigt Friday eine kurze Ergebnis-Zusammenfassung und kehrt stabil in den Review-Flow zurueck.

## Geplante erlaubte Aktionen

| Aktion | Scope | Harter Token | Lokaler Effekt |
|---|---|---|---|
| Nachrichten-Vorschlaege lokal freigeben | nur Nachrichten-Vorschlaege | `BATCH FREIGEBEN` | Status lokal auf `approved`, kein Versand |
| Vorschlaege lokal ablehnen | Nachrichten- und Aufgaben-Vorschlaege | `BATCH ABLEHNEN` | Status lokal auf `rejected` |
| Aufgaben lokal erstellen | nur Aufgaben-Vorschlaege | `BATCH AUFGABEN ERSTELLEN` | lokale Aufgaben erstellen und Vorschlaege auf `converted` setzen |

Nicht erlaubt:

- echte Nachricht senden,
- echten Kalendertermin erstellen,
- externe Provider aufrufen,
- gemischte Aktion ohne Guard-Freigabe anwenden,
- Apply ohne Preview,
- Apply ohne harten Token.

## Guard-Reihenfolge

Vor jeder lokalen Aenderung muss die Reihenfolge stabil bleiben:

1. Aktuelle sichtbare Items neu erfassen.
2. Batch-Auswahl parsen.
3. Preview anzeigen.
4. Action Type bestimmen.
5. Apply Guard ausfuehren.
6. Harten Token abfragen.
7. Apply-Modell ausfuehren.
8. Ergebnis anzeigen.

Wenn einer dieser Schritte blockiert, wird nichts lokal geaendert.

## Fehler- und Abbruchfaelle

Der spaetere CLI-Step muss folgende Faelle testen:

- leere Auswahl bleibt ohne Apply,
- `none` fuehrt keine Aktion aus,
- `z` kehrt zurueck,
- ungueltige IDs blockieren,
- stale Preview blockiert,
- falscher harter Token blockiert,
- falscher Suggestion-Typ blockiert,
- bereits konvertierte Aufgaben-Vorschlaege erzeugen keine Duplikate,
- fehlender `TaskAgent` blockiert Task-Erstellung,
- Review-Loop bleibt nach Blockierung stabil.

## Testplan fuer die spaetere Implementierung

Fokus-Tests fuer den spaeteren Implementierungs-Step:

```bash
python -m pytest friday/tests/test_interface_combined_review.py
python -m pytest friday/tests/test_review_batch_selection_parser.py friday/tests/test_review_batch_selection_preview.py
python -m pytest friday/tests/test_review_batch_apply_guard.py friday/tests/test_review_batch_apply_model.py
```

Full Checks:

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Safety-Bewertung

- Keine Produktlogik in diesem Plan-Step geaendert.
- Keine CLI-Aktion in diesem Plan-Step eingebaut.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Batch Selection CLI Apply Implementation**.

Ziel:

- geplanten CLI-Apply-Pfad lokal implementieren,
- harte Tokens erzwingen,
- Guard und Apply-Modell wiederverwenden,
- Fokus-Tests fuer positive und blockierte CLI-Pfade ergaenzen,
- weiterhin keine externen Aktionen.
