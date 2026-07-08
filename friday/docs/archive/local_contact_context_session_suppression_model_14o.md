# Local Contact Context Session Suppression Model 14O

## Ziel

Build Step 14O ergänzt ein reines In‑Memory-Modell für Session-basierte Unterdrückung von Kontakt-Prompt-Wiederholungen, ohne externe Abhängigkeiten oder Produktionsintegration.

## Implementierter Kern

- Neu: `friday/app/contact_context_session_suppression.py`
- Neue API:
  - `normalize_suppression_key(display_name, source_context) -> tuple[str, str]`
  - `mark_contact_prompt_skipped(display_name, source_context, entries) -> tuple[...]`
  - `is_contact_prompt_suppressed(display_name, source_context, entries) -> bool`
  - `clear_contact_prompt_suppression(display_name, source_context, entries) -> tuple[...]`

## Regeln / Verhalten

- Kein globaler Zustand.
- Kein Persistenz- oder Datenbankzugriff.
- Rückgabe immer als neues Immutable-Tuple (`tuple[ContactPromptSuppressionEntry, ...]`).
- `mark_contact_prompt_skipped` ersetzt bestehenden Sitzungseintrag für dieselbe `(name, context)`-Kombination.
- `is_contact_prompt_suppressed` ist `True` bei `skipped` und `suppressed`.
- `clear_contact_prompt_suppression` entfernt nur den exakten Satz für den Name/Context-Key.

## Testabdeckung

- Neu: `friday/tests/test_contact_context_session_suppression.py`
- Abgedeckt: Skip-Marker, Kontextabgrenzung, Personenabgrenzung, Replace-Verhalten, Löschverhalten.

## Sicherheit

- Keine externen Aktionen.
- Keine DB-/Dateioperation.
- `preview_only=True`, `persisted=False`, `external_lookup_used=False` in neuen Einträgen.

## Nächster Schritt

14P — Session Suppression Readiness Gate
