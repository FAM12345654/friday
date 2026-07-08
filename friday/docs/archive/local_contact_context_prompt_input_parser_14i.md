# Local Contact Context Prompt Input Parser 14I

## Ziel

Isolierter Parser für spätere Kontakt-Kontext-Prompt-Eingaben.

## Umfang

- Reine String-Interpretation.
- Keine echte CLI-Abfrage.
- Keine `input()`-Nutzung.
- Keine `print()`-Nutzung.
- Keine CLI-Loop-Anbindung.
- Keine DB-Persistenz.
- Keine Message-/Review-/Task-Integration.
- Keine externen Kontakte.
- Keine externen APIs.

## Implementierte Bausteine

- `ContactPromptInputParseResult`
- `ContactPromptInputAction`
- `CONTACT_PROMPT_INPUT_TO_TYPE`
- `normalize_contact_prompt_input`
- `parse_contact_prompt_input`

## Verhalten

Gültige Auswahl:

| Eingabe | Kontaktart |
|---|---|
| `1` | kunde |
| `2` | kollege |
| `3` | mitarbeiter |
| `4` | familie |
| `5` | freund |
| `6` | dienstleister |
| `7` | sonstiges |

Skip-Eingaben:

- Enter / leer
- `8`
- `z`
- `zurück`
- `skip`
- `überspringen`

Ungültige Eingaben liefern:

- `Ungültige Auswahl. Bitte erneut versuchen.`

## Safety-/Privacy-Bewertung

- `preview_only=True`
- `persisted=False`
- `external_lookup_used=False`
- keine sensiblen Kategorien
- keine externen Lookups
- keine DB-Schreiboperation
- keine echte Nutzerabfrage
- keine Flow-Integration
- keine Delete-Aktion

## Tests

- `test_contact_context_prompt_input_parser.py`
- Full Regression: `python -m pytest friday/tests`

## Empfehlung für Build Step 14J

Contact Context Prompt Parse Readiness Gate:

- prüft Parser + Renderer zusammen,
- weiterhin keine CLI-Anbindung,
- weiterhin keine Persistenz.
