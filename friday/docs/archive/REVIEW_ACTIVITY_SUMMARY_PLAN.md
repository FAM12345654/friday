# Review Activity Summary Plan

## Ziel

Dieser Plan beschreibt eine spaetere read-only Review-Aktivitaetsuebersicht fuer Friday.

Der Step ist bewusst nur Planung:

- keine Produktlogik-Aenderung,
- keine neuen Tests,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Ausgangslage

Der Review-Batch-Selection-Block ist final abgenommen. Friday kann lokale Review-Vorschlaege einzeln oder als Batch bearbeiten.

Was noch fehlt:

- eine kompakte Uebersicht ueber lokale Review-Aktivitaet,
- eine schnelle Anzeige, wie viele Vorschlaege offen, freigegeben, abgelehnt oder konvertiert sind,
- ein read-only Einstieg fuer Nutzer, die nach Batch-Aktionen verstehen wollen, was lokal passiert ist.

## Geplante Datenquellen

Die Review Activity Summary soll nur vorhandene lokale Daten lesen.

| Datenquelle | Geplante Nutzung |
|---|---|
| `MessageSuggestionRepository.get_all_suggestions()` | Nachrichten-Vorschlaege nach Status zaehlen |
| `TaskSuggestionRepository.get_all_task_suggestions()` | Aufgaben-Vorschlaege nach Status zaehlen |
| `updated_at` | zuletzt veraenderte Vorschlaege sortieren |
| `created_task_id` | konvertierte Aufgaben-Vorschlaege sichtbar machen |

## Geplante Kennzahlen

Die Summary soll folgende Zahlen anzeigen:

- offene Nachrichten-Vorschlaege (`pending`, `edited`),
- lokal freigegebene Nachrichten-Vorschlaege (`approved`),
- abgelehnte Nachrichten-Vorschlaege (`rejected`),
- offene Aufgaben-Vorschlaege (`pending`, `edited`),
- abgelehnte Aufgaben-Vorschlaege (`rejected`),
- konvertierte Aufgaben-Vorschlaege (`converted`),
- Aufgaben-Vorschlaege mit gesetzter `created_task_id`.

## Geplanter CLI-Ort

Empfohlener Ort:

```text
Hauptmenue -> 6. Vorschlaege pruefen / freigeben -> neuer Bereich
```

Moegliche Menue-Erweiterung:

```text
6. Review-Aktivitaet anzeigen
```

Der vorhandene Bereich `5. Batch-Auswahl als Vorschau anzeigen` bleibt unveraendert.

## Geplante Anzeige

Beispiel:

```text
Review-Aktivitaet

Nachrichten-Vorschlaege:
- Offen: 2
- Lokal freigegeben: 3
- Abgelehnt: 1

Aufgaben-Vorschlaege:
- Offen: 1
- Abgelehnt: 0
- In Aufgaben umgewandelt: 4

Zuletzt lokal geaendert:
- Nachricht 12: approved
- Aufgaben-Vorschlag 7: converted -> Aufgabe 14
```

## Nicht-Ziele

- Kein Undo.
- Keine Batch-Aktion.
- Keine Statusaenderung.
- Keine Aufgabe erstellen.
- Keine Nachricht senden.
- Keine Kalenderaktion.
- Kein Export.
- Keine Datenbankschema-Aenderung.
- Keine neuen externen Dienste.

## Sicherheitsregeln

Die Review Activity Summary muss read-only bleiben.

Sie darf:

- lokale Vorschlagsdaten lesen,
- Statuswerte zaehlen,
- kurze Zusammenfassung anzeigen.

Sie darf nicht:

- Vorschlaege aendern,
- Aufgaben erstellen,
- Nachrichten senden,
- Kalendertermine erstellen,
- externe Dienste aufrufen,
- Safety-Flags veraendern.

## Vorgeschlagene Implementierungsschritte

1. Isoliertes Summary-Modell bauen:
   - reine Funktion,
   - Eingabe: Listen von Message- und Task-Suggestions,
   - Ausgabe: strukturierte Summary-Daten.
2. Tests fuer das Summary-Modell ergaenzen.
3. Readiness-Gate fuer das Modell.
4. CLI-Plan fuer die read-only Anzeige.
5. CLI-Implementierung im Review-Bereich.
6. CLI-Readiness-Gate und User-Guide-Update.

## Teststrategie fuer den naechsten technischen Step

Fuer das Modell:

```bash
python -m pytest friday/tests/test_review_activity_summary.py
python -m pytest friday/tests/test_message_suggestion_repository.py
python -m pytest friday/tests/test_task_suggestion_repository.py
```

Full Checks:

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Safety-Bewertung

- Geplanter naechster technischer Step bleibt read-only.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine neuen Provider.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Activity Summary Model**.

Ziel:

- isoliertes read-only Summary-Modell bauen,
- keine CLI-Anbindung im Modell-Step,
- keine Schreiboperation,
- Tests mit einfachen Suggestion-Daten.
