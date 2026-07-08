# CLI Product Roadmap Gate 13S

## Ziel

Übergreifendes Roadmap- und Finalization-Gate nach den lokalen CLI-, Export-, Kontakt-Kontext-, Obsidian-Preview- und Modell-Diagnoseblöcken.

## Stabilisierte produktive Bereiche

| Bereich | Status | Hinweise |
|---|---|---|
| Hauptmenü / Run-Loop | stabil | E2E-getestet |
| Aufgabenmenü | stabil | inklusive Quick Add und Export |
| Task Create/Edit/Search/Done/Archive/Delete | stabil | lokale SQLite-Flows |
| Review Nachrichten-Vorschläge | stabil | lokal, keine echten Nachrichten |
| Review Aufgaben-Vorschläge | stabil | lokale Task-Erzeugung |
| Kalender-Slot-Auswahl | stabil | nur Entwurfstext, kein echter Termin |
| Help / Übersicht | stabil | lokale Safety-Hinweise |
| Onboarding-Hinweis | stabil | lokale Startorientierung |
| Markdown Export | stabil | lokaler Export unter `local_data/exports/` |
| Lokale Modell-Diagnose | stabil (mock-only) | keine echten Modellaufrufe |

## Geplante, noch nicht implementierte Bereiche

| Bereich | Status | Dokument |
|---|---|---|
| Kontakt-Kontext | geplant | [local_contact_context_plan_13e.md](local_contact_context_plan_13e.md) |
| Obsidian Brain Preview | geplant | [obsidian_brain_preview_plan_13f.md](obsidian_brain_preview_plan_13f.md) |
| echte lokale Modellintegration | nicht freigegeben | nur Mock/Preview vorhanden |
| Review Batch Actions | offen | noch nicht umgesetzt |
| Task Tages-/Wochenplanung | offen | noch nicht umgesetzt |

## Nicht freigegeben

- Echte E-Mail-/WhatsApp-/SMS-Aktionen.
- Echte Kalendertermine.
- Externe Provider.
- OpenAI/Ollama/LiteLLM-Live-Aufrufe.
- Netzwerkaktionen.
- API-Keys.
- Obsidian-Write.
- Kontaktimport.
- Freie Exportpfade.
- Automatische Modellnutzung in Task/Message/Review.

## Teststatus

- Main Menu E2E: 32 passed
- Lokalmodell-Mock/Preview: 8 passed
- Markdown Export Tests: `python -m pytest friday/tests/test_task_markdown_export.py`
- Full Regression: 256 passed
- `python -m compileall friday`: erfolgreich
- `git diff --check`: sauber

## Safety-Status

- Local-only.
- Safety-Flags unverändert.
- Delete-Policy unverändert.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine echten Modellaufrufe.
- Kein Obsidian-Write.
- Keine Datenbankschema-Änderung.

## Nächste mögliche Implementierungsblöcke

| Option | Nutzen | Risiko | Empfehlung |
|---|---|---|---|
| Contact Context Preview Model | hoch | mittel | empfohlen |
| Obsidian Brain Preview Payload | hoch | mittel | danach |
| Review Batch Actions | mittel | mittel bis hoch | später |
| Task Tagesplanung | mittel | mittel | später |
| echte lokale Modellintegration | hoch | hoch | erst nach weiteren Gates |

## Empfehlung

Nächster größerer Schritt: **Build Step 14A — Contact Context Preview Model**.

Warum:

- Kontakt-Kontext bildet eine Grundlage für bessere Nachrichten-, Aufgaben- und Review-Kontexte.
- Kann initial als Preview/In-Memory umgesetzt werden.
- Ohne Datenbankschema-Änderung realisierbar.
- Kompatibel mit der bestehenden lokalen Security- und Approval-Strategie.

## Empfehlung für Build Step 14A

- In-Memory-/Preview-Struktur ohne DB-Migration.
- Keine externen Kontakte.
- Keine WhatsApp-/E-Mail-Anbindung.
- Keine Modell-Live-Nutzung.
- Tests mit lokalen Beispieldaten.
- Safety-/Privacy-Grenzen beibehalten.

## Verweise

- [cli_task_markdown_export_docs_13d.md](cli_task_markdown_export_docs_13d.md)
- [local_contact_context_plan_13e.md](local_contact_context_plan_13e.md)
- [obsidian_brain_preview_plan_13f.md](obsidian_brain_preview_plan_13f.md)
- [cli_local_model_diagnostic_finalization_gate_13r.md](cli_local_model_diagnostic_finalization_gate_13r.md)
- [cli_docs_finalization_gate_12n.md](cli_docs_finalization_gate_12n.md)
