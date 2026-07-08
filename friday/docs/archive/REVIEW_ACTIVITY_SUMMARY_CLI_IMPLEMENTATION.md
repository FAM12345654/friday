# Review Activity Summary CLI Implementation

## Ziel

Dieser Schritt bindet die lokale Review Activity Summary read-only in den bestehenden Review-Bereich der CLI ein.

Der Review-Bereich kann damit lokale Aktivitaetszahlen anzeigen, ohne Vorschlaege zu veraendern, externe Aktionen auszufuehren oder neue Daten zu speichern.

## Umgesetzte CLI-Anbindung

| Bereich | Umsetzung |
|---|---|
| Review-Menue | Neue Option `6. Review-Aktivitaet anzeigen` |
| Datenquelle | Vorhandene lokale Nachrichten- und Aufgaben-Vorschlaege |
| Anzeige | Statuszaehler und zuletzt geaenderte lokale Vorschlaege |
| Verhalten | Read-only, keine Statusaenderung, keine Freigabe, kein Versand |
| Rueckkehr | Nach der Anzeige bleibt der Review-Loop stabil nutzbar |

## Angezeigte Informationen

- Nachrichten-Vorschlaege: offen, lokal freigegeben, abgelehnt.
- Aufgaben-Vorschlaege: offen, abgelehnt, in Aufgaben umgewandelt.
- Aufgaben-Verknuepfung: Anzahl der konvertierten Vorschlaege mit lokaler `created_task_id`.
- Zuletzt lokal geaenderte Vorschlaege als kurze Leseliste.

## Tests

- `test_combined_review_activity_summary_shows_local_review_counts`
- `test_combined_review_activity_summary_is_read_only`

Die Tests pruefen, dass die neue Review-Option sichtbar ist, lokale Zaehler angezeigt werden und die Anzeige keine Pending-Vorschlaege veraendert.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Keine Schreiboperation im Summary-Flow.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Validierung

Empfohlene Checks nach dieser Aenderung:

```bash
python -m pytest friday/tests/test_interface_combined_review.py friday/tests/test_review_activity_summary.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Summary CLI Readiness Gate.
