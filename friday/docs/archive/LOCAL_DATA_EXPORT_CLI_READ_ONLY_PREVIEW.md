# Local Data Export CLI Read-Only Preview

## Ziel

Dieses Dokument beschreibt die read-only CLI-Anzeige fuer den lokalen Datenexport.

Der Schritt macht den Export noch nicht ausführbar. Friday zeigt nur eine Vorschau im bestehenden Backup-/Restore-Menue.

## Geaenderte Bereiche

| Datei | Änderung |
|---|---|
| `friday/app/menu.py` | Backup-/Restore-Untermenue um Export-Preview erweitert |
| `friday/app/interface.py` | Read-only Anzeige fuer Local Data Export Preview ergaenzt |
| `friday/tests/test_menu.py` | Menueoptionen angepasst |
| `friday/tests/test_interface_main_menu_e2e.py` | E2E-Test fuer Export-Preview ohne Export ergaenzt |

## Menueverhalten

Das Backup-/Restore-Menue enthaelt jetzt:

| Option | Bedeutung |
|---|---|
| `1` | Backup-Vorschau anzeigen |
| `2` | Backup lokal erstellen |
| `3` | Restore-Dry-Run pruefen |
| `4` | Restore-Kopie erstellen |
| `5` | Lokaler Datenexport Vorschau anzeigen |
| `6` | Zurueck zum Hauptmenue |

## Angezeigte Informationen

Die neue Preview zeigt:

- geplanten Zielordner unter `local_data/exports`,
- Hinweis, dass kein Export erstellt wurde,
- Hinweis, dass kein Token abgefragt wurde,
- deaktivierte externe Aktionen,
- geplante Exportbereiche,
- ausgeschlossene Inhalte wie `.env`, Tokens, Obsidian Vault und rohe aktive DB.

## Bewusst nicht eingebaut

- Kein echter Export.
- Kein Token-Prompt.
- Kein Writer-Aufruf.
- Keine Datenbankabfrage.
- Keine Repository-Sammlung.
- Keine ZIP-Erstellung.
- Keine externe Aktion.
- Keine neuen Safety-Flags.

## Tests

Abgedeckt durch:

- `friday/tests/test_menu.py`
- `friday/tests/test_interface_main_menu_e2e.py`

Geprueft wird:

- Menueoption ist vorhanden,
- Ruecksprung nutzt Option `6`,
- Preview wird angezeigt,
- Zielbereich `local_data/exports` ist sichtbar,
- ausgeschlossene Inhalte werden angezeigt,
- es wird kein Exportordner erstellt.

## Safety-Bewertung

- Keine externe Aktion.
- Keine Netzwerkaktion.
- Keine Datenbankabfrage.
- Keine Datenbankschema-Aenderung.
- Kein Export.
- Kein Token-Prompt.
- Writer bleibt nicht angebunden.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export CLI Read-Only Readiness Gate` folgen.

Dieses Gate sollte pruefen:

- Menue und Preview bleiben read-only,
- kein Writer wird aufgerufen,
- kein Token wird abgefragt,
- kein Exportordner wird erstellt,
- Tests und Safety Smoke bleiben gruen.
