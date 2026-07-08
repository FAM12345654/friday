# Review Activity Detail View CLI Implementation

## Ziel

Dieser Schritt bindet die lokale Review Activity Detail View read-only in den bestehenden Review-Bereich der CLI ein.

Die Detailansicht zeigt lokale Nachrichten- und Aufgaben-Vorschlaege als kurze Liste, ohne Vorschlaege zu veraendern, Aufgaben zu erstellen, Dateien zu schreiben oder externe Aktionen auszufuehren.

## Umgesetzte CLI-Anbindung

| Bereich | Umsetzung |
|---|---|
| Review-Menue | Neue Option `7. Review-Aktivitaet im Detail anzeigen` |
| Datenquelle | Vorhandene lokale Nachrichten- und Aufgaben-Vorschlaege |
| Modell | `build_review_activity_detail_view(...)` |
| Anzeige | Nachrichten- und Aufgaben-Vorschlaege mit ID, Status, Label, kurzem Auszug und optionaler Aufgaben-ID |
| Verhalten | Read-only, keine Statusaenderung, keine Freigabe, keine Ablehnung |
| Rueckkehr | Review-Loop bleibt nach der Anzeige stabil nutzbar |

## Angezeigte Informationen

- Nachrichten-Vorschlaege mit lokaler ID, Status, Absender/Fallback und kurzem Textauszug.
- Aufgaben-Vorschlaege mit lokaler ID, Status, Titel/Fallback und kurzem Auszug.
- Konvertierte Aufgaben-Vorschlaege mit lokaler `created_task_id`.
- Leere Bereiche mit klarer Meldung.

## Tests

Ergaenzte Tests in `friday/tests/test_interface_combined_review.py`:

- `test_combined_review_activity_detail_view_shows_local_review_items`
- `test_combined_review_activity_detail_view_is_read_only`

Die Tests pruefen, dass die neue Review-Option sichtbar ist, lokale Details angezeigt werden und die Anzeige keine Pending-Vorschlaege veraendert.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Keine Schreiboperation im Detail-Flow.
- Keine Statusaenderung im Detail-Flow.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Validierung

Empfohlene Checks:

```bash
python -m pytest friday/tests/test_interface_combined_review.py friday/tests/test_review_activity_detail_view.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Detail View CLI Readiness Gate.
