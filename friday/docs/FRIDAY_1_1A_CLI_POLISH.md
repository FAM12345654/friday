# Friday 1.1A CLI Polish und Nutzerfuehrung

## Ziel

Build Step 1.1A verbessert die Orientierung in der lokalen Friday-CLI, ohne Produktlogik zu aendern.

## Geaenderte Bereiche

| Bereich | Verbesserung |
|---|---|
| Hauptmenue | zeigt direkt den Local-Only-Hinweis |
| Hilfe / Uebersicht | zeigt Version, Startbefehl und lokale Safety-Grenze |
| Hilfe / Uebersicht | erklaert Rueckkehrpfade aus Untermenues |
| Tests | pruefen Version, Startbefehl und Local-Only-Hinweis in der Hilfe |
| README | korrigiert den Friday-1.0-Abschlussabschnitt |

## Nicht geaendert

- Keine Datenbankschema-Aenderung.
- Keine neuen externen Integrationen.
- Keine Provider- oder Login-Anbindung.
- Keine Aenderung an harten Tokens.
- Keine Aenderung an Safety-Flags.
- Keine E-Mail-, WhatsApp-, SMS- oder Kalender-Live-Aktion.

## Safety-Flags

```python
ENABLE_REAL_EMAIL = False
ENABLE_REAL_WHATSAPP = False
ENABLE_REAL_SMS = False
ENABLE_REAL_CALENDAR = False
ENABLE_REAL_WEATHER = False
ENABLE_REAL_MUSIC = False
REQUIRE_USER_APPROVAL = True
USE_SQLITE_STORAGE = True
```

## Empfohlene Tests

- `python -m pytest friday/tests/test_interface_main_menu_e2e.py`
- `python -m pytest friday/tests/test_cli_flow.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer naechsten Build Step

Build Step 1.1B: README-/CLI-Begriffe weiter vereinheitlichen oder gezielte kleine UX-Rueckwege in Untermenues pruefen.
