# Next Local Product Feature Planning after Review Activity Status Filter

## Ziel

Diese Planungsrunde waehlt den kleinsten sinnvollen lokalen Produktfortschritt nach dem abgeschlossenen Review Activity Status Filter Block.

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
- Review Activity Status Filter fuer gezielte Statusansichten,
- read-only CLI-Anbindung fuer Summary, Detail View und Statusfilter,
- Tests fuer Modell und CLI,
- User Guides und Finalization Gates.

Die Review-Aktivitaet ist damit nach Status sichtbar. Der naechste kleine Nutzbarkeitsgewinn ist eine Trennung nach Review-Typ.

## Bewertete Optionen

| Option | Nutzen | Risiko | Testaufwand | Safety-Komplexitaet | Empfehlung |
|---|---|---|---|---|---|
| A. Review Activity Type Filter | Hoch: Nutzer kann Nachrichten- und Aufgaben-Vorschlaege getrennt ansehen | Niedrig: read-only Filter auf vorhandenen Detail-Items | Niedrig: isolierte Filterlogik | Sehr niedrig: keine Writes, keine externen Aktionen | Empfohlen |
| B. Review Activity Search | Mittel bis hoch: Nutzer kann Review-Details textlich finden | Mittel: Suchgrenzen und Privacy-Erwartung muessen sauber geplant werden | Mittel | Niedrig | Danach sinnvoll |
| C. Review Activity Combined Filter | Mittel: Status und Typ gemeinsam filtern | Mittel: CLI-Komplexitaet steigt | Mittel | Niedrig | Spaeter nach einfachem Type Filter |
| D. Review Activity Export | Mittel: lokale Review-Uebersicht als Datei speichern | Mittel: lokaler Write braucht Guard und Token | Mittel bis hoch | Mittel | Spaeter |
| E. Review Dashboard Badge | Mittel: Review-Zustand schneller im Hauptmenue sichtbar | Niedrig bis mittel: Hauptmenue-Ausgabe betroffen | Mittel | Niedrig | Spaeter |

## Empfohlener naechster Produkt-Step

**Name:** Review Activity Type Filter

**Kurzbeschreibung:**
Ein lokaler read-only Filter fuer Review-Aktivitaet. Nutzer koennen spaeter Eintraege nach Typ anzeigen lassen, z. B. `message`, `task` oder `all`.

## Warum dieser Step

- baut direkt auf der vorhandenen Detail View auf,
- nutzt vorhandene `suggestion_type`-Informationen,
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

`REVIEW_ACTIVITY_TYPE_FILTER_PLAN.md`

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
| Review Activity Type Filter Plan | Doku-Plan, keine Produktlogik |
| Review Activity Type Filter Model | Isoliertes read-only Filtermodell |
| Review Activity Type Filter Model Readiness Gate | Freigabe des Modells |
| Review Activity Type Filter CLI Plan | CLI-Anbindung planen |
| Review Activity Type Filter CLI Implementation | Read-only CLI-Filter |
| Review Activity Type Filter User Guide | Nutzererklaerung |
| Review Activity Type Filter Finalization Gate | Abschluss und Doku |

## Vorgeschlagener Testplan

Betroffene Testbereiche:

- `friday/tests/test_review_activity_type_filter.py`
- spaeter `friday/tests/test_interface_combined_review.py`

Neue Tests spaeter:

- Filter `all` zeigt alle lokalen Detail-Items.
- Filter `message` zeigt nur Nachrichten-Vorschlaege.
- Filter `task` zeigt nur Aufgaben-Vorschlaege.
- Unbekannter Filter ergibt eine sichere invalid Antwort.
- Filter bleibt read-only.
- CLI kehrt bei leerer Eingabe oder `z` stabil zur Review-Uebersicht zurueck.

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

Naechster sinnvoller Build Step: Review Activity Type Filter Plan.
