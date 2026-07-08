# Friday Local MVP Release Candidate Checklist

## Ziel

Diese Checkliste beschreibt, was vor der lokalen MVP-Freigabe von Friday geprueft sein muss.

Sie baut auf dem `FRIDAY_LOCAL_MVP_RELEASE_CONSOLIDATION_GATE.md` auf und dient als praktische Go/No-Go-Liste fuer den lokalen Windows-Betrieb.

## Release Candidate Status

| Bereich | Status | Nachweis |
|---|---|---|
| Full Regression | bestanden | `983 passed, 4 skipped` |
| Compilecheck | bestanden | `python -m compileall friday` |
| Safety Smoke | bestanden | `Overall: PASS` |
| Diff Check | bestanden | `git diff --check` sauber |
| Externe Aktionen | deaktiviert | Safety-Flags lokal-only |
| Datenbankschema | stabil | Keine ungatete Schema-Aenderung in diesem Gate |
| Nutzer-Doku | vorhanden | `README_USER.md` |
| Release-Konsolidierung | vorhanden | `FRIDAY_LOCAL_MVP_RELEASE_CONSOLIDATION_GATE.md` |

## Lokale Start-Checks

Vor lokaler Nutzung pruefen:

```bash
python -m friday.main
```

Optional auf Windows:

```bash
start_friday.bat
```

Tests starten:

```bash
run_tests.bat
```

## Pflichtchecks vor Go

| Check | Befehl | Erwartung |
|---|---|---|
| Full Regression | `python -m pytest friday/tests` | gruen |
| Compilecheck | `python -m compileall friday` | erfolgreich |
| Safety Smoke | `python scripts/friday_safety_smoke.py` | `Overall: PASS` |
| Diff Check | `git diff --check` | sauber |

## MVP-ready Funktionen

| Bereich | MVP-Status |
|---|---|
| Hauptmenue / CLI | ready |
| Aufgaben | ready |
| Review / Vorschlaege | ready |
| Review Activity Summary / Detail / Filter / Search | ready |
| Kontakt-Kontext lokal | ready |
| Privacy Dashboard / Cleanup | ready |
| Backup / Restore lokal | ready |
| Obsidian Brain Preview / gated Write | ready |
| Local AI Mock / Validator / Logic Check | ready |
| Self-Building Preview | ready |
| Safety Scanner / Smoke Script | ready |

## Deferred / nicht freigegeben

Diese Funktionen sind nicht Teil des lokalen MVP-Go:

| Bereich | Status |
|---|---|
| Echte E-Mail | nicht freigegeben |
| Echtes WhatsApp | nicht freigegeben |
| Echte SMS | nicht freigegeben |
| Echte Kalendertermine | nicht freigegeben |
| Cloud-AI | nicht freigegeben |
| Automatische Obsidian-Batch-Writes | nicht freigegeben |
| Self-Building Runner ohne Gate | nicht freigegeben |
| Mobile/Publish/Cloudflare-Skripte | ausserhalb lokales MVP |

## Safety-Flags

Diese Werte muessen unveraendert bleiben:

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

## Harte Tokens

Harte Tokens bleiben fuer lokale Schreib-/Risk-Flows erforderlich, z. B.:

- `BACKUP ERSTELLEN`
- `RESTORE ANWENDEN`
- `IMPORT ANWENDEN`
- `PERSON VERGESSEN`
- `OBSIDIAN SCHREIBEN`

Weiche Tokens wie `ja`, `JA` oder `ok` duerfen fuer diese Risk-Flows nicht reichen.

## Go-Kriterien

Friday kann lokal als MVP genutzt werden, wenn:

1. Full Regression gruen ist.
2. Compilecheck erfolgreich ist.
3. Safety Smoke `Overall: PASS` meldet.
4. `git diff --check` sauber ist.
5. Keine externen Aktionen aktiviert wurden.
6. README_USER fuer Start, Tests, Safety und lokale Grenzen aktuell bleibt.
7. Deferred Features nicht versehentlich im Produktfluss aktiv sind.

## No-Go-Kriterien

Nicht freigeben, wenn:

- Safety Smoke fehlschlaegt,
- Tests rot sind,
- Compilecheck fehlschlaegt,
- externe Aktionen aktiviert wurden,
- Safety-Flags veraendert wurden,
- harte Token durch weiche Bestaetigungen ersetzt wurden,
- Secrets, `.env`, Obsidian Vault oder externe Provider unbeabsichtigt eingebunden werden.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Friday Local MVP Final Go/No-Go Gate.
