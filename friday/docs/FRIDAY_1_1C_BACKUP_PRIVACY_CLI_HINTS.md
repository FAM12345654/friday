# Friday 1.1C Backup-/Privacy-CLI-Hinweise

## Ziel

Build Step 1.1C verbessert die Orientierung in den lokalen Backup-/Restore- und Privacy-Untermenues. Nutzer sehen direkt, dass diese Bereiche lokal bleiben und dass schreibende Aktionen harte Freigabe-Tokens brauchen.

## Geaenderte Bereiche

| Bereich | Verbesserung |
|---|---|
| Backup / Restore | Local-only-Hinweis und Rueckkehr mit `9` |
| Privacy Dashboard | Read-only-Hinweis fuer Anzeigen und Rueckkehr mit `11` |
| Tests | bestehende E2E-Menue-Tests pruefen die neuen Hinweise |
| README | dokumentiert den 1.1C-UX-Schritt |
| Doku-Index | verlinkt dieses Dokument |

## Nicht geaendert

- Keine Produktlogik.
- Keine Datenbankschema-Aenderung.
- Keine Aenderung an Backup-, Restore-, Export-, Import- oder Cleanup-Guards.
- Keine Aenderung an harten Tokens.
- Keine Aenderung an Safety-Flags.
- Keine externen Aktionen.

## Safety-Bewertung

- Backup/Restore bleibt lokal.
- Privacy-Anzeigen bleiben read-only.
- Cleanup- und Write-Pfade bleiben hart gegated.
- Es werden keine Provider, Logins oder Netzwerke aktiviert.

## Empfohlene Tests

- `python -m pytest friday/tests/test_interface_main_menu_e2e.py`
- `python -m pytest friday/tests/test_cli_flow.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer naechsten Build Step

Build Step 1.1D: leichte Konsistenzpruefung fuer Kontakt-/E-Mail-/Backup-/Privacy-Hinweise im README und in der CLI-Hilfe, ohne neue Produktlogik.
