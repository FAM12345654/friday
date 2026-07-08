# Friday Post-399 System Consolidation Gate

## Ziel

Konsolidierung des Friday-Systemstands nach dem grossen lokalen Ausbau mit `399 passed`.

## Aktueller Teststand

- Full Regression: `399 passed`
- `python -m compileall friday`: erfolgreich
- `git diff --check`: sauber

## Fertige Hauptbloecke

| Block | Status | Hinweis |
|---|---|---|
| Contact Context Session Suppression | umgesetzt | lokal, in-memory |
| Contact Context Repository | umgesetzt | SQLite-basiert, Consent-/Safety-Regeln |
| Contact Context CLI | umgesetzt | Speichern/Löschen nur mit harten Tokens |
| Review Contact Integration | umgesetzt | lokal, keine externen Aktionen |
| Task Contact Snapshot | umgesetzt | lokaler Kontaktbezug in Aufgaben |
| Obsidian Note Preview | umgesetzt | Preview/Dry-Run |
| Obsidian Brain Preview | umgesetzt | Hauptmenuepunkt vorhanden |
| Obsidian Write Gate | umgesetzt | nur mit Vault, Flag und Token |
| Local Model Provider Foundation | umgesetzt | Mock/Preview/Validator/Logic-Check |
| Full Regression | gruen | `399 passed` |

## Safety-Status

Weiterhin nicht freigegeben:

- echte E-Mails
- echtes WhatsApp
- echte SMS
- echte Kalenderaktionen
- echtes Wetter
- echte Musik
- externe Provider
- Cloud-Aktionen
- externe Modellaufrufe
- automatischer Obsidian-Write
- automatische Speicherung sensibler Daten

## Harte Approval-Tokens

| Token | Zweck |
|---|---|
| `SPEICHERN` | Kontakt-Kontext lokal speichern |
| `KONTAKT LÖSCHEN` | Kontakt-Kontext löschen/vergessen |
| `OBSIDIAN SCHREIBEN` | Obsidian-Notiz schreiben, nur wenn Write-Flag aktiv ist |

## Kontakt-Kontext Status

Fertig:

- Session Suppression
- Repository
- CLI
- Review-Integration
- Task Snapshot

Noch offen:

- Dedupe
- Merge
- Audit
- Kontakt-Export
- Sensitive Guard
- Privacy Dashboard

## Obsidian Brain Status

Fertig:

- Note Preview
- Dry-Run
- Brain Preview Menuepunkt
- Write-Gate mit hartem Token

Noch offen:

- Dedupe gegen bestehende Notizen
- Contradiction Check
- Rollback
- Write-Audit
- Brain Curator
- Haupthirn-/Unterhirn-Struktur

## Local Model Status

Fertig:

- Provider Interface
- Mock Provider
- Ollama Preview Adapter
- Model Output Validator
- Logic Check Agent

Noch offen:

- echter lokaler Ollama-Call
- Produktanbindung
- Timeout/Retry-Hardening
- Prompt Templates
- Halluzinationsschutz gegen lokale Fakten

## Entscheidung

Friday ist nach `399 passed` deutlich weiter, aber weiterhin local-first und safety-gated.

Freigegeben:

- lokale Kontakt-Kontext-Funktionen
- lokale Review-/Task-Kontaktintegration
- Obsidian Preview und kontrollierter Write-Gate
- lokaler Modell-Unterbau ohne echte Modellaufrufe

Nicht freigegeben:

- externe Kommunikation
- Cloud Provider
- automatische Brain-Writes
- externe Modellaufrufe
- automatische Speicherung sensibler Daten
