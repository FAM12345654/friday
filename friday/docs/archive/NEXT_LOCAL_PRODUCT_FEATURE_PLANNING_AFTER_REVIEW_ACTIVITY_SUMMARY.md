# Next Local Product Feature Planning after Review Activity Summary

## Ziel

Diese Planungsrunde waehlt den kleinsten sinnvollen lokalen Produktfortschritt nach dem abgeschlossenen Review Activity Summary Block.

Der Schritt bleibt bewusst dokumentationsorientiert:

- keine Produktlogik-Aenderung,
- keine neuen Tests,
- keine neuen Features,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Ausgangslage

Friday hat jetzt eine lokale read-only Review Activity Summary:

- Review-Menueoption `6. Review-Aktivitaet anzeigen`,
- lokale Zaehler fuer Nachrichten- und Aufgaben-Vorschlaege,
- Anzeige konvertierter Aufgaben-Vorschlaege,
- Anzeige zuletzt lokal geaenderter Vorschlaege,
- User Guide und Finalization Gate vorhanden.

Die Funktion ist bewusst read-only und aendert keine Review-Status.

## Bewertete Optionen

| Option | Nutzen | Risiko | Testaufwand | Safety-Komplexitaet | Empfehlung |
|---|---|---|---|---|---|
| A. Review Activity Detail View | Hoch: Nutzer kann lokale Review-Eintraege genauer ansehen | Niedrig: read-only auf vorhandenen Daten | Niedrig bis mittel: Modell- und CLI-Anzeige testen | Sehr niedrig: keine Writes, keine externen Aktionen | Empfohlen |
| B. Review Activity Filter | Mittel: Status-/Typfilter direkt in Summary | Niedrig bis mittel: neue Filterlogik | Mittel: Filterkombinationen testen | Niedrig: read-only | Danach sinnvoll |
| C. Review Activity Export | Mittel: Uebersicht als Datei speichern | Mittel: lokale Schreiboperation und Pfadregeln | Mittel bis hoch: Guard-/Writer-Tests | Mittel: lokaler Write braucht Approval/Guard | Spaeter, nicht als naechster kleiner Step |
| D. Review Batch Undo Preview | Hoch: Fehler besser abfedern | Mittel bis hoch: Status-Rueckabwicklung kritisch | Hoch: viele Statuspfade | Mittel: lokale Writes betroffen | Nicht direkt nach Summary |
| E. Review Activity Dashboard Badges | Mittel: kompakte Anzeige im Hauptmenue | Niedrig bis mittel: UI-Ausgabe betroffen | Mittel: Main-Menu-Tests | Niedrig | Spaeter sinnvoll |

## Empfohlener naechster Produkt-Step

**Name:** Review Activity Detail View

**Kurzbeschreibung:**
Eine lokale read-only Detailansicht fuer Review-Aktivitaet. Nutzer koennen aus der Summary heraus oder im Review-Bereich eine Liste lokaler Review-Eintraege sehen: Typ, ID, Status, Titel/Textauszug und optional lokale Aufgaben-ID.

## Warum dieser Step

- baut direkt auf der vorhandenen Review Activity Summary auf,
- hoher UX-Nutzen ohne neue Datenhaltung,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen,
- keine Statusaenderungen,
- gut isoliert testbar,
- passt zum vorhandenen Review-Workflow.

## Nicht-Ziele

- keine Freigabe oder Ablehnung von Vorschlaegen,
- keine Batch-Aktion,
- kein Export,
- keine Datei-Schreiboperation,
- keine neue Persistenz,
- keine Datenbankschema-Aenderung,
- keine externen Provider,
- keine echten Nachrichten,
- keine echten Kalendertermine.

## Vorgeschlagener Scope fuer den naechsten Step

Der naechste Step sollte zunaechst nur planen:

`REVIEW_ACTIVITY_DETAIL_VIEW_PLAN.md`

Inhalt:

- Welche Felder angezeigt werden duerfen.
- Wie Nachrichten- und Aufgaben-Vorschlaege einheitlich dargestellt werden.
- Welche Sortierung sinnvoll ist.
- Welche Detailtiefe privacy-sicher ist.
- Welche Tests fuer Modell und CLI noetig sind.

## Vorgeschlagener spaeterer technischer Pfad

| Step | Zweck |
|---|---|
| Review Activity Detail View Plan | Doku-Plan, keine Produktlogik |
| Review Activity Detail View Model | Isoliertes read-only Modell |
| Review Activity Detail View Model Readiness Gate | Freigabe des Modells |
| Review Activity Detail View CLI Plan | CLI-Anbindung planen |
| Review Activity Detail View CLI Implementation | Read-only CLI-Anzeige |
| Review Activity Detail View Finalization Gate | Abschluss und Doku |

## Vorgeschlagener Testplan

Betroffene Testbereiche:

- `friday/tests/test_review_activity_summary.py`
- `friday/tests/test_interface_combined_review.py`

Neue Tests spaeter:

- Detailmodell listet Nachrichten- und Aufgaben-Vorschlaege.
- Detailmodell sortiert stabil.
- Detailmodell zeigt keine sensiblen Zusatzdaten.
- CLI-Detailansicht ist read-only.
- CLI-Detailansicht veraendert keine Pending-Vorschlaege.
- Exit/Rueckkehr bleibt stabil.

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

Naechster sinnvoller Build Step: Review Activity Detail View Plan.
