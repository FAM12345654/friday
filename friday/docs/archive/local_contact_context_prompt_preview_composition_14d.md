# Local Contact Context Prompt Preview Composition 14D

## Ziel

Dieser Schritt verbindet `ContactContextPreview` und `ContactPromptCandidate` zu einer gemeinsamen lokalen Vorschau-Struktur.

Es findet weiterhin **keine echte CLI-Abfrage** statt. Die Composition bleibt rein in-memory und dient als sicherer Zwischenlayer für spätere, kontrollierte UI-/Planungsentscheidungen.

## Umfang

- Reine Preview-Composition für Kontakt-Entscheidungen
- Keine CLI-Abfrage
- Keine Datenbank oder Persistenz
- Keine Message-/Review-/Task-Integration
- Keine externen Kontakte/Lookups
- Keine externen APIs

## Implementierte Bausteine

- `ContactPromptPreview` Dataclass
- `DEFAULT_CONTACT_TYPE_OPTIONS`
- `build_contact_prompt_preview`

## Verhalten

- Erzeugt zuerst eine Kandidaten-Entscheidung via `should_create_contact_prompt_candidate`.
- Erzeugt parallel `ContactContextPreview`.
- Setzt:
  - `should_ask == True` nur bei `status == "allowed"`.
  - `should_ask == False` bei allen Sperrfällen.
- Liefert Standard-Optionsliste für spätere UI-Pfade.
- Hält ausschließlich lokale Flags (`preview_only=True`, `persisted=False`, `external_lookup_used=False`).

## Safety-/Privacy

- Keine echte Nutzerabfrage.
- Keine Persistenz.
- Keine externen Lookups.
- Keine Netzwerk- oder API-Nutzung.
- Keine externen Kontakte.
- Keine neuen DB-Flows.

## Tests

- `friday/tests/test_contact_context_prompt_preview_composition.py`
- Schwerpunkte:
  - allowed vs. blocked
  - known contact / skipped / sensitive_or_disallowed
  - optionale Kontextfelder
  - sichere Flags
  - Disallow durch ungültigen Kontext

## Empfehlung für Build Step 14E

`14E` als Readiness-Gate ergänzen:

- Alle drei Kontaktebene-Modelle (`14A`, `14C`, `14D`) vollständig isoliert prüfen.
- Keine CLI- oder Flow-Integration in 14E.
- Kein DB-/Persistenz-Zugriff.
