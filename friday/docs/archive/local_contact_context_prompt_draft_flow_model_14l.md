# Local Contact Context Prompt Draft Flow Model 14L

## Ziel

Isolierter In-Memory-Draft-Flow für lokale Kontakt-Kontext-Prompts.

## Scope

- reines, side-effect-freies Flow-Modell
- keine CLI-Loop-Anbindung
- keine echte `input()`-Nutzung
- keine `print()`-Nutzung
- keine Persistenz/DB
- keine Message-/Review-/Task-Integration
- keine externen Kontakte/APIs

## Implementierte Bausteine

- `ContactPromptDraftFlowResult`
- `ContactPromptDraftFlowStatus`
- `prepare_contact_prompt_draft_flow`
- `apply_contact_prompt_draft_input`

## Datenmodell

### Statuswerte

| Status | Bedeutung |
|---|---|
| `blocked` | Prompt darf nicht angezeigt werden |
| `rendered` | Prompt-Daten wurden erzeugt |
| `selected` | Kontaktart wurde ausgewählt |
| `skipped` | Prompt wurde übersprungen |
| `invalid` | Eingabe war ungültig |

### Ergebnisobjekt

`ContactPromptDraftFlowResult` enthält:

- Anzeige- und Kontextdaten
- gerenderte Vorschau (`ContactPromptUIRender`)
- geparstes Eingabemodell (`ContactPromptInputParseResult | None`)
- Sicherheits-/Nebenwirkungsflags (`preview_only`, `persisted`, `external_lookup_used`)
- Status und Ergebnisdetails (`selected_contact_type`, `skipped`, `error_message`)

## Verhalten

1. `prepare_contact_prompt_draft_flow(...)` ruft den In-Memory-Renderer auf.
2. Bei `should_render=False` bleibt der Flow `blocked`.
3. Bei `blocked` wird kein `raw_input` verarbeitet.
4. Bei erlaubtem Prompt wird `apply_contact_prompt_draft_input(...)` aufgerufen.
5. Parser-Auswertung:
   - `select_contact_type` → `status = selected`
   - `skip` → `status = skipped`
   - `invalid` → `status = invalid`

## Sicherheit/Privacy

- `preview_only = True`
- `persisted = False`
- `external_lookup_used = False`
- keine externen Aktionen
- Delete-Policy bleibt unverändert
  - `"ja"` löscht nicht
  - `"JA"` bleibt invalid
  - `" JA "` bleibt durch `strip()` erlaubt

## Getestete Module

- `test_contact_context_prompt_draft_flow.py`
- `test_contact_context_prompt_parse_readiness.py`
- `test_contact_context_prompt_input_parser.py`
- `test_contact_context_prompt_ui_renderer.py`
- `test_contact_context_prompt_preview_composition.py`
- `test_contact_context_prompt_candidate.py`
- `test_contact_context_preview.py`

## Empfehlung für Build Step 14M

- `14M — Contact Context Prompt Draft Flow Readiness Gate`

## Referenzen

- `friday/app/contact_context_prompt_draft_flow.py`
- `friday/tests/test_contact_context_prompt_draft_flow.py`
