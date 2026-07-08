# Backup Write CLI Approval Implementation

## Ziel

Backup Write sicher in das lokale Backup-/Restore-Menue integrieren.

Der Write ist nur erlaubt, wenn der lokale Safety Smoke erfolgreich ist und der Nutzer exakt `BACKUP ERSTELLEN` eingibt.

## Implementierter CLI-Bereich

```text
Backup / Restore
1. Backup-Vorschau anzeigen
2. Backup lokal erstellen
3. Restore-Dry-Run prüfen
4. Zurück zum Hauptmenü
```

## Write-Regel

Ein Backup wird nur geschrieben, wenn:

1. Backup Preview erfolgreich gebaut wurde.
2. `run_safety_smoke()` `passed=True` meldet.
3. `write_local_backup(...)` den bestehenden Backup Write Guard nutzt.
4. Nutzer exakt `BACKUP ERSTELLEN` eingibt.
5. Zielpfad unter `local_data/backups/` liegt.

## Blockierte Fälle

- Enter bricht ab.
- `JA` schreibt nicht.
- `ja` schreibt nicht.
- `SPEICHERN` schreibt nicht.
- Scanner Smoke FAIL schreibt nicht.
- falscher Token schreibt nicht.
- bestehender Zielordner wird durch Writer blockiert.

## Nicht enthalten

- Kein echter Restore.
- Kein Restore Write.
- Kein ZIP.
- Kein externer Speicherort.
- Kein Netzwerk.
- Keine Provider.
- Kein automatisches Backup beim Start.

## Tests

- `test_menu.py`
- `test_cli_flow.py`
- `test_interface_main_menu_e2e.py`
- Backup-Writer-/Guard-Regression

## Safety-Bewertung

- Backup Write ist hart gegatet.
- Safety Smoke ist Pflicht.
- Backup bleibt lokal.
- Secrets und Obsidian Vault bleiben ausgeschlossen.
- Restore bleibt nicht freigegeben.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Backup / Restore CLI Readiness Gate.
