# Backup Write CLI Approval Plan

## Ziel

Plan fuer eine spaetere sichere CLI-Anbindung des bereits vorhandenen lokalen Backup Writers.

Dieser Schritt baut noch keine neue Produktlogik und keinen neuen Menuepunkt. Er definiert nur, wie ein Backup Write spaeter aus dem Backup-/Restore-Menue heraus freigegeben werden darf.

## Ausgangslage

Bereits umgesetzt:

- Backup Preview Model
- Backup Write Guard / Model
- Backup Write Implementation
- Backup Write Readiness Gate
- Restore Dry-Run Model
- Restore Dry-Run Readiness Gate
- Backup / Restore CLI Read-Only Preview

Noch nicht umgesetzt:

- Backup Write im CLI-Menue.
- Scanner-Smoke-Ausfuehrung aus der CLI.
- Nutzerbestaetigung im CLI-Backup-Flow.
- Restore Write.

## Geplanter CLI-Flow

Spaeterer Ablauf fuer `Backup lokal erstellen`:

```text
Backup / Restore
1. Backup-Vorschau anzeigen
2. Backup lokal erstellen
3. Restore-Dry-Run prüfen
4. Zurück zum Hauptmenü
```

Bei Auswahl `2`:

```text
Backup lokal erstellen

Friday erstellt ein lokales Backup nur unter:
local_data/backups/

Nicht enthalten:
- .env
- Secrets
- Obsidian Vault
- Caches

Vor dem Schreiben muss der Safety Smoke PASS sein.
Tippe BACKUP ERSTELLEN zum Erstellen oder Enter zum Abbrechen:
```

## Approval-Regel

Ein Backup Write darf spaeter nur laufen, wenn alle Bedingungen erfuellt sind:

1. Backup Preview wurde gebaut.
2. Scanner Smoke Script ist `PASS`.
3. Backup Write Guard erlaubt.
4. Zielpfad liegt unter `local_data/backups/`.
5. Nutzer tippt exakt:

```text
BACKUP ERSTELLEN
```

## Nicht erlaubte Tokens

Diese Eingaben duerfen kein Backup schreiben:

- `JA`
- `ja`
- `ok`
- `yes`
- `speichern`
- `SPEICHERN`
- leere Eingabe
- Eingaben mit anderem Text

## Geplante Blockiermeldungen

| Fall | Meldung |
|---|---|
| leere Eingabe | `Backup wurde abgebrochen.` |
| falscher Token | `Backup wurde nicht freigegeben.` |
| Scanner Smoke FAIL | `Backup wurde blockiert, weil der Safety Smoke nicht erfolgreich war.` |
| Zielordner existiert bereits | `Backup wurde nicht erstellt, weil der Zielordner bereits existiert.` |
| Ziel ausserhalb erlaubtem Pfad | `Backup wurde blockiert, weil der Zielpfad nicht erlaubt ist.` |

## Safety-Grenzen

Backup Write darf spaeter weiterhin nicht:

- automatisch beim Start laufen.
- ohne Nutzerbestaetigung laufen.
- ohne Scanner Smoke PASS laufen.
- ausserhalb `local_data/backups/` schreiben.
- `.env` oder Secrets kopieren.
- Obsidian Vault sichern.
- externe Speicherorte verwenden.
- Netzwerkaktionen ausloesen.
- Restore starten.
- aktive Daten ueberschreiben.

## Vorgeschlagene Tests fuer spaetere Umsetzung

Wenn der CLI-Write-Flow gebaut wird, sollen Tests abdecken:

- Menueoption `2` fragt nach hartem Token.
- Enter bricht ab.
- `JA` schreibt nicht.
- `ja` schreibt nicht.
- `SPEICHERN` schreibt nicht.
- falscher Token schreibt nicht.
- Scanner Smoke FAIL schreibt nicht.
- `BACKUP ERSTELLEN` schreibt genau unter `local_data/backups/`.
- bestehender Zielordner wird nicht ueberschrieben.
- `.env`, Secrets und Obsidian Vault werden nicht kopiert.
- Rueckkehr ins Backup-/Restore-Menue bleibt stabil.
- Exit danach bleibt stabil.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine CLI-Write-Anbindung gebaut.
- Keine Tests geaendert.
- Kein Backup geschrieben.
- Kein Restore ausgefuehrt.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine Netzwerkaktionen.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Backup Write CLI Approval Implementation.
