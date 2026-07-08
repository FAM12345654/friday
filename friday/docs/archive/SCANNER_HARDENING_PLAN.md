# Friday Scanner Hardening Plan

## Ziel

Plan fuer lokale Safety-Scanner nach Guard-Integration in Contact Save.

## Ausgangslage

Friday besitzt lokale sicherheitsrelevante Datenfluesse fuer:

- Contact Context
- Contact Repository
- Review Contact Integration
- Task Contact Snapshot
- Obsidian Brain Preview / Write Gate
- Local Model Foundation
- Sensitive Contact Context Guard

Full Regression: `417 passed`.

## Geplante Scanner

| Scanner | Zweck | Status |
|---|---|---|
| Forbidden Import Scanner | blockierte Imports erkennen | geplant |
| No Network Scanner | Netzwerkzugriffe erkennen | geplant |
| No Input/Print Scanner | isolierte Module side-effect-frei halten | geplant |
| Safety Flag Regression Scanner | Safety-Flags pruefen | geplant |
| Approval Token Scanner | harte Tokens pruefen | geplant |
| Obsidian Write Boundary Scanner | automatische Writes verhindern | geplant |
| Sensitive Guard Usage Scanner | Contact Save Guard nicht umgehen | geplant |
| Friday Safety Smoke Script | alle Scanner gesammelt ausfuehren | geplant |

## Forbidden Imports

Zu pruefen:

- `openai`
- `requests`
- `httpx`
- `twilio`
- `googleapiclient`
- `msgraph`
- `whatsapp`
- `smtplib`
- `imaplib`
- `poplib`
- `socket`

## Netzwerk-Muster

Zu pruefen:

- `requests.`
- `httpx.`
- `urllib.`
- `socket.`
- `aiohttp`
- `websocket`

## Side-Effect-Muster

Zu pruefen in isolierten Modulen:

- `input(`
- `print(`

Erlaubte UI-Ausnahmen muessen explizit dokumentiert werden.

## Safety Flags

Erwartet:

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Approval Tokens

Zu pruefen:

- `SPEICHERN`
- `KONTAKT LÖSCHEN`
- `OBSIDIAN SCHREIBEN`

## Obsidian Boundary

Scanner soll spaeter pruefen:

- kein automatischer Write
- Vault-Pfad erforderlich
- Write-Flag erforderlich
- Token `OBSIDIAN SCHREIBEN` erforderlich

## Sensitive Guard Usage

Scanner soll spaeter pruefen:

- Contact Repository Save nutzt Guard
- Contact Repository Update nutzt Guard
- CLI Contact Save umgeht Guard nicht
- Review Contact Save umgeht Guard nicht

## Smoke Script Ziel

Spaeteres Script:

```powershell
python scripts/friday_safety_smoke.py
```

Soll gesammelt ausfuehren:

- Full Regression
- compileall
- git diff --check
- alle Safety Scanner

## Nicht-Ziele

- Keine Implementierung in diesem Step.
- Keine Produktlogik.
- Keine DB-Migration.
- Keine externen Aktionen.
- Keine Modellaufrufe.
- Kein automatischer Obsidian-Write.

## Empfehlung fuer naechsten Build Step

Forbidden Import Scanner:

- erster kleiner technischer Scanner
- liest lokale Python-Dateien
- meldet blockierte Imports
- keine Produktlogik
