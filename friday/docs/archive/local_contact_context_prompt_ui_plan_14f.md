# Local Contact Context Prompt UI Plan 14F

## Ziel

Planung der späteren CLI-Frage für lokalen Kontakt-Kontext.

`14F` ist reine Planung ohne Implementierung:

- keine `input()`-Nutzung,
- keine CLI-Flow-Anbindung,
- keine Persistenz,
- keine neue Produktlogik.

## Ausgangslage

- `14A`: `ContactContextPreview` vorhanden
- `14B`: Prompt-Regeln geplant
- `14C`: `ContactPromptCandidate` vorhanden
- `14D`: `ContactPromptPreview` Composition vorhanden
- `14E`: Readiness Gate abgeschlossen

## Erlaubte spätere Frageorte

| Ort | Erlaubt? | Hinweis |
|---|---:|---|
| Nachrichten-Review bei unbekanntem Absender | ja | nur wenn Kontaktart unbekannt |
| Aufgabe aus Nachricht erstellen | ja | nur bei aktivem Kontext |
| Explizite Person bearbeiten | ja | Nutzerintention klar |
| Explizite Nutzerfrage zu einer Person | ja | Nutzer hat Kontext geöffnet |
| App-Start | nein | zu störend |
| Hauptmenü ohne konkreten Kontakt | nein | kein aktiver Nutzen |
| Jede neue Nachricht automatisch | nein | Wiederholungsrisiko |
| Bekannter Kontakt | nein | keine Wiederholung |

## Geplanter UI-Text

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

## Erlaubte Eingaben

| Eingabe | Bedeutung |
|---|---|
| `1` | kunde |
| `2` | kollege |
| `3` | mitarbeiter |
| `4` | familie |
| `5` | freund |
| `6` | dienstleister |
| `7` | sonstiges |
| `8` | überspringen |
| Enter | überspringen |
| `z` | zurück/überspringen |
| `skip` | überspringen |
| `überspringen` | überspringen |

## Optionale Folgefragen

Nur nach Auswahl einer Kontaktart:

```text
Optionaler Spitzname oder Kurzname für {Name} (Enter = überspringen):
```

```text
Kurzer lokaler Kontext zu {Name} (Enter = überspringen):
```

## Wiederholungsvermeidung

| Status | Verhalten |
|---|---|
| `unknown` | darf bei relevantem Kontext gefragt werden |
| `known` | nicht automatisch erneut fragen |
| `skipped` | in derselben Session nicht erneut fragen |
| `ask_later` | nur bei neuem relevantem Kontext erneut fragen |

## Skip-Flow

Geplanter Text:

```text
Kontakt-Kontext übersprungen. Friday fragt in dieser Sitzung nicht erneut nach {Name}.
```

- `8`, Enter, `z`, `skip` oder `überspringen` brechen die Abfrage ohne Nebenwirkungen ab.
- `skipped` wird nur als Session-Status dokumentiert.
- Kein automatisches Wiederanfordern derselben Person in derselben Session.

## Safety-/Privacy-Grenzen

- keine sensiblen Kategorien:
  - Politik
  - Religion
  - Ethnie
  - Gesundheit
  - sexuelle Orientierung
  - Gewerkschaftszugehörigkeit
  - strafrechtliche Details
  - private Finanzdetails
  - intime private Profile
- keine externen Kontakte
- keine externen APIs
- keine Netzwerkanfragen
- keine automatische Persistenz
- keine DB-Migration
- keine Obsidian-Schreiboperation
- keine Message-/Review-/Task-Integration in 14F

## Nicht-Ziele

- keine Implementierung
- keine CLI-Abfrage
- keine Persistenz
- keine Tests
- keine Flow-Integration
- keine echten Kontaktimporte

## Spätere Teststrategie

Bei späterer Implementierung prüfen:

- erlaubter Kontext zeigt Prompt
- bekannter Kontakt zeigt keinen Prompt
- App-Start zeigt keinen Prompt
- Skip setzt Session-Suppression
- ungültige Eingabe nutzt Standardfehler (`Ungültige Auswahl. Bitte erneut versuchen.`)
- Enter überspringt
- optionale Folgefragen können leer bleiben
- keine Persistenz ohne separates Persistenz-Gate

## Empfehlung für Build Step 14G

`14G` als UI-Readiness Gate:

- prüft den UI-Plan gegen 14A–14F auf Konsistenz,
- hält weiterhin auf reine Dokumentation,
- danach optional 14H als erste isolierte UI-Render-Funktion ohne `input()`.
