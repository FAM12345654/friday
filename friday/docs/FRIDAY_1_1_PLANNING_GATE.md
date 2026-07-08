# Friday 1.1 Planning Gate

## Ziel

Dieses Gate definiert den sicheren Startpunkt fuer Friday 1.1 nach dem lokalen 1.0-Abschluss. Der Schritt ist bewusst Planung und aendert keine Produktlogik.

## Ausgangslage

| Bereich | Stand |
|---|---|
| Lokale Baseline | `e7e9580` |
| Version | `1.0.0` |
| Full Regression | `1081 passed, 4 skipped` |
| Safety Smoke | `Overall: PASS` |
| Completion Gate | `FRIDAY_1_0_COMPLETION_GATE.md` |
| Externe Aktionen | deaktiviert |

## Grundregel fuer 1.1

Friday 1.1 darf nur mit kleinen, gegateten Schritten wachsen. Jeder technische Schritt braucht:

- klaren Scope,
- Sub-Agent Review,
- Safety Check,
- fokussierte Tests,
- Full Regression vor Abschluss,
- Dokumentation,
- keine echten externen Aktionen ohne eigenes spaeteres Live-Gate.

## Bewertete Kandidaten

| Kandidat | Nutzen | Risiko | Empfehlung |
|---|---|---|---|
| CLI Polish und Nutzerfuehrung | hoch | niedrig | erster 1.1 Kandidat |
| E-Mail-Draft-Verfeinerung | mittel | niedrig bis mittel | sinnvoll, solange local-only |
| Kalender Draft-only Planung | hoch | mittel | nach CLI Polish |
| Review Batch UX verbessern | mittel | mittel | spaeter, wegen Statuslogik |
| Obsidian Komfortfunktionen | mittel | mittel | nur mit Guard und Preview |
| echte E-Mail/WhatsApp/SMS/Kalender | hoch | hoch | nicht in 1.1 ohne separates Live-Gate |

## Gewaehlter erster Kandidat fuer 1.1

**CLI Polish und Nutzerfuehrung**

Warum:

- verbessert sofort die Bedienbarkeit,
- kein Datenbankschema,
- keine externen Aktionen,
- keine Provider,
- gut testbar,
- passt zum stabilen lokalen 1.0-Stand.

## Erlaubter Scope fuer den ersten 1.1-Step

Erlaubt:

- Texte im CLI-Hilfe-/Start-/Rueckkehrbereich klarer machen,
- README/User-Doku synchronisieren,
- bestehende Menuepfade besser erklaeren,
- Tests fuer bestehende Texte und Rueckwege ergaenzen.

Nicht erlaubt:

- echte E-Mail senden,
- WhatsApp/SMS/Kalender live anbinden,
- OAuth/Login/Secrets,
- Cloud-AI,
- Datenbankschema-Aenderung,
- Abschwaechung harter Tokens,
- automatische externe Aktionen.

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

## Harte Tokens bleiben unveraendert

- `SPEICHERN`
- `KONTAKT LÖSCHEN`
- `PERSON VERGESSEN`
- `OBSIDIAN SCHREIBEN`
- `BACKUP ERSTELLEN`
- `RESTORE AUSFUEHREN`
- `DATEN EXPORTIEREN`
- `REVIEW EXPORTIEREN`
- `IMPORT ANWENDEN`
- `EXPORT AUFRAEUMEN`
- `BACKUP AUFRAEUMEN`
- `RESTORE AUFRAEUMEN`
- `REVIEW AUFRAEUMEN`

## Empfohlene Tests fuer den ersten 1.1-Step

- `python -m pytest friday/tests/test_interface_main_menu_e2e.py`
- `python -m pytest friday/tests/test_cli_flow.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer naechsten Build Step

Build Step 1.1A: CLI Polish und Nutzerfuehrung.

Ziel: Bestehende lokale CLI-Pfade klarer erklaeren und testen, ohne neue externe Funktion und ohne Datenbankschema-Aenderung.
