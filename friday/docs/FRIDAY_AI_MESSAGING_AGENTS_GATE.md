# Friday AI Messaging Agents Gate

## Ziel

Dieses Gate dokumentiert die lokale KI-Aktivierung und den Messaging-Draft-Flow fuer Aufgaben-Weiterleitungen.
Friday bleibt lokal-first und sendet keine echten Nachrichten.

## Aktivierter lokaler KI-Stand

| Einstellung | Wert |
|---|---|
| `ENABLE_LOCAL_OLLAMA` | `True` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `OLLAMA_MODEL` | `qwen3:8b` |
| `OLLAMA_TIMEOUT_SECONDS` | `30` |
| Cloud-Fallback | verboten |

Die Aktivierung wurde nur nach dem harten Token `OLLAMA AKTIVIEREN`, Safety-Smoke-PASS und lokalem Health Check angewendet.

## Messaging-Draft-Flow

| Schritt | Verhalten |
|---|---|
| Kontakt auswaehlen | lokal aus gespeicherten Kontakten |
| Kanal auswaehlen | E-Mail oder WhatsApp |
| Draft erstellen | lokal ueber Ollama, sonst lokaler Fallback |
| Token pruefen | `EMAIL SENDEN` oder `WHATSAPP SENDEN` |
| Externe App oeffnen | nur Deep-Link mit vorbereitetem Text |
| Echter Versand | nicht durch Friday; Nutzer entscheidet in der externen App |

## Safety-Grenzen

- Keine echten E-Mails durch Friday.
- Kein echtes WhatsApp durch Friday.
- Keine echte SMS.
- Keine echten Kalenderaktionen.
- Keine Cloud-KI.
- Keine API-Keys oder Provider-Secrets.
- Keine automatische Nachricht.
- Deep-Links oeffnen nur die externe App; der Nutzer sendet manuell.

## Unveraenderte Safety-Flags

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

## Rollback

Wenn die lokale KI wieder deaktiviert werden soll, werden diese Zeilen in `friday/config.py` zurueckgesetzt:

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

Danach muessen laufen:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts\friday_safety_smoke.py
git diff --check
```

## Validierter Stand

| Pruefung | Ergebnis |
|---|---|
| Fokus-Tests KI/Messaging/Safety | `52 passed` |
| Full Regression | `1151 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Diff Check | sauber |
| Lokaler Ollama E2E | `qwen3:8b` lieferte gueltiges JSON im zweiten Warm-Run |

## Empfehlung

Naechster Schritt: Mobile-OTA verteilen und auf dem Handy pruefen:

- App starten,
- Aufgabe oeffnen,
- `Weiterleiten` waehlen,
- Kontakt und Kanal auswaehlen,
- KI-Draft pruefen,
- Token eingeben,
- externe App oeffnet sich,
- Versand bleibt manuell beim Nutzer.
