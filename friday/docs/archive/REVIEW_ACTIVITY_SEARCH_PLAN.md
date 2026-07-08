# Review Activity Search Plan

## Ziel

Dieser Schritt plant eine lokale read-only Suche fuer Review-Aktivitaet in Friday.

Die Suche soll vorhandene lokale Review-Detail-Eintraege nach einem Suchbegriff anzeigen, ohne Vorschlaege zu veraendern, Aufgaben zu erstellen, Dateien zu schreiben oder externe Aktionen auszufuehren.

## Ausgangslage

Friday hat bereits:

- Review Activity Summary,
- Review Activity Detail View,
- Review Activity Status Filter,
- Review Activity Type Filter.

Damit sind lokale Review-Eintraege sichtbar und filterbar. Eine Suche ist der naechste kleine Nutzbarkeitsgewinn, damit einzelne Vorschlaege schneller gefunden werden koennen.

## Geplanter Suchumfang

Die Suche soll nur vorhandene `ReviewActivityDetailItem`-Felder auswerten:

| Feld | Zweck |
|---|---|
| `suggestion_type` | Suche nach `message` oder `task` |
| `suggestion_id` | Suche nach sichtbarer lokaler ID |
| `status` | Suche nach Status wie `pending`, `approved`, `converted` |
| `primary_label` | Suche nach Absender oder Aufgabentitel |
| `excerpt` | Suche im lokalen Vorschautext |
| `created_task_id` | Suche nach verknuepfter lokaler Aufgaben-ID |

## Verhalten

- Suchbegriffe werden per `strip().lower()` normalisiert.
- Mehrfache Leerzeichen werden auf ein Leerzeichen reduziert.
- Leere oder zu kurze Suchbegriffe sind ungueltig und liefern keine Items.
- Treffer bleiben in der vorhandenen Reihenfolge der Detail View.
- Die Suche ist eine einfache lokale Teilstring-Suche.
- Die Suche ist literal: keine Regex, keine Wildcards, keine semantische Suche.
- Ergebnisse werden begrenzt, damit breite Trefferlisten uebersichtlich bleiben.

## Modell-Scope

Der erste technische Schritt soll nur ein isoliertes Modell enthalten:

- keine CLI-Ausgabe,
- kein `input()`,
- kein `print()`,
- kein DB-Zugriff,
- keine Repository-Nutzung,
- keine Schreiboperation,
- keine Kombination mit Status- oder Typfilter.

## Spaetere CLI-Anbindung

Die spaetere CLI-Anbindung soll im bestehenden Review-Bereich erfolgen.

Geplanter Ablauf:

1. Nutzer waehlt Review-Aktivitaet durchsuchen.
2. Friday fragt nach einem Suchbegriff.
3. Friday baut die vorhandene Review Activity Detail View.
4. Friday sucht read-only in den Detail-Items.
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
- Keine fuzzy Suche.
- Keine Volltext-Indexierung.

## Testplan

Modelltests:

- Suchbegriffe werden normalisiert.
- Suche findet Treffer im Label.
- Suche findet Treffer im Excerpt.
- Suche findet Treffer nach Status oder Typ.
- Suche findet Treffer nach lokaler ID.
- Leere oder zu kurze Suchbegriffe bleiben sicher.
- Suche ohne Treffer bleibt gueltig und leer.
- Trefferlimitierung bleibt sichtbar.
- Regex-artige Suchbegriffe werden literal behandelt.
- Read-only Safety-Flags bleiben korrekt.

Spaetere CLI-Tests:

- CLI zeigt Treffer fuer einen Suchbegriff.
- CLI meldet keinen Treffer sicher.
- CLI meldet leere Suchbegriffe sicher.
- Leer oder `z` kehrt ohne Aenderung zurueck.

## Safety-Bewertung

- Planung bleibt local-only.
- Geplante Suche bleibt read-only.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Search Model.
