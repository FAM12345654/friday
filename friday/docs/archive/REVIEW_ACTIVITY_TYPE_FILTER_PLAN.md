# Review Activity Type Filter Plan

## Ziel

Dieser Schritt plant einen lokalen read-only Typfilter fuer Review-Aktivitaet in Friday.

Der Filter soll vorhandene lokale Review-Detail-Eintraege nach Typ anzeigen, ohne Vorschlaege zu veraendern, Aufgaben zu erstellen, Dateien zu schreiben oder externe Aktionen auszufuehren.

## Erlaubte Filterwerte

| Filter | Bedeutung |
|---|---|
| `all` | Alle lokalen Review-Detail-Eintraege |
| `message` | Nur lokale Nachrichten-Vorschlaege |
| `task` | Nur lokale Aufgaben-Vorschlaege |

## Verhalten

- `all` gibt alle vorhandenen Detail-Items in vorhandener Reihenfolge zurueck.
- `message` gibt nur Items mit `suggestion_type == "message"` zurueck.
- `task` gibt nur Items mit `suggestion_type == "task"` zurueck.
- Leere oder unbekannte Filterwerte sind ungueltig und liefern keine Items.
- Der Filter normalisiert Eingaben per `strip().lower()`.

## Modell-Scope

Der erste technische Schritt soll nur ein isoliertes Modell enthalten:

- keine CLI-Ausgabe,
- kein `input()`,
- kein `print()`,
- kein DB-Zugriff,
- keine Repository-Nutzung,
- keine Schreiboperation.

## Spaetere CLI-Anbindung

Die spaetere CLI-Anbindung soll im bestehenden Review-Bereich erfolgen.

Geplanter Ablauf:

1. Nutzer waehlt Review-Aktivitaet nach Typ filtern.
2. Friday fragt nach einem Typfilter.
3. Friday baut die vorhandene Review Activity Detail View.
4. Friday filtert read-only nach Typ.
5. Friday zeigt passende lokale Review-Details an.
6. Danach kehrt Friday in die Review-Uebersicht zurueck.

## Nicht-Ziele

- Keine Statusaenderung.
- Keine Freigabe oder Ablehnung.
- Keine Batch-Aktion.
- Keine Aufgabe erstellen.
- Kein Export.
- Keine Datei-Schreiboperation.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine Kombination mit Statusfilter in diesem Schritt.

## Testplan

Modelltests:

- Filterwerte werden normalisiert.
- `all` zeigt alle Items.
- `message` zeigt nur Nachrichten-Items.
- `task` zeigt nur Aufgaben-Items.
- ungueltige Filter bleiben sicher.
- Read-only Safety-Flags bleiben korrekt.

Spaetere CLI-Tests:

- CLI zeigt Nachrichten-Items fuer `message`.
- CLI zeigt Aufgaben-Items fuer `task`.
- CLI meldet ungueltige Filterwerte sicher.
- Leer oder `z` kehrt ohne Aenderung zurueck.

## Safety-Bewertung

- Planung bleibt local-only.
- Geplanter Filter bleibt read-only.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Type Filter Model.
