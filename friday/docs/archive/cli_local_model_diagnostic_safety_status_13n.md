# Local Model Diagnostic Safety Status 13N

## Ziel
Kleiner lokaler Diagnosehinweis im bestehenden Sicherheitsstatus, ohne Produktfluss-Integration.

## Neue Statuszeilen
- `Lokaler Modell-Diagnosemodus: Mock/Preview`
- `Externe Modellaufrufe: False`
- `Produktfluss angebunden: False`

## Umfang
- Reine Anzeige im Menüpunkt `Sicherheitsstatus`.
- Keinerlei Produktlogik-Integration in Tasks, Nachrichten oder Review.
- Kein neuer Menüpunkt.
- Keine echten Modellaufrufe.
- Keine Provider-Aktivierung.
- Keine Netzwerkzugriffe.

## Bestätigte Safety-Bewertung
- Keine Ollama-/LiteLLM-/OpenAI-Aufrufe.
- Keine API-Keys.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Safety-Flags unverändert.
- Delete-Policy unverändert:
  - `"ja"` löscht nicht.
  - `"JA"` löscht.
  - `" JA "` bleibt durch `strip()` erlaubt.

## Tests
- `test_handle_menu_choice_safety_status` in `friday/tests/test_interface_main_menu_e2e.py`
- Komplettlauf: `python -m pytest friday/tests`

## Empfehlung für Build Step 13O
- Build Step 13O: Local Model Diagnostic Help Integration Planning
- planen, ob der Hilfetext einen kurzen Verweis auf den Diagnosemodus erhält.
