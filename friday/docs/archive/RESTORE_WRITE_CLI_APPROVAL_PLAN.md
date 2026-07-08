# Restore Write CLI Approval Plan

## Ziel

Plan fuer eine spaetere sichere CLI-Anbindung des Restore Writers.

Dieser Schritt baut keine CLI-Integration und fuehrt keinen Restore aus. Er definiert nur, wie der bereits gepruefte Restore Writer spaeter im Backup-/Restore-Menue freigegeben werden darf.

## Ausgangslage

Bereits umgesetzt:

- Restore Dry-Run Model
- Restore Write Guard Model
- Restore Write Implementation
- Restore Write Readiness Gate
- Backup / Restore CLI Readiness Gate

Noch nicht umgesetzt:

- Restore Write im CLI-Menue.
- Restore Write Nutzerbestaetigung im CLI.
- Restore Write CLI Tests.
- Restore Write CLI Readiness Gate.

## Geplanter CLI-Flow

Spaeterer Backup-/Restore-Menuebereich:

```text
Backup / Restore
1. Backup-Vorschau anzeigen
2. Backup lokal erstellen
3. Restore-Dry-Run prüfen
4. Restore-Kopie erstellen
5. Zurück zum Hauptmenü
```

Bei Auswahl `4`:

```text
Restore-Kopie erstellen

Friday kopiert erlaubte Backup-Sektionen nur in:
local_data/restores/friday_restore_<timestamp>/

Die aktive Datenbank wird nicht ersetzt.
Es wird nichts in aktive Projektpfade zurückgeschrieben.

Tippe RESTORE AUSFUEHREN zum Erstellen der Restore-Kopie oder Enter zum Abbrechen:
```

## Approval-Regel

Eine Restore-Kopie darf spaeter nur erstellt werden, wenn:

1. Restore Dry-Run erfolgreich ist.
2. Restore Write Guard erlaubt.
3. Backup liegt unter `local_data/backups/`.
4. Ziel liegt unter `local_data/restores/`.
5. Aktive Datenbank wird nicht ersetzt.
6. Nutzer tippt exakt:

```text
RESTORE AUSFUEHREN
```

## Nicht erlaubte Tokens

Diese Eingaben duerfen keine Restore-Kopie schreiben:

- `JA`
- `ja`
- `ok`
- `yes`
- `SPEICHERN`
- `BACKUP ERSTELLEN`
- leere Eingabe
- Eingaben mit anderem Text

## Geplante Blockiermeldungen

| Fall | Meldung |
|---|---|
| leere Eingabe | `Restore wurde abgebrochen.` |
| falscher Token | `Restore Write wurde nicht freigegeben.` |
| Dry-Run blockiert | `Restore wurde blockiert, weil der Dry-Run nicht erfolgreich war.` |
| aktiver DB-Konflikt | `Restore wurde blockiert, weil eine aktive Datenbank nicht ersetzt werden darf.` |
| Zielordner existiert bereits | `Restore wurde nicht erstellt, weil der Zielordner bereits existiert.` |
| Backup ausserhalb erlaubtem Pfad | `Restore wurde blockiert, weil der Backup-Pfad nicht erlaubt ist.` |

## Safety-Grenzen

Restore Write darf spaeter weiterhin nicht:

- automatisch beim Start laufen.
- ohne Nutzerbestaetigung laufen.
- ohne Restore Dry-Run laufen.
- ohne Restore Write Guard laufen.
- aktive SQLite-Datenbank ersetzen.
- in aktive Projektpfade zurueckkopieren.
- Obsidian Vault wiederherstellen.
- Secrets wiederherstellen.
- externe Speicherorte verwenden.
- Netzwerkaktionen ausloesen.
- Provider-/Modellaufrufe ausloesen.

## Vorgeschlagene Tests fuer spaetere Umsetzung

Wenn der CLI-Flow gebaut wird, sollen Tests abdecken:

- Menueoption `4` fragt nach hartem Token.
- Enter bricht ab.
- `JA` schreibt nicht.
- `ja` schreibt nicht.
- `BACKUP ERSTELLEN` schreibt nicht.
- falscher Token schreibt nicht.
- Dry-Run FAIL schreibt nicht.
- aktiver DB-Konflikt schreibt nicht.
- `RESTORE AUSFUEHREN` schreibt nur in `local_data/restores/`.
- aktive Datenbank bleibt unveraendert.
- existierender Zielordner wird nicht ueberschrieben.
- Rueckkehr ins Backup-/Restore-Menue bleibt stabil.
- Exit danach bleibt stabil.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine CLI-Restore-Write-Anbindung gebaut.
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

Restore Write CLI Approval Implementation.
