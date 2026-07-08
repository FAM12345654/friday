# Friday Local MVP Release Notes

## Release

Friday Local MVP

Datum: 2026-07-08

## Kurzfassung

Friday ist als lokaler MVP fuer den Windows-PC freigegeben.

Der MVP bleibt lokal-first:

- keine echten Nachrichten,
- keine echten Kalendertermine,
- keine externen Provider,
- keine Cloud-AI,
- keine unguarded Writes.

## Aktueller Validierungsstand

| Check | Ergebnis |
|---|---|
| Full Regression | `983 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Diff Check | sauber |

## Enthaltene MVP-Bereiche

| Bereich | Status |
|---|---|
| Lokale CLI | enthalten |
| Aufgabenverwaltung | enthalten |
| Lokale Review-/Vorschlagspruefung | enthalten |
| Review Activity Summary / Detail / Filter / Search | enthalten |
| Kontakt-Kontext lokal | enthalten |
| Privacy Dashboard / Cleanup | enthalten |
| Backup / Restore lokal | enthalten |
| Obsidian Brain Preview / gated Write | enthalten |
| Local AI Mock / Validator / Logic Check | enthalten |
| Self-Building Preview | enthalten |
| Safety Scanner / Smoke Script | enthalten |

## Bewusst nicht enthalten

| Bereich | Status |
|---|---|
| Echte E-Mail | deferred |
| Echtes WhatsApp | deferred |
| Echte SMS | deferred |
| Echte Kalendertermine | deferred |
| Wetter-/Musik-Provider | deferred |
| Cloud-AI | deferred |
| Automatische Obsidian-Batch-Writes | deferred |
| Mobile/Publish/Cloudflare-Flows | ausserhalb lokales MVP |

## Start

Im Projektordner:

```bash
python -m friday.main
```

Alternativ auf Windows:

```bash
start_friday.bat
```

## Tests

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Safety-Hinweis

Diese Safety-Flags bleiben fuer den lokalen MVP verbindlich:

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

Riskante lokale Schreib- oder Loeschfluesse bleiben hart gegatet, z. B.:

- `BACKUP ERSTELLEN`
- `RESTORE ANWENDEN`
- `IMPORT ANWENDEN`
- `PERSON VERGESSEN`
- `OBSIDIAN SCHREIBEN`

## Bekannte Grenzen

- Externe Integrationen sind bewusst deaktiviert.
- Cloud-Provider sind bewusst deaktiviert.
- Mobile/Publish/Cloudflare-Skripte gehoeren nicht zum lokalen MVP-Gate.
- Neue riskante Flows brauchen eigene Plan-, Guard- und Readiness-Gates.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Friday Local MVP Release Notes Readiness Gate.
