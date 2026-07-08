# Restore Write Implementation Plan

## Ziel

Plan fuer eine spaetere technische Restore Write Implementation.

Dieser Schritt baut keinen Restore. Er beschreibt nur, wie ein echter lokaler Restore spaeter umgesetzt werden duerfte, ohne aktive Daten still zu ueberschreiben.

## Ausgangslage

Bereits umgesetzt:

- Restore Dry-Run Model
- Restore Dry-Run Readiness Gate
- Restore Write Plan
- Restore Write Guard Model
- Restore Write Guard Readiness Gate
- Backup / Restore CLI Readiness Gate

Noch nicht umgesetzt:

- Restore Write Implementation
- Restore Write CLI Approval
- Restore Write Readiness Gate
- Restore Rollback oder Sicherheitskopie

## Implementierungsprinzip

Ein Restore Write darf spaeter nur als kontrollierter lokaler Copy-Back gebaut werden.

Er darf niemals:

- aktive SQLite-Datenbank direkt ueberschreiben.
- ohne Dry-Run laufen.
- ohne Restore Write Guard laufen.
- ohne harten Token laufen.
- externe Pfade lesen oder schreiben.
- ZIP-Dateien automatisch entpacken.
- Obsidian Vault wiederherstellen.
- Secrets wiederherstellen.

## Geplanter Ablauf

1. Nutzer waehlt Backup-Ordner.
2. Restore Dry-Run wird ausgefuehrt.
3. Restore Write Guard prueft:
   - Dry-Run erlaubt,
   - Backup unter `local_data/backups/`,
   - keine verbotenen Inhalte,
   - kein aktiver DB-Konflikt,
   - Token `RESTORE AUSFUEHREN`.
4. Restore Write baut eine Ziel-Vorschau.
5. Restore Write kopiert nur erlaubte Sektionen.
6. Ergebnis dokumentiert geschriebene Dateien.

## Geplante Zielpfade

| Backup-Sektion | Spaeterer Zielpfad | Standard |
|---|---|---|
| `exports/` | `local_data/restored_exports/<timestamp>/` | erlaubt nach Guard |
| `database/` | `local_data/restored_database/<timestamp>/` | nur als Kopie, nicht aktive DB |
| `safety/` | `local_data/restored_safety_docs/<timestamp>/` | optional |

Wichtig:

Die aktive Datenbank unter `local_data/friday.db` oder `local_data/friday.sqlite` darf durch diesen Restore Write nicht ersetzt werden.

## Geplante Modelle

### RestoreWrittenFile

- `relative_path`
- `source_path`
- `bytes_written`

### RestoreWriteResult

- `allowed`
- `persisted`
- `target_root`
- `written_files`
- `blocked_reasons`
- `warnings`
- `message`
- `preview_only`
- `external_lookup_used`

## Geplante Blockierfaelle

| Fall | Verhalten |
|---|---|
| fehlender Guard | blockieren |
| Guard nicht erlaubt | blockieren |
| falscher Token | blockieren durch Guard |
| aktiver DB-Konflikt | blockieren durch Guard |
| Zielordner existiert bereits | blockieren, nicht ueberschreiben |
| Backup-Sektion fehlt | warnen oder blockieren |
| `.env` / Secrets | blockieren |
| Obsidian Vault | blockieren |

## Erlaubte Schreibstrategie

Wenn spaeter implementiert, darf der Restore Write nur neue Zielordner anlegen:

```text
local_data/restores/friday_restore_<timestamp>/
```

Darunter koennen Unterordner liegen:

```text
database/
exports/
safety/
RESTORE_MANIFEST.json
README_RESTORE.md
```

Dieser Ansatz stellt Daten bereit, ohne sie aktiv in Friday zu ersetzen.

## Nicht-Ziele

Dieser Plan erlaubt nicht:

- automatisches Aktivieren einer wiederhergestellten Datenbank.
- direktes Ersetzen von `friday.db`.
- Restore in Obsidian Vaults.
- Restore aus Cloud.
- Restore aus ZIP.
- Restore ohne Token.
- Restore ohne Guard.
- externe Provider.

## Vorgeschlagene Tests fuer spaetere Umsetzung

- falscher Token schreibt nichts.
- fehlender Guard schreibt nichts.
- Guard blockiert, Write schreibt nichts.
- Zielordner existiert bereits, Write schreibt nichts.
- `RESTORE AUSFUEHREN` schreibt nur in neuen Restore-Zielordner.
- aktive Datenbank wird nicht ersetzt.
- Exporte werden nur in Restore-Zielordner kopiert.
- Secrets und Obsidian Vault werden nicht kopiert.
- Ergebnis enthaelt `RestoreWrittenFile`.
- `preview_only=False` nur bei tatsaechlichem Restore-Zielordner-Write.
- keine externen Aktionen.

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

Restore Write Implementation.
