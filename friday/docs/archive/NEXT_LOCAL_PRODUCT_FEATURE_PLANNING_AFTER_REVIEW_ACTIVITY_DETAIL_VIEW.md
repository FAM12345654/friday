# Next Local Product Feature Planning after Review Activity Detail View

## Ziel

Diese Planungsrunde waehlt den kleinsten sinnvollen lokalen Produktfortschritt nach dem abgeschlossenen Review Activity Detail View Block.

Der Schritt bleibt bewusst dokumentationsorientiert:

- keine Produktlogik-Aenderung,
- keine neuen Tests,
- keine neuen Features,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Ausgangslage

Friday hat jetzt:

- Review Activity Summary mit lokalen Zaehlern,
- Review Activity Detail View mit lokalen Eintraegen,
- read-only CLI-Anbindung fuer Summary und Detail View,
- Tests fuer Modell und CLI,
- User Guides und Finalization Gates.

Die Review-Aktivitaet ist damit sichtbar, aber noch nicht gezielt filterbar.

## Bewertete Optionen

| Option | Nutzen | Risiko | Testaufwand | Safety-Komplexitaet | Empfehlung |
|---|---|---|---|---|---|
| A. Review Activity Status Filter | Hoch: Nutzer kann offene, freigegebene, abgelehnte oder konvertierte Eintraege gezielt sehen | Niedrig: read-only Filter auf vorhandenen Daten | Mittel: Filterlogik und CLI-Ausgabe testen | Sehr niedrig: keine Writes, keine externen Aktionen | Empfohlen |
| B. Review Activity Type Filter | Mittel: Nachrichten oder Aufgaben getrennt anzeigen | Niedrig: einfacher read-only Filter | Niedrig bis mittel | Sehr niedrig | Als Teil von A oder danach sinnvoll |
| C. Review Activity Export | Mittel: lokale Review-Uebersicht als Datei speichern | Mittel: lokale Schreiboperation mit Guard/Approval | Mittel bis hoch | Mittel: lokaler Write braucht klare Regeln | Spaeter |
| D. Review Activity Dashboard Badge | Mittel: kompakte Anzeige im Hauptmenue | Niedrig bis mittel: Menueausgabe betroffen | Mittel | Niedrig | Spaeter sinnvoll |
| E. Review Activity Search | Mittel bis hoch: Suche in Review-Details | Mittel: Textsuche/Privacy-Grenzen | Mittel | Niedrig | Spaeter nach Filter sinnvoll |

## Empfohlener naechster Produkt-Step

**Name:** Review Activity Status Filter

**Kurzbeschreibung:**
Ein lokaler read-only Filter fuer Review-Aktivitaet. Nutzer koennen spaeter Eintraege nach Status anzeigen lassen, z. B. `pending`, `approved`, `rejected`, `converted` oder `all`.

## Warum dieser Step

- baut direkt auf Summary und Detail View auf,
- erhoeht Nutzbarkeit ohne Schreiboperation,
- keine neue Persistenz,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen,
- gut isoliert als Modell testbar,
- spaeter einfach in die CLI integrierbar.

## Nicht-Ziele

- Keine Statusaenderung.
- Keine Freigabe oder Ablehnung.
- Keine Batch-Aktion.
- Keine Aufgabe erstellen.
- Kein Export.
- Keine Datei-Schreiboperation.
- Keine Datenbankschema-Aenderung.
- Keine externen Provider.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.

## Vorgeschlagener Scope fuer den naechsten Step

Der naechste Step sollte zunaechst nur planen:

`REVIEW_ACTIVITY_STATUS_FILTER_PLAN.md`

Inhalt:

- erlaubte Filterwerte,
- Verhalten bei `all`,
- Verhalten bei unbekanntem Filter,
- ob Filter nur Modell oder spaeter CLI betrifft,
- welche Tests fuer Modell und CLI noetig sind,
- Safety-Grenzen fuer read-only Filterung.

## Vorgeschlagener spaeterer technischer Pfad

| Step | Zweck |
|---|---|
| Review Activity Status Filter Plan | Doku-Plan, keine Produktlogik |
| Review Activity Status Filter Model | Isoliertes read-only Filtermodell |
| Review Activity Status Filter Model Readiness Gate | Freigabe des Modells |
| Review Activity Status Filter CLI Plan | CLI-Anbindung planen |
| Review Activity Status Filter CLI Implementation | Read-only CLI-Filter |
| Review Activity Status Filter Finalization Gate | Abschluss und Doku |

## Vorgeschlagener Testplan

Betroffene Testbereiche:

- `friday/tests/test_review_activity_detail_view.py`
- spaeter `friday/tests/test_interface_combined_review.py`

Neue Tests spaeter:

- Filter `all` zeigt alle lokalen Detail-Items.
- Filter `pending` zeigt nur offene Items.
- Filter `approved` zeigt nur lokal freigegebene Nachrichten-Vorschlaege.
- Filter `rejected` zeigt abgelehnte Vorschlaege.
- Filter `converted` zeigt konvertierte Aufgaben-Vorschlaege.
- Unbekannter Filter ergibt eine sichere leere oder invalid Antwort.
- Filter bleibt read-only.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Keine Schreiboperation geplant.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Validierung fuer diese Planungsrunde

Empfohlene Checks:

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Status Filter Plan.
