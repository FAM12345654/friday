# Local Contact Context Prompt UI Renderer 14H

## Ziel

Isolierter Renderer für die geplante spätere Kontakt-Kontext-Frage.

## Umfang

- Reine Text-/Optionen-Erzeugung.
- Keine echte CLI-Abfrage.
- Keine `input()`-Nutzung.
- Keine `print()`-Nutzung.
- Keine CLI-Loop-Anbindung.
- Keine DB-Persistenz.
- Keine Message-/Review-/Task-Integration.
- Keine externen Kontakte.
- Keine externen APIs.

## Implementierte Bausteine

- `ContactPromptUIRender`
- `CONTACT_PROMPT_OPTION_LABELS`
- `CONTACT_PROMPT_SKIP_INPUTS`
- `CONTACT_PROMPT_INVALID_MESSAGE`
- `build_contact_prompt_text`
- `render_contact_prompt_ui`

## Verhalten

Der Renderer erzeugt:

- Prompt-Titel,
- Prompt-Frage,
- Optionen 1–8,
- Skip-Eingaben,
- Standardfehlertext,
- Safe-Flags.

Der Renderer fragt nicht selbst ab.

## Safety-/Privacy-Bewertung

- `preview_only=True`
- `persisted=False`
- `external_lookup_used=False`
- keine sensiblen Kategorien
- keine externen Lookups
- keine DB-Schreiboperation
- keine echte Nutzerabfrage
- keine Flow-Integration

## Tests

- `test_contact_context_prompt_ui_renderer.py`
- Full Regression: `python -m pytest friday/tests`

## Empfehlung für Build Step 14I

Contact Context Prompt Input Parser:

- reine Parser-Funktion für spätere Eingaben,
- keine `input()`-Nutzung,
- keine CLI-Anbindung,
- keine Persistenz.
