# Restore Write Readiness Gate

## Ziel

Readiness-/Safety-Gate fuer die Restore Write Implementation.

Der Restore Writer kopiert erlaubte Backup-Sektionen nur in einen separaten Restore-Zielordner und ersetzt niemals die aktive Friday-Datenbank.

## Gepruefte Bausteine

| Baustein | Status | Hinweis |
|---|---|---|
| `RestoreWrittenFile` | umgesetzt | beschreibt kopierte Restore-Datei |
| `RestoreWriteResult` | umgesetzt | beschreibt Restore-Copy-Ergebnis |
| `write_local_restore_copy(...)` | umgesetzt | schreibt nur in separaten Restore-Zielordner |
| Restore Write Guard | umgesetzt | prueft Dry-Run, Token, Pfade und Konflikte |
| Restore Writer Tests | umgesetzt | blockierende und erfolgreiche Pfade abgedeckt |

## Gepruefte Safety-Regeln

| Regel | Ergebnis |
|---|---|
| falscher Token schreibt nichts | geprueft |
| fehlender Dry-Run schreibt nichts | geprueft |
| Guard-Block schreibt nichts | geprueft |
| aktiver DB-Konflikt schreibt nichts | geprueft |
| Zielordner existiert bereits | blockiert |
| `.env` / Secrets im Backup | blockiert |
| aktive DB wird nicht ersetzt | geprueft |
| Restore schreibt nur unter `local_data/restores/` | geprueft |

## Freigegeben

- Restore Copy als importierbarer lokaler Baustein.
- Kopieren erlaubter Backup-Sektionen in:

```text
local_data/restores/friday_restore_<timestamp>/
```

- Schreiben von:
  - `RESTORE_MANIFEST.json`
  - `README_RESTORE.md`
  - erlaubten Backup-Sektionen in separaten Restore-Unterordnern

## Nicht freigegeben

- CLI-Restore-Write.
- automatischer Restore.
- Ersetzen der aktiven SQLite-Datenbank.
- Zurueckkopieren in aktive Projektpfade.
- Restore aus ZIP-Dateien.
- Obsidian Vault Restore.
- Secrets Restore.
- externe Speicherorte.
- Netzwerkaktionen.
- Provider-/Modellaufrufe.

## Teststatus

- Restore-/Backup-Fokus: 39 passed
- Full Regression: 552 passed
- compileall: erfolgreich
- Scanner Smoke Script: PASS
- git diff --check: sauber

## Safety-Bewertung

- Restore Write ist hart gegatet.
- Restore Write ersetzt keine aktive Datenbank.
- Restore Write schreibt nur in separaten Zielordner.
- Keine CLI-Integration.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Kein Netzwerk.
- Keine Provider.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Entscheidung

Die Restore Write Implementation ist als lokaler Copy-Baustein freigegeben.

Nicht freigegeben bleibt die CLI-Anbindung fuer Restore Write. Dafuer braucht Friday einen separaten Plan, Tests und ein eigenes Approval-Gate.

## Empfehlung

Naechster sinnvoller Build Step:

Restore Write CLI Approval Plan.
