# Review Activity Combined Filter Plan

## Ziel

Dieser Plan beschreibt den naechsten lokalen Review-Activity-Block fuer Friday:

**Review Activity Combined Filter**

Der Block soll die bereits vorhandenen read-only Review-Activity-Funktionen kombinieren:

- Status Filter,
- Type Filter,
- Search.

Der Plan ist ein reines Readiness- und Produktplanungsdokument. In diesem Schritt wird keine Produktlogik umgesetzt.

## Ausgangslage

Bereits abgeschlossen sind:

- Review Activity Summary,
- Review Activity Detail View,
- Review Activity Status Filter,
- Review Activity Type Filter,
- Review Activity Search,
- Chat-1 Product and CLI Finalization Gate.

Der naechste sinnvolle Schritt ist nicht ein neuer Schreibpfad, sondern eine kleine read-only Verbesserung der bestehenden Review-Journey.

## Gewuenschter Nutzerfluss

Friday soll spaeter lokale Review-Aktivitaeten mit mehreren Kriterien gleichzeitig eingrenzen koennen:

- Status allein,
- Typ allein,
- Suchbegriff allein,
- Status plus Typ,
- Status plus Suchbegriff,
- Typ plus Suchbegriff,
- Status plus Typ plus Suchbegriff.

Beispiele:

- offene Task-Vorschlaege anzeigen,
- angenommene Nachrichtenvorschlaege anzeigen,
- alle Review-Eintraege mit einem Suchbegriff in Titel oder Beschreibung finden,
- nur abgelehnte Eintraege eines bestimmten Typs durchsuchen.

## Vorgeschlagene Filterreihenfolge

Das spaetere Modell soll deterministisch und leicht testbar bleiben.

Empfohlene Reihenfolge:

1. lokale Review-Aktivitaeten laden oder als In-Memory-Liste entgegennehmen,
2. optional nach Status filtern,
3. optional nach Typ filtern,
4. optional Suchbegriff anwenden,
5. Ergebnis stabil sortieren,
6. leere Trefferliste klar darstellen.

Die Reihenfolge ist bewusst einfach. Status und Typ reduzieren die Ergebnismenge, Search arbeitet danach auf dem verbleibenden lokalen Datensatz.

## Eingabegrenzen

Der geplante Combined Filter soll nur lokale, harmlose Filterwerte akzeptieren:

- bekannte Statuswerte,
- bekannte Review-Activity-Typen,
- optionaler Suchbegriff als lokaler String.

Ungueltige Status- oder Typwerte sollen nicht stillschweigend als neue Werte interpretiert werden.

Leere Suchbegriffe sollen wie "keine Suche" behandelt werden.

## Modell-Grenzen

Der erste technische Step soll ein isoliertes read-only Modell sein:

- kein CLI-Menuepunkt,
- keine Dateioperation,
- kein Datenbank-Write,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen,
- keine echten Modellaufrufe,
- keine Batch-Aktion,
- keine gespeicherten Filter-Presets.

## CLI-Grenzen

Eine CLI-Anbindung ist erst nach einem eigenen Model Readiness Gate erlaubt.

Die spaetere CLI soll:

- nur lokale Review-Aktivitaeten anzeigen,
- jederzeit Ruecksprung ins Review-Menue erlauben,
- ungueltige Filtereingaben klar erklaeren,
- keine Review-Entscheidungen automatisch anwenden,
- keine Schreibaktion ausloesen.

## Teststrategie

Der naechste technische Model-Step soll Tests mit In-Memory-Daten verwenden.

Mindestfaelle:

- Status allein filtert korrekt,
- Typ allein filtert korrekt,
- Suche allein filtert korrekt,
- Status plus Typ filtert korrekt,
- Status plus Suche filtert korrekt,
- Typ plus Suche filtert korrekt,
- Status plus Typ plus Suche filtert korrekt,
- leere Suche veraendert das Ergebnis nicht,
- ungueltiger Status wird abgewiesen,
- ungueltiger Typ wird abgewiesen,
- Ergebnisreihenfolge bleibt stabil,
- leere Trefferliste bleibt sicher und lesbar.

## Safety-Grenzen

Die folgenden Safety-Flags bleiben unveraendert:

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Nicht-Ziele

Nicht Teil dieses Blocks:

- neue Tabellen,
- DB-Migrationen,
- gespeicherte Filter-Presets,
- automatische Review-Batch-Aktionen,
- echte externe Nachrichten,
- echte Kalender-, Wetter- oder Musikaktionen,
- Cloud-Provider,
- Netzwerkaktionen,
- echte AI-Modellaufrufe,
- Veraenderung der Delete-Policy.

## Readiness-Entscheidung

Der Plan ist bereit fuer den naechsten kleinsten technischen Step:

`REVIEW_ACTIVITY_COMBINED_FILTER_MODEL.md`

Dieser Step darf nur ein isoliertes read-only Modell mit Tests enthalten.
