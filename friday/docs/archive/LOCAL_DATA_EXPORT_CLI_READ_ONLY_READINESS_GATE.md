# Local Data Export CLI Read-Only Readiness Gate

## Ziel

Dieses Gate prueft die read-only CLI-Anzeige fuer den lokalen Datenexport.

Die Anzeige ist fuer lokale Orientierung freigegeben. Ein echter Export ueber die CLI bleibt noch nicht freigegeben.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/menu.py` | Backup-/Restore-Menue enthaelt Export-Preview und Ruecksprung ueber Option `6` |
| `friday/app/interface.py` | Export-Preview wird angezeigt, ohne Token oder Writer-Aufruf |
| `friday/tests/test_menu.py` | Menueoptionen abgesichert |
| `friday/tests/test_interface_main_menu_e2e.py` | Read-only Export-Preview abgesichert |
| `friday/docs/LOCAL_DATA_EXPORT_CLI_READ_ONLY_PREVIEW.md` | Schritt-Dokumentation vorhanden |

## Readiness-Ergebnis

- Backup-/Restore-Menue zeigt lokalen Datenexport als Preview.
- Ruecksprung zum Hauptmenue ist stabil.
- Preview zeigt Zielbereich `local_data/exports`.
- Preview zeigt geplante Exportbereiche.
- Preview zeigt ausgeschlossene Inhalte.
- Preview fragt keinen Token ab.
- Preview ruft den Writer nicht auf.
- Preview erstellt keinen Exportordner.
- Preview liest keine Datenbank.
- Preview nutzt keine externen Aktionen.

## Nicht freigegeben

Noch nicht freigegeben sind:

- echter Export ueber CLI,
- Token-Prompt `DATEN EXPORTIEREN`,
- Writer-Aufruf aus dem Interface,
- automatische Datensammlung aus Repositories,
- ZIP-Erstellung,
- Cloud-Export,
- Obsidian Export,
- externe Provider,
- echte Nachrichten,
- echte Kalenderaktionen.

## Tests

Abgedeckt durch:

- `friday/tests/test_menu.py`
- `friday/tests/test_interface_main_menu_e2e.py`

Zusatzvalidierung:

- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Safety-Bewertung

- Keine externe Aktion.
- Keine Netzwerkaktion.
- Keine Datenbankabfrage.
- Keine Datenbankschema-Aenderung.
- Kein Export.
- Kein Token-Prompt.
- Kein Writer-Aufruf.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.
- Safety Smoke PASS.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export CLI Approval Plan` folgen.

Dieser Plan sollte festlegen:

- wie der Token `DATEN EXPORTIEREN` spaeter abgefragt wird,
- wie Safety Smoke PASS vor dem Token-Prompt angezeigt wird,
- wie Guard-Blockiergruende im CLI dargestellt werden,
- wie ein Exportabbruch ohne Dateioperation aussieht,
- welche Tests vor einer echten CLI-Write-Anbindung noetig sind.
