# Approval Token Scanner

## Ziel

Lokaler Scanner fuer harte Friday-Approval-Tokens.

## Umfang

- liest lokale Python-Dateien
- nutzt AST
- sammelt String-Literale
- prueft erwartete harte Tokens
- erkennt weiche Bestaetigungen
- fuehrt keine Dateien aus
- importiert keine gescannten Module
- veraendert keine Dateien

## Erwartete Tokens

| Token | Zweck |
|---|---|
| `SPEICHERN` | Kontakt-Kontext speichern |
| `KONTAKT LÖSCHEN` | Kontakt-Kontext im bestehenden DB-Cleanup-Pfad loeschen |
| `PERSON VERGESSEN` | Forget Person im Kontakt-Menue ausfuehren |
| `OBSIDIAN SCHREIBEN` | Obsidian Write ausfuehren |
| `BACKUP ERSTELLEN` | lokales Backup erstellen |
| `RESTORE AUSFUEHREN` | lokale Restore-Kopie erstellen |
| `DATEN EXPORTIEREN` | lokalen Datenexport erstellen |
| `IMPORT ANWENDEN` | lokalen Import-Apply ausfuehren |
| `EXPORT AUFRAEUMEN` | lokale Exporte aufraeumen |
| `BACKUP AUFRAEUMEN` | lokale Backups aufraeumen |
| `RESTORE AUFRAEUMEN` | lokale Restore-Kopien aufraeumen |
| `REVIEW AUFRAEUMEN` | lokale Review-History aufraeumen |
| `COMMIT ERSTELLEN` | spaeteren lokalen Commit ausfuehren |

## Weiche Tokens

Beispiele:

- `ja`
- `yes`
- `ok`
- `speichern`
- `loeschen`
- `löschen`
- `schreiben`

## Delete-Policy-Kompatibilitaet

Die bestehende Delete-Policy bleibt separat.

`JA` darf im bestehenden Delete-Flow weiter existieren, soll aber keinen harten Write-Token ersetzen.

## Implementierte Bausteine

- `ApprovalTokenLiteral`
- `ApprovalTokenFinding`
- `ApprovalTokenScanResult`
- `scan_python_source_for_string_literals`
- `evaluate_approval_token_literals`
- `scan_python_file_for_approval_tokens`
- `scan_paths_for_approval_token_regressions`

## Safety

- keine Netzwerkaktionen
- keine Provideraufrufe
- keine Ausfuehrung gepruefter Dateien
- keine Produktlogik
- keine DB-Schreiboperation
- keine Obsidian-Schreiboperation

## Tests

- `test_approval_token_scanner.py`

## Empfehlung

Naechster sinnvoller Schritt:

Scanner Smoke Script.
