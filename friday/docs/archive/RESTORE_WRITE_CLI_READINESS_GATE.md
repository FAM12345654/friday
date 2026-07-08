# Restore Write CLI Readiness Gate

## Ziel

Dieses Gate prueft den aktuellen Restore-Write-CLI-Stand nach der Umsetzung der lokalen Restore-Kopie.

Der Restore-Write bleibt bewusst sicher eingeschraenkt:

- keine Wiederherstellung in aktive Projektpfade,
- kein Ersetzen der aktiven Friday-Datenbank,
- kein Restore aus externen Speicherorten,
- keine Netzwerk- oder Provider-Aktionen.

## Gepruefter CLI-Bereich

```text
Backup / Restore
1. Backup-Vorschau anzeigen
2. Backup lokal erstellen
3. Restore-Dry-Run pruefen
4. Restore-Kopie erstellen
5. Zurueck zum Hauptmenue
```

## Readiness-Ergebnis

| Bereich | Ergebnis |
|---|---|
| Restore-Dry-Run vor Write | erforderlich |
| Hartes Approval-Token | `RESTORE AUSFUEHREN` |
| Zielordner | `local_data/restores/` |
| Aktive Datenbank ersetzen | blockiert |
| Falscher Token | blockiert |
| Enter/Abbruch | schreibt nicht |
| Externe Speicherorte | nicht erlaubt |
| Netzwerk/Provider | nicht vorhanden |

## Abgesicherte Faelle

- Restore-Kopie wird nur nach erfolgreichem Dry-Run erstellt.
- Restore-Kopie wird nur mit exakt `RESTORE AUSFUEHREN` erstellt.
- `JA`, `ja`, Enter und `BACKUP ERSTELLEN` fuehren nicht zu einem Restore-Write.
- Aktiver Datenbankkonflikt blockiert den Restore-Write.
- Restore-Zielordner werden separat unter `local_data/restores/` angelegt.
- Bestehende Restore-Zielordner werden nicht ueberschrieben.
- Die aktive Friday-Datenbank bleibt unangetastet.

## Nicht freigegeben

- Kein Restore in aktive Projektdateien.
- Kein automatisches Ueberschreiben von `friday.db`.
- Kein Restore aus ZIP-Dateien.
- Kein Obsidian-Vault-Restore.
- Kein Cloud-/Provider-/Netzwerkzugriff.
- Kein automatischer Restore ohne Nutzer-Token.

## Testabdeckung

- `test_interface_main_menu_e2e.py`
- `test_restore_writer.py`
- `test_restore_write_guard.py`
- `test_menu.py`
- Full Regression: `python -m pytest friday/tests`
- Compilecheck: `python -m compileall friday`
- Safety Smoke: `python scripts/friday_safety_smoke.py`
- Whitespace/Diff-Check: `git diff --check`

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine aktiven Projektdateien werden ersetzt.
- Restore schreibt nur lokale Kopien.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Restore Dry-Run / Restore Write Documentation Finalization.
