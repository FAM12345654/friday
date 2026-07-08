# Friday Data Models

## Ziel

Uebersicht ueber zentrale lokale Datenmodelle.

## Contact Context

Wichtige Modelle:

- ContactContextPreview
- ContactPromptCandidate
- ContactPromptPreview
- ContactPromptUIRender
- ContactPromptInputParseResult
- ContactPromptDraftFlowResult
- Contact Context Repository Records
- Session Suppression Entries

Freitextfelder wie `relationship_context` oder `notes` muessen vor Speicherung durch den Sensitive Contact Context Guard erlaubt werden.

## Forget Person

Wichtige Modelle:

- ForgetPersonPreview
- ForgetPersonPreviewContact
- ForgetPersonWriteGuardResult
- ForgetPersonWriteResult

`ForgetPersonPreview` oeffnet eine vorhandene SQLite-Datenbank nur read-only und sucht passende lokale Kontakt-Kontexte per `contact_id` oder normalisiertem Anzeigenamen.

Der Write-Flow bleibt auf `contact_contexts` beschraenkt:

- kein Obsidian-Write,
- keine externen Aktionen,
- keine Schema-Aenderung,
- kein Write ohne lokales Backup,
- kein Write ohne Safety Smoke PASS,
- kein Write ohne exakt `PERSON VERGESSEN`,
- Transaktion und Rollback bei Candidate-Count-Mismatch.

## Tasks

Wichtige Modelle:

- lokale Aufgaben
- Task Contact Snapshot
- Markdown Export Payload

### Tasks SQLite

Die Tabelle `tasks` enthaelt jetzt optional:

- `recurrence TEXT`

Erlaubte Werte:

- `NULL` fuer keine Wiederholung,
- `taeglich`,
- `woechentlich`,
- `monatlich`.

Die Spalte ist additiv und nullable. Beim Erledigen einer wiederkehrenden Aufgabe wird lokal genau eine neue offene Folgeaufgabe mit fortgeschriebenem Fälligkeitsdatum erzeugt. Loeschen und Archivieren erzeugen keine Folgeaufgabe.

## Review

Wichtige Modelle:

- lokale Nachrichten-Vorschlaege
- lokale Aufgaben-Vorschlaege
- Contact Context Draft im Review

## Privacy Dashboard

Wichtige Modelle:

- PrivacyDashboardSummary
- PrivacyDashboardLocalCounts
- PrivacyDataArea
- PrivacySafetyFlag
- PrivacyExternalAction
- PrivacyGatedAction

`PrivacyDashboardLocalCounts` ist eine read-only Sicht auf vorhandene lokale Daten.
Sie zaehlt vorhandene SQLite-Tabellen und lokale Backup-/Restore-Ordner, erzeugt aber keine Datenbank, keine Ordner und kein Schema.

## Obsidian

Wichtige Modelle:

- Obsidian Note Preview
- Obsidian Brain Preview
- Obsidian Write Candidate
- Obsidian Dry-Run Result
- Obsidian Brain Finalization Gate

## Local Model

Wichtige Modelle:

- LocalModelProvider
- Mock Provider Result
- Ollama Preview Result
- OllamaHealthResult
- OllamaGenerationResult
- Model Output Validation Result
- Logic Check Result
- Local AI Finalization Gate

## Self-Building Preview

Wichtige Modelle:

- BuildQueueItem
- BuildQueuePreview
- TestRunnerPreview
- GitStatusViewerPreview
- CommitDraft
- CommitApprovalPreview
- SelfBuildingFinalizationGate

Diese Modelle bleiben preview-only.
Sie fuehren keine Testkommandos aus, rufen kein Git auf, erstellen keinen Commit und schreiben keine Daten.

## Release Gates

Wichtige Dokumentationsmodelle:

- Obsidian Brain Finalization Gate
- Local AI Finalization Gate
- Self-Building Finalization Gate
- Friday Local MVP Release Gate

Release-Gates sind lokale Freigabe-Dokumente.
Sie aendern kein Datenbankschema, schreiben keine Runtime-Daten und aktivieren keine externen Aktionen.

Gemeinsamer Gate-Contract:

- `preview_only=True` fuer reine Vorschau-/Gate-Modelle,
- `persisted=False`, solange kein eigenes Write-Gate erfolgreich durchlaufen wurde,
- `external_lookup_used=False` im lokalen MVP,
- `blocked_reasons` oder `blocked_actions` fuer nicht freigegebene Pfade,
- `required_token` oder `approval_token_required` fuer spaetere harte Freigaben.

## Backup / Restore

Modelle:

- BackupManifest
- BackupPreview
- BackupWriteResult
- RestoreDryRunResult
- Backup/Restore Forbidden Path Policy

### BackupPreview

- `project_root`
- `planned_backup_root`
- `sections`
- `manifest_preview`
- `preview_only`
- `persisted`
- `external_lookup_used`

### BackupPreviewSection

- `name`
- `status`
- `path`
- `reason`
- `file_count`

### Backup Write

Geplante Modelle:

- BackupWritePlan
- BackupWriteGuardResult
- BackupWriteResult

### BackupWriteGuardResult

- `allowed`
- `planned_backup_root`
- `blocked_reasons`
- `message`
- `checked_sections`
- `excluded_sections`
- `preview_only`
- `persisted`
- `external_lookup_used`

### Backup Write Implementation

Geplante Modelle:

- BackupWriteRequest
- BackupWriteResult
- BackupWrittenFile

### BackupWriteResult

- `allowed`
- `persisted`
- `target_path`
- `written_files`
- `blocked_reasons`
- `message`
- `preview_only`
- `external_lookup_used`

### BackupWrittenFile

- `relative_path`
- `source_path`
- `bytes_written`

### Backup/Restore Forbidden Path Policy

`is_forbidden_backup_restore_path(...)` ist ein gemeinsamer lokaler Safety-Check fuer Backup Write und Restore Dry-Run.
Er blockiert oder ueberspringt:

- `.env` und `.env.*`,
- Secrets,
- Tokens,
- API-Keys,
- Credentials,
- Private Keys,
- Passwoerter,
- `.obsidian`,
- Obsidian-Vault-Varianten,
- Symlink-/Junction-Kandidaten,
- Pfade, die per `resolve()` ausserhalb des erwarteten lokalen Roots liegen.

Der Check schreibt nichts, aendert kein Schema und fuehrt keine externen Aktionen aus.
Backup Writer und Restore Writer validieren Quellen erneut, damit gefaelschte Preview- oder Dry-Run-Objekte keine externen Dateien kopieren.

### Restore Dry-Run

Modelle:

- RestoreDryRunResult
- RestoreDryRunSection

### RestoreDryRunResult

- `allowed`
- `backup_root`
- `manifest_found`
- `manifest_valid`
- `sections_checked`
- `missing_sections`
- `blocked_reasons`
- `warnings`
- `message`
- `preview_only`
- `persisted`
- `external_lookup_used`

### RestoreDryRunSection

- `name`
- `status`
- `path`
- `file_count`
- `message`

### Restore Write

Geplante Modelle:

- RestoreWriteGuardResult
- RestoreWritePlan
- RestoreWriteResult

### RestoreWriteGuardResult

- `allowed`
- `backup_root`
- `target_root`
- `blocked_reasons`
- `warnings`
- `message`
- `preview_only`
- `persisted`
- `external_lookup_used`

### RestoreWriteResult

Felder:

- `allowed`
- `persisted`
- `target_root`
- `written_files`
- `blocked_reasons`
- `warnings`
- `message`
- `preview_only`
- `external_lookup_used`

### RestoreWrittenFile

Felder:

- `relative_path`
- `source_path`
- `bytes_written`
