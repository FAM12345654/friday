# Review Activity Detail View CLI Plan

## Ziel

Dieser Schritt plant die read-only CLI-Anbindung der Review Activity Detail View.

Die geplante CLI-Anzeige soll lokale Review-Eintraege im Review-Bereich sichtbar machen, ohne Vorschlaege zu veraendern, Aufgaben zu erstellen, Dateien zu schreiben oder externe Aktionen auszufuehren.

## Ausgangslage

Vorhanden sind:

- `friday/app/review_activity_detail_view.py`
- `friday/tests/test_review_activity_detail_view.py`
- `REVIEW_ACTIVITY_DETAIL_VIEW_MODEL.md`
- `REVIEW_ACTIVITY_DETAIL_VIEW_MODEL_READINESS_GATE.md`
- bestehende Review Activity Summary im Review-Menue mit Option `6`

Das Detailmodell ist isoliert und read-only freigegeben.

## Geplante CLI-Option

Im Review-Bereich soll eine neue read-only Option ergaenzt werden:

```text
7. Review-Aktivitaet im Detail anzeigen
```

Die bestehende Option `6. Review-Aktivitaet anzeigen` bleibt die kompakte Uebersicht.

## Geplantes Ausgabeformat

```text
Review-Aktivitaet im Detail

Nachrichten-Vorschlaege:
- #1 [pending] Chef: Kannst du morgen den Termin...
- #2 [approved] Team: Termin bestaetigt...

Aufgaben-Vorschlaege:
- #3 [pending] Rechnung pruefen: Bitte lokal pruefen.
- #4 [converted] Unterlagen vorbereiten: Unterlagen... -> Aufgabe 12
```

Bei leerer Aktivitaet:

```text
Keine lokalen Review-Details vorhanden.
```

## Datenquelle

Die CLI soll nur vorhandene lokale Suggestion-Repositories lesen:

- `message_agent.suggestion_repository.get_all_suggestions()`
- `message_agent.task_suggestion_repository.get_all_task_suggestions()`

Falls ein Repository nicht vorhanden ist, soll die Anzeige stabil leer bleiben.

## Geplanter technischer Ablauf

1. Review-Menue zeigt Option `7`.
2. Nutzer waehlt `7`.
3. Interface liest lokale Nachrichten- und Aufgaben-Vorschlaege ueber vorhandene Helper.
4. Interface ruft `build_review_activity_detail_view(...)` auf.
5. Interface gibt kurze, read-only Details aus.
6. Review-Loop bleibt danach aktiv.

## Tests fuer die spaetere Implementierung

Ergaenzen in:

- `friday/tests/test_interface_combined_review.py`

Geplante Tests:

- Review-Menue zeigt `7. Review-Aktivitaet im Detail anzeigen`.
- Detailansicht zeigt lokale Nachrichten- und Aufgaben-Vorschlaege.
- Konvertierte Aufgaben-Vorschlaege zeigen `-> Aufgabe <id>`.
- Leere Detailansicht zeigt eine klare Meldung.
- Detailansicht ist read-only und veraendert keine Pending-Vorschlaege.
- Rueckkehr in den Review-Loop bleibt stabil.

## Nicht-Ziele

- Keine Statusaenderung.
- Keine Freigabe.
- Keine Ablehnung.
- Keine Batch-Aktion.
- Keine Aufgabe erstellen.
- Kein Export.
- Keine Datei-Schreiboperation.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.

## Safety-Bewertung

- Geplante CLI-Anbindung bleibt read-only.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Keine Schreiboperation.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Validierung fuer die spaetere Implementierung

Empfohlene Checks:

```bash
python -m pytest friday/tests/test_interface_combined_review.py friday/tests/test_review_activity_detail_view.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Detail View CLI Implementation.
