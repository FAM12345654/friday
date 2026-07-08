# Next Local Product Block Planning After Chat 1 Finalization

## Ziel

Dieses Planungs-Gate legt den naechsten kleinen lokalen Produktblock nach dem Abschluss der Chat-1 Produkt- und CLI-Fertigstellung fest.

Der Schritt ist bewusst nur Planung:

- keine Code-Aenderung,
- keine CLI-Aenderung,
- keine Datenbankmigration,
- keine externen Aktionen,
- keine echten Provider- oder Modellaufrufe.

## Ausgewaehlter naechster Produktblock

Empfohlen wird:

**Review Activity Combined Filter**

Der Block kombiniert bereits vorhandene lokale Review-Activity-Funktionen:

- Status Filter,
- Type Filter,
- Search,
- bestehende Activity-Daten aus lokalen Vorschlagsquellen.

## Warum dieser Block klein und sicher ist

- Der Block ist read-only planbar und umsetzbar.
- Es werden vorhandene lokale Review-Daten genutzt.
- Es ist keine neue Persistenz notwendig.
- Es ist keine Datenbankschema-Aenderung notwendig.
- Es sind keine externen Aktionen notwendig.
- Die bestehende Review Activity Journey wird nicht ersetzt, sondern vorsichtig erweitert.
- Die Funktion passt direkt an die bereits abgeschlossenen Review Activity Blocks an.

## Produktnutzen

Der Nutzer kann spaeter gezielter lokale Review-Aktivitaeten eingrenzen, zum Beispiel:

- nur offene Eintraege eines bestimmten Typs,
- nur angenommene Task-Vorschlaege,
- Suchbegriff plus Status,
- Suchbegriff plus Typ,
- Status plus Typ plus Suchbegriff.

Das reduziert Menuewechsel und macht die Review-Journey besser nachvollziehbar.

## Erste Build-Steps

1. `REVIEW_ACTIVITY_COMBINED_FILTER_PLAN.md`
   - Detaillierter Plan fuer die Kombination aus Status, Typ und Suche.
   - Keine Implementierung.

2. `REVIEW_ACTIVITY_COMBINED_FILTER_MODEL.md`
   - Isoliertes read-only Modell fuer kombinierte Filterung.
   - Tests mit lokalen In-Memory-Daten.

3. `REVIEW_ACTIVITY_COMBINED_FILTER_MODEL_READINESS_GATE.md`
   - Abschlusspruefung des isolierten Modells vor jeder CLI-Anbindung.

## Spaetere optionale Schritte

- CLI-Plan fuer eine read-only Anzeige im Review-Menue.
- CLI-Implementierung nur nach Readiness-Gate.
- Nutzererklaerung fuer kombinierte Filter.
- Finalization Gate nach Full Regression.

## No-Go-Risiken

Nicht Teil dieses Blocks:

- gespeicherte Filter-Presets,
- neue Tabellen oder DB-Migrationen,
- automatische Batch-Aktionen,
- externe Nachrichten, Kalender, Wetter, Musik oder Provider,
- echte AI-Modellaufrufe,
- Cloud- oder Netzwerkaktionen,
- Veraenderung der Safety-Flags,
- Veraenderung der Delete-Policy.

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

## Ergebnis

Der naechste lokale Produktblock ist geplant als:

**Review Activity Combined Filter**

Naechster sinnvoller Build-Step:

`REVIEW_ACTIVITY_COMBINED_FILTER_PLAN.md`
