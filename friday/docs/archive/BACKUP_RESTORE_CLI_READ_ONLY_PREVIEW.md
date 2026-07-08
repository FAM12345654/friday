# Backup / Restore CLI Read-Only Preview

## Ziel

Erster lokaler Backup-/Restore-Menuebereich in der Friday CLI.

Dieser Schritt macht nur lesende Funktionen sichtbar:

- Backup-Vorschau anzeigen.
- Restore-Dry-Run pruefen.
- Zurueck zum Hauptmenue.

Backup Write bleibt bewusst nicht im Menue angebunden.

## Implementierter CLI-Bereich

Hauptmenue:

```text
11. Backup / Restore
```

Untermenue:

```text
Backup / Restore
1. Backup-Vorschau anzeigen
2. Restore-Dry-Run prüfen
3. Zurück zum Hauptmenü
```

## Verhalten

| Option | Verhalten | Schreibt Dateien? |
|---|---|---|
| `1` Backup-Vorschau anzeigen | zeigt geplanten Zielordner und Sektionen | nein |
| `2` Restore-Dry-Run prüfen | prueft einen angegebenen Backup-Ordner | nein |
| `3` Zurueck | kehrt ins Hauptmenue zurueck | nein |

## Nicht enthalten

- Kein Backup Write im Menue.
- Kein harter Token im Menue.
- Kein echter Restore.
- Kein Ueberschreiben aktiver Daten.
- Kein ZIP.
- Kein externer Speicherort.
- Kein Netzwerk.
- Keine Provider.

## Tests

- `test_menu.py`
- `test_cli_flow.py`
- `test_interface_main_menu_e2e.py`

## Safety-Bewertung

- Backup Preview bleibt lesend.
- Restore Dry-Run bleibt lesend.
- Backup Write bleibt separat gegatet.
- Echter Restore bleibt nicht freigegeben.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Backup Write CLI Approval Plan.
