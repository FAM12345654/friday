# Local Contact Context Prompt Draft Flow Plan 14K

## Ziel

Planung des nächsten lokalen Schritts für den Kontakt-Kontext-Prompt:
den bisher isolierten Renderer und Parser in einen klaren Draft-Flow zu überführen, weiterhin ohne Produktlogik-Integration.

## Gültiger Scope (14K)

14K ist reines Planen/Definieren:

- kein Produktcode,
- keine CLI-Loop-Anbindung,
- keine `input()`-Nutzung in der eigentlichen Flow-Umsetzung,
- keine Persistenz,
- keine DB-Änderung,
- keine externen Kontakte/APIs,
- keine Integration in Message-/Review-/Task-Flows.

## Voraussetzungen aus 14A–14J

- `ContactContextPreview` existiert (`14A`).
- `ContactPromptCandidate` existiert (`14C`).
- Prompt-Preview-Composition ist implementiert (`14D`).
- UI-Renderer ohne `input()` existiert (`14H`).
- Input-Parser ohne `input()` existiert (`14I`).
- Renderer/Parser-Konsistenz ist geprüft (`14J`).

## Draft-Flow (geplant)

```text
1. Relevanten Kontaktkontext ermitteln
   (bekannte Kontaktinformationen prüfen: unknown / known / skipped / ask_later)
2. Kontakt-Kontext-Prompt rendern (Renderer)
3. Roh-Eingabe lesen (außerhalb dieses Schritts)
4. Eingabe über Parser auswerten
5. Verhalten je Ergebnis:
   - select_contact_type: Kandidat mit Kontaktart hinterlegen (lokal)
   - skip: Kandidat als übersprungen markieren (lokal)
   - invalid: Standardfehlertext zeigen, erneut versuchen
6. Draft-Ergebnis zurückgeben (ohne Schreibzugriff, ohne Nebenwirkung außerhalb des lokalen Rückgabewerts)
```

## Sicherheitsgrenzen (festgelegt)

- Keine `delete`-ähnlichen Sonderaktionen im Kontext dieses Flows.
- `"JA"` ist weiterhin ungültig (`invalid`) und löst keine Sonderlogik aus.
- Skip-Eingaben bleiben konsistent (`""`, `8`, `z`, `zurück`, `skip`, `überspringen`).
- Alle Safe-Flags bleiben:
  - `preview_only=True`
  - `persisted=False`
  - `external_lookup_used=False`

## Nicht-Ziele dieses Schritts

- Kein produktiver CLI-Workflowscope (kein Run-Loop-Branch).
- Keine Speicherung in SQLite.
- Keine Nachrichtensende-, Terminbuchungs- oder Export-Funktionalität.
- Keine Modell-/Provider-Calls.

## Nächste technische Vorprüfung vor 14L

- Vor der späteren Implementierung sollten folgende Readiness-Zustände unverändert grün bleiben:
  - `test_contact_context_prompt_parse_readiness.py`
  - `test_contact_context_prompt_input_parser.py`
  - `test_contact_context_prompt_ui_renderer.py`

## Empfehlung für nächsten Build Step

- `14L`: Implementierungsentwurf für den lokalen Contact-Context-Draft-Flow unter Verwendung von
  - `render_contact_prompt_ui(...)`
  - `parse_contact_prompt_input(...)`
  mit klaren Abbruch- und Wiederholungsregeln und weiterhin lokaler/sicherer Semantik.
