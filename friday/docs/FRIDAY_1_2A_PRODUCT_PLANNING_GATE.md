# Friday 1.2A Product Planning Gate

## Ziel

Build Step 1.2A plant den naechsten kleinen lokalen Produktfortschritt nach Friday 1.1. Dieser Schritt baut keine neue Produktlogik und aktiviert keine externen Aktionen.

## Ausgangslage

| Bereich | Stand |
|---|---|
| Lokale Baseline | `e7e9580` |
| Post-1.0 UX Commit | `f6617db` |
| Letzter Full Run | `1084 passed, 4 skipped` |
| Safety Smoke | `Overall: PASS` |
| Produktmodus | lokal |
| Externe Aktionen | deaktiviert |

## Bewertete Kandidaten fuer Friday 1.2

| Kandidat | Nutzen | Risiko | Empfehlung |
|---|---|---|---|
| Lokale Aufgaben-Review-Ansicht verbessern | hoch | niedrig | empfohlen |
| E-Mail-Draft Templates lokal | mittel | niedrig bis mittel | danach sinnvoll |
| Backup/Restore Status-Zusammenfassung | mittel | niedrig | gut als Doku-/UX-Folge |
| Kontakt-Kontext Suchkomfort | mittel | niedrig | spaeter sinnvoll |
| Kalender Draft-only Planung | hoch | mittel | erst nach weiterem Gate |
| echte E-Mail/WhatsApp/SMS/Kalender | hoch | hoch | nicht fuer 1.2 ohne Live-Gate |

## Gewaehlter erster 1.2-Kandidat

**Lokale Aufgaben-Review-Ansicht verbessern**

Warum:

- hoher Nutzerwert im bestehenden lokalen Kernprodukt,
- keine externen Dienste,
- keine neuen Provider,
- wahrscheinlich keine Datenbankschema-Aenderung,
- gut testbar mit vorhandenen Task-/CLI-Tests,
- passt zur stabilen 1.0/1.1-Basis.

## Erlaubter Scope fuer 1.2B

Erlaubt:

- bessere lokale Aufgaben-Zusammenfassung,
- klare Anzeige von offenen, faelligen, ueberfaelligen und erledigten Aufgaben,
- read-only Einstieg ueber bestehende Aufgaben- oder Hilfe-Pfade,
- Tests fuer Anzeige und Rueckkehrpfade,
- Dokumentation.

Nicht erlaubt:

- echte externe Aktionen,
- neue Provider,
- Cloud-AI,
- E-Mail-/WhatsApp-/SMS-/Kalender-Live-Funktionen,
- Datenbankschema-Aenderung ohne eigenes Schema-Gate,
- Abschwaechung harter Tokens,
- automatische Loesch-/Archivierungsaktionen.

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

## Empfohlene Tests fuer 1.2B

- `python -m pytest friday/tests/test_task_interface_flow.py`
- `python -m pytest friday/tests/test_interface_main_menu_e2e.py`
- `python -m pytest friday/tests/test_task_agent.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer naechsten Build Step

Build Step 1.2B: Lokale Aufgaben-Review-Ansicht planen oder als read-only Preview-Modell bauen, ohne Datenbankschema-Aenderung und ohne externe Aktionen.
