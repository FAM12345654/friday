# Restore Write CLI Approval Implementation

## Ziel

Restore Copy sicher in das lokale Backup-/Restore-Menue integrieren.

Der Restore Write erstellt nur eine lokale Restore-Kopie unter `local_data/restores/` und ersetzt niemals die aktive Friday-Datenbank.

## Implementierter CLI-Bereich

```text
Backup / Restore
1. Backup-Vorschau anzeigen
2. Backup lokal erstellen
3. Restore-Dry-Run prüfen
4. Restore-Kopie erstellen
5. Zurück zum Hauptmenü
```

## Write-Regel

Eine Restore-Kopie wird nur geschrieben, wenn:

1. Restore Dry-Run erfolgreich ist.
2. Restore Write Guard erlaubt.
3. Nutzer exakt `RESTORE AUSFUEHREN` eingibt.
4. Zielpfad unter `local_data/restores/` liegt.
5. aktive Datenbank nicht ersetzt wird.

## Blockierte Fälle

- Enter bricht ab.
- `JA` schreibt nicht.
- `ja` schreibt nicht.
- `BACKUP ERSTELLEN` schreibt nicht.
- fehlgeschlagener Dry-Run schreibt nicht.
- aktiver DB-Konflikt schreibt nicht.
- bestehender Restore-Zielordner wird nicht ueberschrieben.

## Nicht enthalten

- Kein Restore in aktive Projektpfade.
- Kein Ersetzen von `friday.db`.
- Kein Restore aus ZIP.
- Kein Obsidian Vault Restore.
- Keine externen Speicherorte.
- Kein Netzwerk.
- Keine Provider.

## Tests

- `test_interface_main_menu_e2e.py`
- Restore-Writer-/Guard-Regression

## Safety-Bewertung

- Restore Write ist hart gegatet.
- Restore-Kopie bleibt lokal.
- Aktive Datenbank wird nicht ersetzt.
- Restore schreibt nur in separaten Zielordner.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Restore Write CLI Readiness Gate.
