# Friday Local MVP Final Go/No-Go Gate

## Ziel

Dieses Gate bewertet den finalen lokalen MVP-Stand von Friday nach der Release Candidate Checklist.

Es entscheidet nicht ueber externe Integrationen. Es bewertet nur, ob Friday lokal auf dem Windows-PC als MVP genutzt werden kann.

## Entscheidung

| Entscheidung | Ergebnis |
|---|---|
| Lokaler MVP | GO |
| Externe Integrationen | NO-GO / deferred |
| Cloud-Provider | NO-GO / deferred |
| Echte Nachrichten oder Termine | NO-GO / deferred |

## Freigabeumfang

Friday ist fuer den lokalen MVP-Betrieb freigegeben fuer:

- lokale CLI-Nutzung,
- lokale Aufgabenverwaltung,
- lokale Review- und Vorschlagspruefung,
- lokale Review Activity Summary, Detail View, Filter und Search,
- lokalen Kontakt-Kontext mit Guards und harten Tokens,
- lokales Privacy Dashboard und Cleanup-Flows,
- lokales Backup/Restore mit Guards,
- Obsidian Preview und hart gegatete Writes,
- Local AI Mock/Validator/Logic-Check ohne echten Produkt-Provider,
- Self-Building Preview ohne riskante automatische Ausfuehrung,
- Safety Scanner und Safety Smoke.

## Nicht freigegeben

Diese Bereiche bleiben ausdruecklich nicht freigegeben:

- echte E-Mail,
- echtes WhatsApp,
- echte SMS,
- echte Kalendertermine,
- Wetter-/Musik-Provider,
- Cloud-AI,
- automatische Obsidian-Batch-Writes,
- Self-Building Runner ohne eigenes Gate,
- Mobile/Publish/Cloudflare-Skripte als Teil des lokalen MVP.

## Finaler Validierungsstand

| Check | Ergebnis |
|---|---|
| Full Regression | `983 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Diff Check | sauber |

## Safety-Flags

Diese Werte bleiben fuer den lokalen MVP verbindlich:

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

Riskante lokale Schreib- oder Loeschfluesse bleiben hart gegatet.

Beispiele:

- `BACKUP ERSTELLEN`
- `RESTORE AUSFUEHREN`
- `IMPORT ANWENDEN`
- `PERSON VERGESSEN`
- `OBSIDIAN SCHREIBEN`

Weiche Eingaben wie `ja`, `JA`, `ok`, Enter oder aehnliche Varianten reichen fuer diese Risk-Flows nicht.

## Go-Kriterien

Der lokale MVP ist freigegeben, solange:

1. Full Regression gruen bleibt.
2. Compilecheck erfolgreich bleibt.
3. Safety Smoke `Overall: PASS` meldet.
4. `git diff --check` sauber bleibt.
5. Keine externen Aktionen aktiviert werden.
6. Safety-Flags unveraendert bleiben.
7. Deferred Features eigene Gates bekommen, bevor sie produktiv genutzt werden.

## No-Go-Kriterien

Lokale MVP-Freigabe ist zu stoppen, wenn:

- Tests fehlschlagen,
- Compilecheck fehlschlaegt,
- Safety Smoke fehlschlaegt,
- externe Aktionen aktiviert werden,
- Safety-Flags veraendert werden,
- harte Tokens abgeschwaecht werden,
- Secrets, `.env`, Obsidian Vault oder externe Provider ungeprueft eingebunden werden,
- ein neuer Write-/Delete-Flow ohne Guard und Readiness Gate eingebaut wird.

## Release-Hinweis

Friday ist damit als lokaler MVP releasefaehig.

Die naechste Arbeit sollte nicht mehr ungeordnet neue Features anbauen, sondern in klaren Release- oder Produktphasen erfolgen.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Friday Local MVP Post-Release Roadmap.
