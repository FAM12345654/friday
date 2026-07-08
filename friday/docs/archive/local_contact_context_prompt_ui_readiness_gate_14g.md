# Local Contact Context Prompt UI Readiness Gate 14G

## Ziel

Readiness-/Safety-Gate für die geplante spätere CLI-Frage zum lokalen Kontakt-Kontext.

`14G` ist reine Dokumentation. Es wird keine CLI-Abfrage implementiert.

## Geprüfte Grundlagen

| Step | Thema | Status |
|---|---|---|
| 14A | ContactContextPreview | umgesetzt |
| 14B | Contact Context Prompt Planning | geplant |
| 14C | ContactPromptCandidate | umgesetzt |
| 14D | ContactPromptPreview Composition | umgesetzt |
| 14E | Prompt Preview Readiness Gate | abgeschlossen |
| 14F | Prompt UI Planning | geplant |

## Geprüfter UI-Plan

Die geplante spätere Frage lautet:

```text
Kontakt-Kontext für {Name}

Wer ist {Name} für dich?
1. Kunde
2. Kollege
3. Mitarbeiter
4. Familie
5. Freund
6. Dienstleister
7. Sonstiges
8. Überspringen

Auswahl (1-8):
```

## Readiness-Ergebnis

Freigegeben als Plan:

- Frage ist kurz.
- Frage ist lokal.
- Frage ist überspringbar.
- Eingaben sind begrenzt.
- Skip-Pfad ist geplant.
- Wiederholungsvermeidung ist geplant.
- Keine sensiblen Kategorien sind vorgesehen.
- Keine automatische Persistenz ist vorgesehen.

Nicht freigegeben:

- echte CLI-Abfrage,
- `input()`-Nutzung,
- DB-Speicherung,
- Migration,
- Message-/Review-/Task-Integration,
- externe Kontakte,
- externe APIs,
- Obsidian-Write.

## Erlaubte spätere Frageorte

| Ort                                         | Status |
| --- | --- |
| Nachrichten-Review bei unbekanntem Absender | geplant erlaubt |
| Aufgabe aus Nachricht erstellen             | geplant erlaubt |
| Explizite Person bearbeiten                 | geplant erlaubt |
| Explizite Nutzerfrage zu einer Person       | geplant erlaubt |
| App-Start                                   | nicht erlaubt   |
| Hauptmenü ohne konkreten Kontakt            | nicht erlaubt   |
| Jede neue Nachricht automatisch             | nicht erlaubt   |
| Bekannter Kontakt                           | nicht erlaubt   |

## Eingabe- und Skip-Regeln

| Eingabe        | Geplantes Verhalten |
| --- | --- |
| `1` bis `7`    | Kontaktart wählen |
| `8`            | überspringen |
| Enter          | überspringen |
| `z`            | zurück/überspringen |
| `skip`         | überspringen |
| `überspringen` | überspringen |
| ungültige Eingabe | Standardfehler anzeigen |

Standardfehler:

```text
Ungültige Auswahl. Bitte erneut versuchen.
```

## Wiederholungsvermeidung

| Status      | Verhalten |
| --- | --- |
| `unknown`   | darf bei relevantem Kontext gefragt werden |
| `known`     | nicht automatisch erneut fragen |
| `skipped`   | in derselben Session nicht erneut fragen |
| `ask_later` | nur bei neuem relevantem Kontext erneut fragen |

## Safety-/Privacy-Ergebnis

- Keine sensiblen Kategorien.
- Keine politischen/religiösen/gesundheitlichen/ethnischen Profile.
- Keine externen Kontakte.
- Keine externen APIs.
- Keine Netzwerkaktionen.
- Keine automatische Persistenz.
- Keine DB-Migration.
- Keine Obsidian-Schreiboperation.
- Keine Message-/Review-/Task-Integration.
- Safety-Flags unverändert.
- Delete-Policy unverändert.

## Teststatus

- `test_contact_context_preview.py`: `8` passed
- `test_contact_context_prompt_candidate.py`: `8` passed
- `test_contact_context_prompt_preview_composition.py`: `7` passed
- Full Regression: `279` passed
- compileall: erfolgreich
- git diff --check: sauber

## Entscheidung

Der UI-Plan ist bereit für einen nächsten isolierten technischen Schritt.

Freigegeben für später:

- isolierte UI-Render-Funktion ohne `input()`,
- reine Text-/Optionen-Erzeugung,
- Unit-Tests für Ausgabe und Optionen.

Weiterhin nicht freigegeben:

- echte Eingabeabfrage,
- CLI-Loop-Anbindung,
- Speicherung,
- DB,
- externe Kontakte,
- Flow-Integration.

## Empfehlung für Build Step 14H

Contact Context Prompt UI Renderer:

- isolierte Render-Funktion für Prompt-Text und Optionen,
- keine `input()`-Nutzung,
- keine CLI-Anbindung,
- keine Persistenz,
- keine externen Aktionen.
