# Review Activity Search Model

## Ziel

Dieser Schritt implementiert ein isoliertes read-only Modell fuer die lokale Review Activity Search.

Das Modell sucht in bereits vorbereiteten Review-Detail-Items nach einem Suchbegriff. Es fuehrt keine CLI-Ausgabe, keine Eingabe, keinen DB-Zugriff und keine externen Aktionen aus.

## Neue Modell-Datei

`friday/app/review_activity_search.py`

Enthaltene Elemente:

- `INVALID_REVIEW_ACTIVITY_SEARCH_QUERY_MESSAGE`
- `DEFAULT_REVIEW_ACTIVITY_SEARCH_MIN_QUERY_LENGTH`
- `DEFAULT_REVIEW_ACTIVITY_SEARCH_RESULT_LIMIT`
- `ReviewActivitySearchResult`
- `normalize_review_activity_search_query(...)`
- `build_review_activity_search(...)`

## Suchfelder

Die Suche nutzt nur vorhandene lokale Detail-Item-Felder:

- `suggestion_type`
- `suggestion_id`
- `status`
- `primary_label`
- `excerpt`
- `created_task_id`

## Verhalten

- Suchbegriffe werden normalisiert.
- Leere oder zu kurze Suchbegriffe sind ungueltig.
- Treffer bleiben in der vorhandenen Reihenfolge.
- Nicht gefundene Suchbegriffe liefern eine gueltige leere Trefferliste.
- Treffer werden auf ein sicheres Limit begrenzt.
- Regex-artige Suchbegriffe werden literal behandelt.
- Das Modell bleibt read-only.

## Tests

Neue Testdatei:

`friday/tests/test_review_activity_search.py`

Abgesicherte Faelle:

- Suchbegriffe werden normalisiert.
- Suche findet Treffer im Label.
- Suche findet Treffer im Excerpt.
- Suche findet Treffer nach Status und Typ.
- Suche findet Treffer nach lokalen IDs.
- leere oder zu kurze Suchbegriffe bleiben sicher.
- Suche ohne Treffer bleibt gueltig und leer.
- Trefferlimitierung bleibt sichtbar.
- Regex-artige Suchbegriffe werden literal behandelt.
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

Naechster sinnvoller Build Step: Review Activity Search Model Readiness Gate.
