# Backup Write Plan

## Ziel

Plan fuer einen spaeteren lokalen Backup Write in Friday.

Dieser Step ist reine Planung. Es wird kein Backup geschrieben.

## Ausgangslage

Vorhanden:

- Backup / Restore Plan
- Backup Preview Model
- Backup Preview Readiness Gate
- Scanner Smoke Script

## Zentrale Write-Regel

Ein Backup Write darf spaeter nur erfolgen, wenn:

1. Backup Preview vorhanden ist.
2. Zielpfad unter `local_data/backups/` liegt.
3. Secrets ausgeschlossen sind.
4. `.env` ausgeschlossen ist.
5. Obsidian Vault nicht automatisch enthalten ist.
6. Scanner Smoke Script PASS ist.
7. Nutzer exakt `BACKUP ERSTELLEN` eingibt.

`BACKUP ERSTELLEN` ueberstimmt keine Excludes.

## Geplanter Backup-Zielpfad

```text
local_data/backups/friday_backup_<YYYYMMDD_HHMMSS>/
```

## Geplante Struktur

```text
friday_backup_<timestamp>/
├── manifest.json
├── README_BACKUP.md
├── database/
├── exports/
├── safety/
└── docs_snapshot/
```

## Geplante Write-Sektionen

| Sektion | Verhalten |
|---|---|
| `manifest.json` | schreiben |
| `README_BACKUP.md` | schreiben |
| `database/` | lokale DB-Kopie, falls vorhanden |
| `exports/` | lokale Exporte kopieren, falls vorhanden |
| `safety/` | Safety-Doku kopieren |
| `docs_snapshot/` | optional ausgewaehlte Doku |
| `obsidian_vault/` | ausgeschlossen |
| `.env` / Secrets | ausgeschlossen |
| `.venv` / Caches | ausgeschlossen |

## Approval Token

Geplanter harter Token:

`BACKUP ERSTELLEN`

Nicht ausreichend:

- `ja`
- `JA`
- `ok`
- `yes`
- `speichern`

## Blockierregeln

Backup Write muss blockieren, wenn:

- Preview fehlt.
- Zielpfad ausserhalb `local_data/backups/` liegt.
- Scanner Smoke Script nicht PASS ist.
- Secrets enthalten waeren.
- `.env` enthalten waere.
- Obsidian Vault enthalten waere.
- Token falsch ist.

## Nicht-Ziele

- Keine Implementierung in diesem Step.
- Kein Backup Write.
- Kein Restore.
- Keine Datei kopieren.
- Keine Datei schreiben.
- Keine ZIP-Datei.
- Keine DB-Kopie.
- Kein Obsidian-Vault-Backup.
- Kein Netzwerk.
- Keine Cloud.

## Spaetere Teststrategie

Ein spaeterer technischer Step sollte testen:

- korrekter Token erlaubt lokalen Backup Write.
- falscher Token blockiert.
- `ja` und `JA` blockieren.
- Zielpfad ausserhalb wird blockiert.
- `.env` wird nicht kopiert.
- Secrets werden nicht kopiert.
- Obsidian Vault wird nicht kopiert.
- Scanner Smoke FAIL blockiert.
- Manifest wird geschrieben.
- README_BACKUP wird geschrieben.
- Backup bleibt lokal.

## Empfehlung

Naechster technischer Schritt:

Backup Write Guard / Backup Write Model.
