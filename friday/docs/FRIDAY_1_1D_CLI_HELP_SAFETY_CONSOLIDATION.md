# Friday 1.1D CLI-Hilfe Safety-Konsolidierung

## Ziel

Build Step 1.1D konsolidiert die lokalen Safety-Hinweise in der zentralen CLI-Hilfe. Nutzer sollen an einer Stelle sehen, welche Bereiche lokal bleiben und welche Aktionen harte Tokens brauchen.

## Geaenderte Bereiche

| Bereich | Verbesserung |
|---|---|
| Hilfe / Uebersicht | eigener Block `Lokale Safety-Hinweise` |
| Kontakt-Kontext | Hinweis auf lokale Verarbeitung und harte Tokens |
| E-Mail-Entwurf Preview | Hinweis auf Session-only, kein Provider, kein Versand |
| Backup / Restore | Hinweis auf lokale Writes nur nach hartem Token |
| Privacy Dashboard | Hinweis auf read-only Anzeigen und gegatetes Cleanup |
| Tests | bestehender Hilfe-Test prueft die konsolidierten Hinweise |

## Nicht geaendert

- Keine Produktlogik.
- Keine Datenbankschema-Aenderung.
- Keine neuen Provider.
- Keine externen Aktionen.
- Keine Safety-Flag-Aenderung.
- Keine Token-Aenderung.

## Safety-Bewertung

- Alle Hinweise beschreiben bestehende Sicherheitsgrenzen.
- Es wird keine neue Aktion freigeschaltet.
- E-Mail bleibt draft-only.
- Backup, Restore, Privacy Cleanup und Kontakt-Loeschungen bleiben hart gegated.

## Empfohlene Tests

- `python -m pytest friday/tests/test_interface_main_menu_e2e.py`
- `python -m pytest friday/tests/test_cli_flow.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer naechsten Build Step

Build Step 1.1E: kleine Dokumentationsbereinigung der Post-1.0-Dokumente und optional Full Regression, bevor weitere UX-Schritte folgen.
