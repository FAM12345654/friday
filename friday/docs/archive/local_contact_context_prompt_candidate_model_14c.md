# Local Contact Context Prompt Candidate Model 14C

## Ziel

Dieses Dokument ergänzt den lokalen, technischen Schritt 14C mit einem In-Memory-Modell für mögliche Kontakt-Rückfragen.

14C definiert nur die Entscheidungslogik, ob Friday später nach lokaler Kontakt-Einordnung fragen darf.
Es gibt noch keine echte Nutzerabfrage, keine Persistenz und keine Flow-Integration.

## Umfang

- Reines Preview-/In-Memory-Modell
- Keine CLI-Integration
- Keine Message-/Review-/Task-Integration
- Keine Datenbank oder DB-Migration
- Keine externen Kontakte/Lookups/APIs
- Keine sensiblen Profilkategorien

## Implementierte Bausteine

- `ContactPromptCandidate` Dataclass
- `build_contact_prompt_question`
- `should_create_contact_prompt_candidate`
- `PromptStatus` / `ContactPromptReason` Typen
- `ALLOWED_SOURCE_CONTEXTS` / `DISALLOWED_SOURCE_CONTEXTS`

## Entscheidungslayer

Das Modell liefert einen Kandidaten mit folgenden Zuständen:

- `allowed`: Kontext erlaubt eine spätere Rückfrage
- `not_allowed`: Kontext oder Daten verhindern die Rückfrage
- `ask_later`: für spätere Erweiterung reserviert
- `skipped`: kürzlich übersprungen, daher aktuell nicht erneut fragen

## Entscheidungsregel

- `sensitive_or_disallowed=True` -> `not_allowed`, Grund `sensitive_or_disallowed`
- `recently_skipped=True` -> `skipped`, Grund `recently_skipped`
- Kontaktart bekannt (`contact_type` ungleich `"unbekannt"`) -> `not_allowed`, Grund `known_contact`
- Kontext nicht in erlaubten Kontexten oder explizit gesperrt -> `not_allowed`, Grund `no_active_context`
- erlaubte Kontexte mit unbekanntem Kontakt:
  - `nachrichten_review` -> `unknown_contact_in_review`
  - `person_bearbeiten` -> `explicit_person_edit`
  - `aufgabe_aus_nachricht` -> `task_from_unknown_sender`
  - `nutzeranfrage` -> `explicit_user_request`
  - → Status `allowed`

Erlaubte Kontexte:

- `nachrichten_review`
- `person_bearbeiten`
- `aufgabe_aus_nachricht`
- `nutzeranfrage`

Nicht erlaubte Kontexte:

- `app_start`
- `automatisch_jede_nachricht`
- `unklar`
- alle unbekannten Kontexte

## Safety-/Privacy

- Rein lokal
- keine Persistenz (`persisted=False`)
- keine externen Suchvorgänge (`external_lookup_used=False`)
- keine eigentliche Speicherung in Vorschau

## Tests

- `friday/tests/test_contact_context_prompt_candidate.py`
- Fokus auf reine Logik, keine DB-/Filesystem-/Network-Abhängigkeit

## Empfehlung für Build Step 14D

`14D` verbinden: Kandidat mit der lokalen Preview (`ContactContextPreview`) kombinieren,
ohne CLI-Abfrage und weiterhin ohne Persistenz.
