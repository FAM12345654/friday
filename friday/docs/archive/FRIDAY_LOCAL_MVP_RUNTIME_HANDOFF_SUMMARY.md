# Friday Local MVP Runtime Handoff Summary

## Ziel

Dieses Dokument fasst den aktuellen lokalen Runtime-Stand von Friday fuer die weitere Uebergabe zusammen.

Der Schritt ist bewusst dokumentationsorientiert:

- keine Produktlogik,
- keine neuen Features,
- keine neuen Tests,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Lokaler MVP-Status

| Bereich | Status | Hinweis |
|---|---|---|
| Lokale CLI | stabil | Start ueber `python -m friday.main` oder `start_friday.bat` |
| Aufgabenverwaltung | stabil | Create, Edit, Search, Done, Archive, Delete lokal abgesichert |
| Review / Vorschlaege | stabil | Nachrichten- und Aufgaben-Vorschlaege bleiben lokal |
| Review Activity | stabil | Summary, Detail, Status-/Type-Filter, Search und Combined Filter |
| Contact Context | stabil | Preview, Draft, Save Approval, Forget Flow und Sensitive Guard |
| Obsidian Brain | gated | Preview, Dry-Run und Write nur mit Guard und hartem Token |
| Backup / Restore | gated | Backup Write und Restore Copy lokal, kein In-Place-Restore |
| Privacy Dashboard / Cleanup | gated | Read-only Uebersicht plus guard-basierte Cleanup-Flows |
| Local Data Export / Import | gated | Export und Import-Apply nur lokal, guard-basiert und tokenpflichtig |
| Day Planning | read-only | Tagesplanung bleibt Vorschau ohne automatische Task-Aenderung |
| Local AI | preview-only | Mock bleibt Default, keine Cloud-AI, keine echten Modellaufrufe |
| Safety Scanner | stabil | Scanner Smoke Script prueft zentrale lokale Safety-Regeln |

## Aktuelle Validierung

| Check | Ergebnis |
|---|---|
| Full Regression | `983 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Diff Check | sauber |

Die bekannten Skips sind akzeptiert und blockieren den lokalen MVP nicht.

## Standard-Kommandos

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Bewusst deaktivierte externe Funktionen

| Funktion | Status |
|---|---|
| Echte E-Mail | deaktiviert |
| Echtes WhatsApp | deaktiviert |
| Echte SMS | deaktiviert |
| Echte Kalendertermine | deaktiviert |
| Wetter-Provider | deaktiviert |
| Musik-Provider | deaktiviert |
| Cloud-AI | deaktiviert |
| Externe Provider-Aufrufe | nicht freigegeben |

## Safety-Flags

Diese Werte bleiben fuer die lokale Runtime verbindlich:

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

## Harte Token-Grenzen

Riskante lokale Schreib- oder Loeschfluesse bleiben hart gegatet:

- `SPEICHERN`
- `KONTAKT LÖSCHEN`
- `PERSON VERGESSEN`
- `OBSIDIAN SCHREIBEN`
- `BACKUP ERSTELLEN`
- `RESTORE AUSFUEHREN`
- `DATEN EXPORTIEREN`
- `IMPORT ANWENDEN`
- `EXPORT AUFRAEUMEN`
- `BACKUP AUFRAEUMEN`
- `RESTORE AUFRAEUMEN`
- `REVIEW AUFRAEUMEN`

Weiche Bestaetigungen duerfen diese Flows nicht ersetzen.

## Uebergabe-Hinweise

- Friday ist lokal als MVP nutzbar.
- Externe Integrationen bleiben deferred.
- Mobile/Publish/Cloudflare-Flows gehoeren nicht zum lokalen MVP-Gate.
- Neue riskante Funktionen brauchen eigene Plan-, Guard-, Writer- und Readiness-Gates.
- Produktlogik sollte nur in kleinen, fokussierten Schritten erweitert werden.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Roadmap Phase 1 lokale Stabilisierung.
