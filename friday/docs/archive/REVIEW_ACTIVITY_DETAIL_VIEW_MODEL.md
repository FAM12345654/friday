# Review Activity Detail View Model

## Ziel

Dieser Schritt implementiert ein isoliertes read-only Modell fuer die lokale Review Activity Detail View.

Das Modell bereitet vorhandene lokale Nachrichten- und Aufgaben-Vorschlaege als kurze Detail-Liste auf. Es fuehrt keine CLI-Ausgabe, keine Eingabe, keinen DB-Zugriff und keine externen Aktionen aus.

## Neue Modell-Datei

`friday/app/review_activity_detail_view.py`

Enthaltene Strukturen:

- `ReviewActivityDetailItem`
- `ReviewActivityDetailView`
- `build_review_activity_detail_view(...)`

## Modellverhalten

| Bereich | Verhalten |
|---|---|
| Nachrichten-Vorschlaege | Werden als Detail-Items mit Typ, ID, Status, Sender und kurzem Textauszug dargestellt |
| Aufgaben-Vorschlaege | Werden als Detail-Items mit Typ, ID, Status, Titel, kurzem Auszug und optionaler `created_task_id` dargestellt |
| Sortierung | Stabil nach `updated_at` und ID, neuere Eintraege zuerst |
| Textauszug | Lange Texte werden auf einen sicheren kurzen Auszug gekuerzt |
| Fehlende Felder | Werden mit sicheren Fallbacks behandelt |
| Read-only Flags | `preview_only=True`, `persisted=False`, `external_action_used=False` |

## Tests

Neue Testdatei:

`friday/tests/test_review_activity_detail_view.py`

Abgesicherte Faelle:

- Nachrichten-Vorschlaege werden gelistet.
- Aufgaben-Vorschlaege werden gelistet.
- Kombinierte Items werden stabil sortiert.
- Lange Texte werden gekuerzt.
- Fehlende Felder brechen nicht.
- Read-only Safety-Flags bleiben korrekt.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Kein DB-Zugriff.
- Keine Schreiboperation.
- Kein `input()`.
- Kein `print()`.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Validierung

Empfohlene Checks:

```bash
python -m pytest friday/tests/test_review_activity_detail_view.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Detail View Model Readiness Gate.
