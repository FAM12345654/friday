# Restore Write Plan

## Ziel

Plan fuer einen spaeteren echten lokalen Restore Write.

Dieser Schritt implementiert keinen Restore. Er definiert nur die Sicherheitsregeln, die vor einem spaeteren Restore Write zwingend erfuellt sein muessen.

## Ausgangslage

Bereits umgesetzt:

- Backup Preview Model
- Backup Write Guard / Model
- Backup Write Implementation
- Backup / Restore CLI Readiness Gate
- Restore Dry-Run Model
- Restore Dry-Run Readiness Gate

Noch nicht umgesetzt:

- Restore Write Guard
- Restore Write Implementation
- Restore CLI Approval
- Restore-Konfliktstrategie
- Restore-Rollback-Strategie

## Grundsatz

Ein Restore ist riskanter als ein Backup.

Deshalb darf ein spaeterer Restore Write niemals direkt nach Auswahl eines Backup-Ordners laufen. Vor jedem Restore Write braucht Friday:

1. Restore Dry-Run PASS.
2. Backup-Pfad unter `local_data/backups/`.
3. Gueltiges `manifest.json`.
4. Keine Secrets im Backup.
5. Keine Obsidian-Vault-Inhalte im Backup.
6. Konfliktpruefung fuer aktive Daten.
7. harte Nutzerbestaetigung.
8. eigenes Readiness Gate.

## Geplanter harter Token

Ein spaeterer Restore Write darf nur mit exakt diesem Token laufen:

```text
RESTORE AUSFUEHREN
```

Nicht erlaubte Tokens:

- `JA`
- `ja`
- `ok`
- `yes`
- `SPEICHERN`
- `BACKUP ERSTELLEN`
- leere Eingabe

## Geplante Restore-Sektionen

| Sektion | Standardentscheidung | Bedingung |
|---|---|---|
| `database/` | blockiert bis eigenes Gate | aktive DB darf nicht direkt ueberschrieben werden |
| `exports/` | moeglich als Copy-Back | nur nach Konfliktpruefung |
| `safety/` | read-only Referenz | nicht automatisch zurueckkopieren |
| `manifest.json` | lesen | nie als Ziel schreiben |
| `README_BACKUP.md` | lesen | nie als Ziel schreiben |

## Konfliktstrategie

Ein Restore Write darf spaeter keine vorhandenen Dateien still ueberschreiben.

Geplante Optionen:

| Konflikt | Verhalten |
|---|---|
| aktive `friday.db` existiert | blockieren oder vorher Sicherheitskopie verlangen |
| Export-Datei existiert | blockieren oder neuen Namen mit Restore-Zeitstempel verwenden |
| Zielordner fehlt | darf angelegt werden, wenn innerhalb erlaubtem Pfad |
| Backup-Sektion fehlt | blockieren oder Warnung, je nach Sektion |

## Geplantes Sicherheitsmodell

Vor einem Restore Write sollte ein Restore Write Guard pruefen:

- Restore Dry-Run Result ist erlaubt.
- Backup Root liegt unter `local_data/backups/`.
- Zielpfade liegen innerhalb des lokalen Friday-Projekts.
- keine `.env`.
- keine Secrets.
- kein Obsidian Vault.
- kein Netzwerk.
- kein externer Speicherort.
- kein direkter Datenbank-Overwrite ohne eigenes Gate.
- Token ist exakt `RESTORE AUSFUEHREN`.

## Nicht-Ziele

Dieser Plan erlaubt nicht:

- Restore Write.
- CLI-Restore-Write.
- Ueberschreiben der aktiven SQLite-Datenbank.
- automatischen Restore.
- Restore aus ZIP-Dateien.
- Restore aus Cloud/Netzwerk.
- Obsidian Vault Restore.
- Secrets Restore.
- externe Provider.

## Vorgeschlagene Tests fuer spaetere Umsetzung

Spaetere Tests sollten abdecken:

- Restore Write Guard blockiert ohne Dry-Run PASS.
- Restore Write Guard blockiert falschen Token.
- `JA` und `ja` blockieren.
- `BACKUP ERSTELLEN` blockiert fuer Restore.
- exakter Token `RESTORE AUSFUEHREN` ist notwendig.
- Backup ausserhalb `local_data/backups/` blockiert.
- `.env` im Backup blockiert.
- `secrets` im Backup blockiert.
- Obsidian Vault im Backup blockiert.
- aktive DB wird nicht still ueberschrieben.
- Restore Write erzeugt keine externen Aktionen.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Implementierung gebaut.
- Keine Tests geaendert.
- Kein Restore ausgefuehrt.
- Keine Daten ueberschrieben.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine Netzwerkaktionen.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Restore Write Guard Model.
