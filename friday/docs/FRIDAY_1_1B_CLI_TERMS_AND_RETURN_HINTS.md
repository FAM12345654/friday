# Friday 1.1B CLI-Begriffe und Rueckkehrhinweise

## Ziel

Build Step 1.1B vereinheitlicht kleine CLI-Hinweise, damit Nutzer schneller erkennen, wie sie aus lokalen Untermenues zurueckkehren und welche Aktionen rein lokal bleiben.

## Geaenderte Bereiche

| Bereich | Verbesserung |
|---|---|
| Kontakt-Kontext-Menue | zeigt Local-Only-Hinweis und Rueckkehr ueber `5` |
| E-Mail-Entwurf Preview | zeigt Session-only-Hinweis und Rueckkehr ueber `6` oder Enter |
| Tests | pruefen beide neuen Orientierungshinweise |
| README | ergaenzt kurzen Hinweis auf 1.1B |
| Doku-Index | verlinkt dieses Dokument |

## Nicht geaendert

- Keine Produktlogik geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen aktiviert.
- Keine Provider- oder Login-Anbindung.
- Keine Aenderung an Safety-Flags.
- Keine Aenderung an harten Tokens.

## Safety-Bewertung

- Kontakt-Kontext bleibt lokal und gegated.
- E-Mail-Entwuerfe bleiben Session-only.
- Es wird nichts echt gesendet.
- Es wird kein echter Kalendertermin erstellt.
- Keine Netzwerkaktion.

## Empfohlene Tests

- `python -m pytest friday/tests/test_interface_main_menu_e2e.py`
- `python -m pytest friday/tests/test_cli_flow.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer naechsten Build Step

Build Step 1.1C: kleine Konsistenzpruefung der Backup-/Privacy-Untermenues und README-Begriffe, ohne neue Produktlogik.
