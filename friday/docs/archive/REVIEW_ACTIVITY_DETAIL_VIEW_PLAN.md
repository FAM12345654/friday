# Review Activity Detail View Plan

## Ziel

Dieser Schritt plant eine lokale read-only Detailansicht fuer Review-Aktivitaet in Friday.

Die Detailansicht soll auf der bestehenden Review Activity Summary aufbauen und einzelne lokale Review-Eintraege sichtbarer machen, ohne Status zu aendern, Aufgaben zu erstellen, Dateien zu schreiben oder externe Aktionen auszufuehren.

## Ausgangslage

Friday hat bereits:

- eine lokale Review Activity Summary,
- Zaehler fuer Nachrichten- und Aufgaben-Vorschlaege,
- Anzeige zuletzt lokal geaenderter Vorschlaege,
- CLI-Anbindung im Review-Menue,
- User Guide und Finalization Gate.

Die bestehende Summary beantwortet die Frage: "Wie viele Review-Eintraege gibt es in welchem Status?"

Die geplante Detailansicht soll die Frage beantworten: "Welche lokalen Review-Eintraege sind das konkret?"

## Geplanter Umfang

| Bereich | Geplantes Verhalten |
|---|---|
| Nachrichten-Vorschlaege | Lokale Vorschlaege mit ID, Status, Sender und kurzem Textauszug anzeigen |
| Aufgaben-Vorschlaege | Lokale Vorschlaege mit ID, Status, Titel und optionaler lokaler Aufgaben-ID anzeigen |
| Sortierung | Stabil und nachvollziehbar, bevorzugt nach letzter lokaler Aenderung oder ID |
| Anzeige | Kurze Liste, keine langen Nachrichtentexte |
| Verhalten | Read-only, keine Statusaenderung, keine Freigabe, keine Ablehnung |
| Datenquelle | Vorhandene lokale Repositories/Daten aus dem Review-System |

## Erlaubte Felder

| Typ | Erlaubte Felder |
|---|---|
| Nachrichten-Vorschlag | `id`, `status`, `sender`, kurzer `text`-Auszug, optional `updated_at` |
| Aufgaben-Vorschlag | `id`, `status`, `title`, optional `created_task_id`, optional `updated_at` |

## Nicht erlaubte oder nicht noetige Felder

- Keine vollstaendigen langen Nachrichtentexte in der Detailuebersicht.
- Keine sensiblen Kontakt-Kontext-Details.
- Keine Provider- oder Account-Daten.
- Keine externen IDs, falls sie spaeter existieren.
- Keine Secrets.
- Keine Dateipfade ausser lokalen Test-/Doku-Verweisen.

## UX-Vorschlag

Die Anzeige koennte im Review-Bereich als neue read-only Option geplant werden:

```text
7. Review-Aktivitaet im Detail anzeigen
```

Die Ausgabe sollte kurz bleiben:

```text
Review-Aktivitaet im Detail

Nachrichten-Vorschlaege:
- #1 [pending] Chef: Kannst du morgen...
- #2 [approved] Team: Termin bestaetigt...

Aufgaben-Vorschlaege:
- #3 [pending] Rechnung pruefen
- #4 [converted] Unterlagen vorbereiten -> Aufgabe 12
```

Die genaue Nummerierung der CLI-Option muss im technischen CLI-Plan nochmals mit dem bestehenden Review-Menue abgeglichen werden.

## Modell-Vorschlag

Ein spaeteres isoliertes Modell koennte diese Strukturen nutzen:

```python
ReviewActivityDetailItem
ReviewActivityDetailView
build_review_activity_detail_view(message_suggestions, task_suggestions)
```

Das Modell bleibt:

- ohne `input()`,
- ohne `print()`,
- ohne DB-Zugriff,
- ohne externe Imports,
- ohne Seiteneffekte.

## Teststrategie fuer spaetere Umsetzung

Modelltests:

- Nachrichten- und Aufgaben-Vorschlaege werden gemeinsam gelistet.
- Status wird stabil uebernommen.
- Textauszuege werden gekuerzt.
- `created_task_id` wird nur bei Aufgaben-Vorschlaegen angezeigt.
- Leere Eingaben ergeben eine leere Detailansicht.
- Unbekannte oder fehlende Felder brechen nicht.

CLI-Tests:

- Detailoption wird im Review-Menue angezeigt.
- Detailansicht zeigt lokale Nachrichten- und Aufgaben-Vorschlaege.
- Detailansicht ist read-only.
- Pending-Vorschlaege bleiben pending.
- Rueckkehr in den Review-Loop bleibt stabil.

## Nicht-Ziele

- Keine Freigabe oder Ablehnung von Vorschlaegen.
- Keine Batch-Aktion.
- Keine Aufgabe erstellen.
- Kein Export.
- Keine Datei-Schreiboperation.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.

## Safety-Bewertung

- Planung bleibt local-only.
- Geplante Detailansicht bleibt read-only.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
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

Naechster sinnvoller Build Step: Review Activity Detail View Model.
