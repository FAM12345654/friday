# Backup Write Implementation Plan

## Ziel

Plan fuer die spaetere technische Umsetzung eines lokalen Backup Writes in Friday.

Dieser Step ist reine Planung. Es wird kein Backup geschrieben.

## Ausgangslage

Vorhanden:

- Backup / Restore Plan
- Backup Preview Model
- Backup Preview Readiness Gate
- Backup Write Plan
- Backup Write Guard / Model
- Backup Write Guard Readiness Gate
- Scanner Smoke Script

## Zentrale Implementierungsregel

Ein spaeterer Backup Write darf nur ausgefuehrt werden, wenn:

1. eine Backup Preview vorhanden ist,
2. der Backup Write Guard erlaubt,
3. der Zielpfad unter `local_data/backups/` liegt,
4. Scanner Smoke Script PASS ist,
5. Nutzer exakt `BACKUP ERSTELLEN` eingibt,
6. Secrets, `.env`, Caches und Obsidian Vault ausgeschlossen bleiben.

`BACKUP ERSTELLEN` ueberstimmt keine Excludes.

## Geplanter Write-Ablauf

```text
Backup Preview
-> Backup Write Guard
-> Scanner Smoke Check
-> Zielordner unter local_data/backups erstellen
-> manifest.json schreiben
-> README_BACKUP.md schreiben
-> erlaubte Sektionen kopieren
-> BackupWriteResult zurueckgeben
```

## Geplante Write-Sektionen

| Sektion | Geplantes Verhalten |
|---|---|
| `manifest.json` | aus Preview und Write-Ergebnis schreiben |
| `README_BACKUP.md` | lokalen Hinweistext schreiben |
| `database/` | lokale DB kopieren, falls Preview DB included meldet |
| `exports/` | lokale Exporte kopieren, falls Preview exports included meldet |
| `safety/` | Safety-Doku kopieren, falls Preview safety_docs included meldet |
| `docs_snapshot/` | optional ausgewaehlte Doku, spaeter eigenes Gate |
| `obsidian_vault/` | ausgeschlossen |
| `.env` / Secrets | ausgeschlossen |
| `.venv` / Caches | ausgeschlossen |

## Geplante Modelle

- `BackupWriteRequest`
- `BackupWriteResult`
- `BackupWrittenFile`

## Geplanter harter Token

```text
BACKUP ERSTELLEN
```

Nicht ausreichend:

- `ja`
- `JA`
- `ok`
- `yes`
- `speichern`
- `BACKUP`

## Geplante Blockierregeln

Backup Write muss blockieren, wenn:

- Preview fehlt,
- Backup Write Guard blockiert,
- Scanner Smoke Script nicht PASS ist,
- Zielpfad ausserhalb `local_data/backups/` liegt,
- Zielordner bereits existiert und keine spaetere Overwrite-Regel freigegeben ist,
- Secrets oder `.env` enthalten waeren,
- Obsidian Vault enthalten waere,
- Token falsch ist.

## Geplante Dateioperationen fuer spaeter

Erst in einem spaeteren Implementierungs-Step erlaubt:

- Zielordner unter `local_data/backups/` erstellen,
- Manifest schreiben,
- README_BACKUP schreiben,
- erlaubte lokale Dateien kopieren.

Weiterhin verboten:

- Dateien ausserhalb des Backup-Zielordners schreiben,
- ZIP erzeugen ohne eigenes Gate,
- Restore ausfuehren,
- Obsidian Vault kopieren,
- Secrets kopieren,
- externe Speicherziele verwenden.

## Spaetere Teststrategie

Ein spaeterer technischer Step sollte testen:

- korrekter Token schreibt lokales Backup unter `local_data/backups/`,
- falscher Token schreibt nichts,
- `ja` und `JA` schreiben nichts,
- Guard-Block schreibt nichts,
- Scanner Smoke FAIL schreibt nichts,
- Zielpfad ausserhalb wird blockiert,
- `.env` wird nicht kopiert,
- Secrets werden nicht kopiert,
- Obsidian Vault wird nicht kopiert,
- Manifest wird geschrieben,
- README_BACKUP wird geschrieben,
- vorhandener Zielordner wird nicht ueberschrieben,
- BackupWriteResult enthaelt Safe-Flags.

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

## Empfehlung

Naechster sinnvoller Build Step:

Backup Write Implementation.
