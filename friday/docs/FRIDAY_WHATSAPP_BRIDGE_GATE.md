# Friday WhatsApp Read-Bridge Gate

## Ziel

Dieses Gate beschreibt die lokale WhatsApp-Web-Read-Bridge.
Die Bridge ist bewusst getrennt vom Python-Paket und liest nur eingehende WhatsApp-Web-Ereignisse.
Friday sendet ueber diese Bridge nichts.

## Umgesetzt

| Bereich | Status | Hinweis |
|---|---|---|
| Neues Read-Flag | umgesetzt | `ENABLE_WHATSAPP_BRIDGE_READ = False` als Default |
| Safety-Flags | unveraendert | `ENABLE_REAL_WHATSAPP = False` bleibt bestehen |
| API-Ingest | umgesetzt | `POST /api/whatsapp/ingest`, gesperrt wenn Read-Flag aus |
| API-Status | umgesetzt | `GET /api/whatsapp/status` |
| API-Nachrichten | umgesetzt | `GET /api/whatsapp/messages`, read-only |
| SQLite-Tabelle | umgesetzt | `whatsapp_messages` mit Hash fuer Chat/Nummer |
| Agent-Verarbeitung | umgesetzt | lokale Reply-/Task-Suggestions im bestehenden Review-Flow |
| CLI-Anzeige | umgesetzt | Nachrichtenbereich zeigt WhatsApp-Read-Preview |
| CLI-Kontenmenue | umgesetzt | Status und Aktivierungs-Gate |
| Mobile-Anzeige | umgesetzt | Nachrichten-Tab und Datenschutz-Statuskarte |
| Node-Bridge | umgesetzt | `friday-whatsapp-bridge/` mit `whatsapp-web.js` und `qrcode-terminal` |
| Start/Stop-Skripte | umgesetzt | `start_whatsapp_bridge.bat`, `stop_whatsapp_bridge.bat` |

## Sicherheitsgrenzen

- Kein automatischer WhatsApp-Versand.
- Keine Auto-Antwort.
- Kein History-Massenabruf.
- Keine Presence-Manipulation.
- Gruppen werden standardmaessig ignoriert.
- Senden bleibt nur Deep-Link/App-Oeffnung mit Token `WHATSAPP SENDEN`.
- `ENABLE_REAL_WHATSAPP` bleibt `False`.
- Neue Bridge ist nur Lesen und hinter `ENABLE_WHATSAPP_BRIDGE_READ`.

## Aktivierung

Aktivierung braucht:

1. Token `WHATSAPP BRIDGE AKTIVIEREN`.
2. Safety Smoke `PASS`.
3. Nutzerentscheidung trotz Risiko-Hinweis.

Start danach:

```powershell
.\start_friday_api.bat
.\start_whatsapp_bridge.bat
```

Beim ersten Start muss im Bridge-Ordner einmal installiert werden:

```powershell
cd friday-whatsapp-bridge
npm install
```

## Datenschutz

- WhatsApp-Session, Bridge-Token und Bridge-Konfiguration liegen unter `local_data/whatsapp/`.
- `local_data/whatsapp/` ist gitignored.
- Telefonnummern werden nicht im Klartext in SQLite gespeichert.
- Chat-ID und Nummer werden gehasht/maskiert.
- Tests verwenden keine echten Telefonnummern und keinen echten WhatsApp-Zugang.
- Logs enthalten keine Nachrichtentexte und keine Telefonnummern.

## Risiko-Hinweis

WhatsApp-Web-Bridges koennen gegen WhatsApp-Regeln verstossen.
Dadurch kann ein Kontosperrungs-Risiko entstehen.
Empfehlung: nur bewusst, lokal und bevorzugt mit Zweitnummer nutzen.

## Rollback

1. Bridge stoppen (`STRG+C` oder `stop_whatsapp_bridge.bat`).
2. In `friday/config.py` setzen:

```python
ENABLE_WHATSAPP_BRIDGE_READ = False
```

3. Optional lokale Bridge-Daten entfernen:

```powershell
Remove-Item -Recurse -Force local_data\whatsapp
```

## Validierung

Aktueller Validierungsstand:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts\friday_safety_smoke.py
git diff --check
npx expo export --platform android
```

Ergebnis:

- `1177 passed, 4 skipped`
- Compilecheck erfolgreich
- Safety Smoke `Overall: PASS`
- Diff-Check sauber
- Expo Android Export erfolgreich

## Naechster sinnvoller Schritt

Manuelle Bridge-Abnahme:

- Read-Flag bewusst aktivieren,
- API starten,
- `npm install` im Bridge-Ordner ausfuehren,
- Bridge starten,
- QR-Code scannen,
- eine Testnachricht empfangen,
- pruefen, dass Vorschlaege im Review-Flow erscheinen,
- bestaetigen, dass nichts automatisch gesendet wird.
