# Review Activity Type Filter Model

## Ziel

Dieser Schritt implementiert ein isoliertes read-only Modell fuer den lokalen Review Activity Type Filter.

Das Modell filtert bereits vorbereitete Review-Detail-Items nach Typ. Es fuehrt keine CLI-Ausgabe, keine Eingabe, keinen DB-Zugriff und keine externen Aktionen aus.

## Neue Modell-Datei

`friday/app/review_activity_type_filter.py`

Enthaltene Elemente:

- `VALID_REVIEW_ACTIVITY_TYPE_FILTERS`
- `INVALID_REVIEW_ACTIVITY_TYPE_FILTER_MESSAGE`
- `ReviewActivityTypeFilterResult`
- `normalize_review_activity_type_filter(...)`
- `build_review_activity_type_filter(...)`

## Erlaubte Filterwerte

| Filter | Bedeutung |
|---|---|
| `all` | Alle lokalen Review-Detail-Eintraege |
| `message` | Nur lokale Nachrichten-Vorschlaege |
| `task` | Nur lokale Aufgaben-Vorschlaege |

## Tests

Neue Testdatei:

`friday/tests/test_review_activity_type_filter.py`

Abgesicherte Faelle:

- Filterwerte werden normalisiert.
- `all` zeigt alle Items.
- `message` zeigt nur Nachrichten-Items.
- `task` zeigt nur Aufgaben-Items.
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

Naechster sinnvoller Build Step: Review Activity Type Filter Model Readiness Gate.
