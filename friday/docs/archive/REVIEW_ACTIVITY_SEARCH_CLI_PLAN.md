# Review Activity Search CLI Plan

## Ziel

Dieser Schritt plant die read-only CLI-Anbindung der Review Activity Search.

Die CLI soll lokale Review-Details nach einem Suchbegriff anzeigen koennen, ohne Vorschlaege zu veraendern, Aufgaben zu erstellen, Dateien zu schreiben oder externe Aktionen auszufuehren.

## Geplanter Menuepunkt

Im bestehenden Review-Bereich soll ein neuer Menuepunkt ergaenzt werden:

`10. Review-Aktivitaet durchsuchen`

Die bestehenden Menuepunkte fuer Summary, Detail View, Statusfilter und Typfilter bleiben unveraendert.

## Geplanter Ablauf

1. Nutzer oeffnet den Review-Bereich.
2. Nutzer waehlt den Such-Menuepunkt.
3. Friday fragt nach einem Suchbegriff.
4. Leere Eingabe oder `z` kehrt ohne Aenderung zur Review-Uebersicht zurueck.
5. Friday baut die vorhandene Review Activity Detail View.
6. Friday sucht read-only in den Detail-Items.
7. Friday zeigt passende lokale Review-Details an.
8. Danach kehrt Friday in die Review-Uebersicht zurueck.

## CLI-Ausgabe

Geplante Ueberschrift:

`Review-Aktivitaet durchsuchen`

Geplante Ergebniszeilen nutzen die bestehende Detail-Item-Ausgabe:

`- #<id> [<status>] <label>: <excerpt>`

Wenn keine passenden Details vorhanden sind:

`Keine lokalen Review-Details fuer diesen Suchbegriff gefunden.`

Wenn der Suchbegriff ungueltig ist:

`Ungueltiger Review-Suchbegriff.`

Zu kurze Suchbegriffe gelten ebenfalls als ungueltig.

## Nicht-Ziele

- Keine fuzzy Suche.
- Keine Volltext-Indexierung.
- Keine Regex- oder Wildcard-Suche.
- Keine Kombination mit Statusfilter.
- Keine Kombination mit Typfilter.
- Keine Statusaenderung.
- Keine Freigabe oder Ablehnung.
- Keine Batch-Aktion.
- Keine Aufgabe erstellen.
- Kein Export.
- Keine Datei-Schreiboperation.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.

## Testplan

CLI-Tests:

- Review-Menue zeigt den neuen Such-Menuepunkt.
- Suche nach Label zeigt passende Items.
- Suche nach Aufgaben-/Nachrichtentext zeigt passende Items.
- Suche ohne Treffer zeigt eine sichere Leermeldung.
- Leere Eingabe oder `z` kehrt ohne Aenderung zurueck.

Modelltests bleiben in:

`friday/tests/test_review_activity_search.py`

CLI-Tests sollen in:

`friday/tests/test_interface_combined_review.py`

## Safety-Bewertung

- CLI-Anbindung bleibt read-only.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Keine Schreiboperation.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Search CLI Implementation.
