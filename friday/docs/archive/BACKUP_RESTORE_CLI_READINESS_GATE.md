# Backup / Restore CLI Readiness Gate

## Ziel

Readiness-/Safety-Gate fuer den lokalen Backup-/Restore-CLI-Block.

Der CLI-Bereich kann Backup Preview anzeigen, lokale Backups hart gegatet erstellen und Restore-Dry-Run ausfuehren. Echter Restore bleibt nicht freigegeben.

## Gepruefte Bausteine

| Baustein | Status | Hinweis |
|---|---|---|
| Backup Preview Model | umgesetzt | zeigt geplante Backup-Inhalte ohne Write |
| Backup Write Guard | umgesetzt | prueft Token, Zielpfad, Smoke und Excludes |
| Backup Write Implementation | umgesetzt | schreibt lokal nur unter Guard |
| Restore Dry-Run Model | umgesetzt | prueft Backup ohne Zurueckschreiben |
| Backup / Restore CLI Read-Only Preview | umgesetzt | Backup Preview und Restore Dry-Run sichtbar |
| Backup Write CLI Approval Implementation | umgesetzt | Backup Write nur mit Safety Smoke PASS und `BACKUP ERSTELLEN` |

## CLI-Status

Hauptmenue:

```text
11. Backup / Restore
```

Untermenue:

```text
1. Backup-Vorschau anzeigen
2. Backup lokal erstellen
3. Restore-Dry-Run prüfen
4. Zurück zum Hauptmenü
```

## Freigegeben

- Backup Preview im CLI anzeigen.
- Lokales Backup unter `local_data/backups/` erstellen.
- Backup Write nur mit Safety Smoke PASS.
- Backup Write nur mit hartem Token `BACKUP ERSTELLEN`.
- Restore-Dry-Run im CLI ausfuehren.
- Ungueltige Eingaben stabil behandeln.
- Rueckkehr zum Hauptmenue.

## Nicht freigegeben

- echter Restore.
- Restore Write.
- Ueberschreiben aktiver SQLite-Daten.
- Zurueckkopieren von Exporten.
- Obsidian Vault Backup.
- Obsidian Vault Restore.
- ZIP-/Archiv-Entpackung.
- externe Speicherorte.
- Netzwerkaktionen.
- Provider-/Modellaufrufe.
- automatische Backups beim Start.

## Gepruefte Blockierungen

| Fall | Ergebnis |
|---|---|
| Enter bei Backup Write | bricht ab |
| `JA` bei Backup Write | schreibt nicht |
| falscher Token | schreibt nicht |
| Safety Smoke FAIL | schreibt nicht |
| Restore-Dry-Run | schreibt nichts zurueck |
| ungueltige Menueauswahl | Standardmeldung |

## Teststatus

- CLI-/Backup-Fokus: 87 passed
- Full Regression: 530 passed
- compileall: erfolgreich
- Scanner Smoke Script: PASS
- git diff --check: sauber

## Safety-Bewertung

- Backup Write ist hart gegatet.
- Restore bleibt nicht freigegeben.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Kein Netzwerk.
- Keine Provider.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Entscheidung

Der lokale Backup-/Restore-CLI-Block ist freigegeben fuer:

- Backup Preview
- hart gegateten lokalen Backup Write
- Restore Dry-Run

Nicht freigegeben bleibt:

- echter Restore

## Empfehlung

Naechster sinnvoller Build Step:

Restore Write Plan.
