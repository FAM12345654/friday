# Review Activity Status Filter Model

## Ziel

Dieser Schritt implementiert ein isoliertes read-only Modell fuer den lokalen Review Activity Status Filter.

Das Modell filtert bereits vorbereitete Review-Detail-Items nach Status. Es fuehrt keine CLI-Ausgabe, keine Eingabe, keinen DB-Zugriff und keine externen Aktionen aus.

## Neue Modell-Datei

`friday/app/review_activity_status_filter.py`

Enthaltene Elemente:

- `VALID_REVIEW_ACTIVITY_STATUS_FILTERS`
- `ReviewActivityStatusFilterResult`
- `normalize_review_activity_status_filter(...)`
- `build_review_activity_status_filter(...)`

## Tests

Neue Testdatei:

`friday/tests/test_review_activity_status_filter.py`

Abgesicherte Faelle:

- Filterwerte werden normalisiert.
- `all` zeigt alle Items.
- `pending` zeigt pending Items.
- `open` zeigt pending und edited Items.
- `converted` zeigt converted Items.
- ungueltige Filter bleiben sicher.
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

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Status Filter Model Readiness Gate.
