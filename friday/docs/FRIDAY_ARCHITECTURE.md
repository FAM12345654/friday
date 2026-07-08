# Friday Architecture

## Ziel

Aktuelle lokale Systemarchitektur von Friday nach dem Post-399-Ausbau.

## Hauptbereiche

| Bereich | Zweck |
|---|---|
| CLI Interface | lokale Bedienung |
| Task System | lokale Aufgaben |
| Review System | lokale Vorschlaege |
| Contact Context | Personen-/Kontaktkontext |
| Obsidian Brain | lokale Wissensvorschau und gated Write |
| Local Model Foundation | Mock/Preview/Validator/Logic-Check |
| Self-Building Preview | Build Queue, Test Runner Allowlist, Git Viewer und Commit Draft ohne Ausfuehrung |
| Safety Layer | Flags, Tokens, Gates |
| Release Gates | lokale MVP-Freigabe ueber Tests, Compilecheck, Safety Smoke und Doku |

## Runtime Boundaries

- Produktlogik im lokalen MVP bleibt Python-only.
- Persistenz im lokalen MVP bleibt SQLite ueber die Python-Standardbibliothek `sqlite3`.
- Keine Cloud-Datenbank, kein ORM und kein externer Datenbankserver sind Teil des lokalen MVP.
- Keine externen Modell-, Provider- oder Netzwerkaktionen sind Teil der lokalen Release-Freigabe.
- Mobile-Live-, EAS-/Expo- und Cloudflare-Publish-Flows liegen ausserhalb dieses lokalen MVP-Gates.

## Datenfluss Contact Context

```text
Nachricht / Nutzerkontext
-> Contact Candidate
-> Prompt Preview
-> UI Renderer
-> Input Parser
-> Draft Flow
-> Save Approval
-> Contact Repository
```

## Datenfluss Obsidian

```text
Task / Contact
-> Note Preview
-> Sensitive Guard
-> Path Safety
-> Dry Run
-> Write Gate
-> Token OBSIDIAN SCHREIBEN
-> Vault Write
```

## Datenfluss Local Model

```text
Provider Interface
-> Mock / Preview Adapter
-> Output Validator
-> Logic Check Agent
-> noch keine Produktanbindung
```

## Datenfluss Self-Building Preview

```text
Build Step Idee
-> Build Queue Preview
-> Test Runner Allowlist Preview
-> Git Status Viewer Preview
-> Commit Draft Preview
-> Token COMMIT ERSTELLEN als spaeteres Gate
-> keine Ausfuehrung im MVP
```

## Lokales MVP Release Gate

```text
Obsidian Brain Finalization Gate
-> Local AI Finalization Gate
-> Self-Building Finalization Gate
-> Full Regression
-> Compilecheck
-> Safety Smoke
-> git diff --check
-> FRIDAY_LOCAL_MVP_RELEASE_GATE
```

## Geplanter Datenfluss Backup

```text
Local Data
-> Backup Preview
-> Scanner Smoke Check
-> Write Guard
-> Token BACKUP ERSTELLEN
-> Local Backup Write
```

## Geplanter Datenfluss Backup Write Implementation

```text
Backup Preview
-> Backup Write Guard
-> Scanner Smoke Check
-> Zielpfad local_data/backups
-> Manifest schreiben
-> README_BACKUP schreiben
-> erlaubte lokale Sektionen kopieren
-> BackupWriteResult
```

## Vorheriger Backup-Planungsfluss

```text
Local Data
-> Backup Preview
-> Manifest
-> Safety Check
-> Hard Token
-> Local Backup Write
```

## Geplanter Datenfluss Restore

```text
Backup Folder
-> Manifest Validation
-> Restore Dry Run
-> Safety Check
-> Hard Token
-> Local Restore
```

## Nicht freigegebene Datenfluesse

- externe Kommunikation
- Cloud-Provider
- externe Modellaufrufe
- automatischer Obsidian-Write
- Local-AI Live-Calls im Produktfluss
- Self-Building Runner-Ausfuehrung ohne eigenes Gate
- Git-Mutationen ohne eigenes Gate und harten Token
- automatische Speicherung sensibler Daten
