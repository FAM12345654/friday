# Review Activity Type Filter CLI Plan

## Ziel

Dieser Schritt plant die read-only CLI-Anbindung des Review Activity Type Filters.

Die CLI soll lokale Review-Details nach Typ anzeigen koennen, ohne Vorschlaege zu veraendern, Aufgaben zu erstellen, Dateien zu schreiben oder externe Aktionen auszufuehren.

## Geplanter Menuepunkt

Im bestehenden Review-Bereich soll ein neuer Menuepunkt ergaenzt werden:

`9. Review-Aktivitaet nach Typ filtern`

Der bestehende Statusfilter bleibt unveraendert.

## Geplanter Ablauf

1. Nutzer oeffnet den Review-Bereich.
2. Nutzer waehlt den Typfilter-Menuepunkt.
3. Friday fragt nach einem Typfilter.
4. Erlaubte Eingaben: `all`, `message`, `task`.
5. Leere Eingabe oder `z` kehrt ohne Aenderung zur Review-Uebersicht zurueck.
6. Friday baut die vorhandene Review Activity Detail View.
7. Friday filtert die Detail-Items read-only nach Typ.
8. Friday zeigt passende lokale Review-Details an.
9. Danach kehrt Friday in die Review-Uebersicht zurueck.

## CLI-Ausgabe

Geplante Ueberschrift:

`Review-Aktivitaet nach Typ`

Geplante Ergebniszeilen nutzen die bestehende Detail-Item-Ausgabe:

`- #<id> [<status>] <label>: <excerpt>`

Wenn keine passenden Details vorhanden sind:

`Keine lokalen Review-Details fuer diesen Typ gefunden.`

Wenn der Filter ungueltig ist:

`Ungueltiger Review-Typfilter.`

## Nicht-Ziele

- Keine Kombination mit Statusfilter.
- Keine Suche.
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

- Review-Menue zeigt den neuen Typfilter-Menuepunkt.
- Auswahl `9` mit `message` zeigt nur Nachrichten-Items.
- Auswahl `9` mit `task` zeigt nur Aufgaben-Items.
- Ungueltiger Filter zeigt eine sichere Fehlermeldung.
- Leere Eingabe oder `z` kehrt ohne Aenderung zurueck.

Modelltests bleiben in:

`friday/tests/test_review_activity_type_filter.py`

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

Naechster sinnvoller Build Step: Review Activity Type Filter CLI Implementation.
