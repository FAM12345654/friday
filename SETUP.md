# Friday Plattform-Setup (API, Mobile, Desktop)

## 0) Alles auf einmal starten

```bash
start_friday_stack.bat
```

Startet API (8000), Mobile und Desktop in separaten Fenstern.

Optionaler Check:

```bash
verify_friday_services.bat
```

Kontrolliert, ob Port `8000` offen ist, die wichtigsten API-Endpunkte erreichbar sind und ob `friday-mobile/.env` eine passende `EXPO_PUBLIC_FRIDAY_API_URL` enthält.

Ein-Befehl-Checkliste:

```bash
run_friday_checklist.bat
run_friday_checklist.bat --repair
run_friday_checklist.bat --start --repair
run_friday_checklist.bat --repair --mobile-release
run_friday_checklist.bat --install --repair --start
```

Die Checkliste kann Setup/Install ausführen, Shortcuts/Dateien prüfen, den Stack starten und danach die Service-Verifikation ausführen.
Mit `--repair` werden fehlende Shortcuts repariert und `friday-mobile/.env` mit `EXPO_PUBLIC_FRIDAY_API_URL=http://127.0.0.1:8000` angelegt, falls sie fehlt.
Mit `--mobile-release` wird zusätzlich geprüft, ob EAS Build/Update für Handy-Download und automatische Updates vollständig verbunden ist.

Für automatisierte Nutzung (z. B. CI, Skripte) kannst du die Ausgabe vereinfachen:

```bash
verify_friday_services.bat --ci
verify_friday_services.bat --ci --json
verify_friday_services.bat --summary-only
```

Oder direkt mit dedizierter CI-Helferdatei:

```bash
verify_friday_services_ci.bat
```

Optionen:
- `--ci` oder `--no-pause`: läuft ohne `pause` und liefert nur die Zusammenfassung.
- `--summary-only`: unterdrückt Detail-Logs, liefert den `[OK]/[WARN]/[FAIL]`-Status.
- `--json`: gibt zusätzlich einen JSON-Block für das Parsing durch Tools/Pipelines aus.
- `verify_friday_services_ci.bat` nutzt standardmäßig `-SummaryOnly -AsJson`.
- `--help`, `-h`, `/h`, `/?`: zeigt Hilfe für den Aufruf an.

Shortcut-Check:

```bash
verify_friday_shortcuts.bat
verify_friday_shortcuts.bat --ci
verify_friday_shortcuts.bat --repair
verify_friday_shortcuts.bat --repair --ci
verify_friday_shortcuts.bat --no-open --no-pause
```

Optionen:

- `--repair`: erstellt fehlende Verknüpfungen automatisch nach (`create_friday_shortcut.ps1`) und prüft danach erneut.
- `--ci`: setzt `--no-open` und `--no-pause`.
- `--no-open`: öffnet keinen Projekt- oder Desktop-Ordner automatisch.
- `--no-pause`/`/no-pause`/`-nopause`: verhindert die `pause` am Ende.
- `--help`, `-h`, `/h`, `/?`: zeigt kurze Hilfe an.

Alternative (nur Desktop, ohne eingebettete API):

```bash
start_friday_desktop_skip_api.bat
```

## Typische Probleme

### API antwortet nicht auf `/health`

- Prüfe, ob `start_friday_api.bat` aktiv ist.
- Prüfe, ob Port `8000` von einem anderen Dienst belegt ist.
- Wenn Desktop im Stack läuft, nutzt er `FRIDAY_SKIP_EMBEDDED_API=1`, damit kein zweiter API-Prozess startet.

### Port 8000 ist belegt

- Stoppe den alten API-Prozess und starte den Stack neu.
- Alternativ kann der API-Port über `FRIDAY_API_PORT` im Desktop-Lauf geändert werden.

### Mobile kann nicht verbinden

- Prüfe `friday-mobile/.env` (`EXPO_PUBLIC_FRIDAY_API_URL`).
- Emulator: `http://10.0.2.2:8000`
- Sim/Tablet auf PC: `http://127.0.0.1:8000`
- Physisches Gerät: `http://<pc-lan-ip>:8000`

### Desktop startet nicht (Skip-API-Modus)

- `start_friday_desktop_skip_api.bat` erwartet einen laufenden API-Dienst auf `FRIDAY_API_PORT` (Standard `8000`).
- Prüfe zuerst `start_friday_api.bat` oder `start_friday_stack.bat`.
- Starte dann den Check:

```bash
verify_friday_services.bat
```

- Wichtige Hinweise:
  - Wenn der Desktop trotzdem den API selbst starten will, setze vor dem Start `FRIDAY_SKIP_EMBEDDED_API=1`.
  - Für ein anderes Backend-Set einheitlich `FRIDAY_API_PORT`/`FRIDAY_API_HOST` sowie `EXPO_PUBLIC_FRIDAY_API_URL` anpassen.

## 1) API (`friday-api`)

```bash
cd friday-api
python -m pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Sicherstellen:

- Port 8000 frei
- `http://127.0.0.1:8000/health` liefert `{"ok":true,...}`
- CORS erlaubt die Mobile/Desktop-Origins (`FRIDAY_CORS_ORIGINS`)

## 2) Mobile (`friday-mobile`)

```bash
cd friday-mobile
npm install
copy .env.example .env
npm start
```

`EXPO_PUBLIC_FRIDAY_API_URL` muss auf die API zeigen:

Standard fuer physisches Handy im lokalen WLAN: `http://192.168.178.42:8000`

Der vollstaendige Mobile-/Desktop-Guide steht hier:

```text
friday/docs/FRIDAY_MOBILE_DESKTOP_GUIDE.md
```

- Emulator (Android): `http://10.0.2.2:8000`
- Simulator (iOS): `http://127.0.0.1:8000`
- Physisches Gerät: `http://<pc-lan-ip>:8000`

### Handy-Download und automatische Updates

Für eine installierbare Handy-Version nutzt Friday Mobile EAS Build mit interner Distribution. Der Android-Preview-Build erzeugt eine direkt installierbare APK über einen EAS-Link.


Aktueller Creme/Moos-Preview-Build:

```text
https://expo.dev/artifacts/eas/EKmkRcLTi_ZmjHcgInjy_L9QkfPUK9Cg1C7b0qZvUrs.apk
```

Release-Check:

```bash
verify_friday_mobile_release.bat
```

Einmalige EAS-Verknüpfung:

```bash
configure_friday_mobile_eas.bat
```

Danach Android-Download-Link bauen:

```bash
build_friday_mobile_android_preview.bat
```

Kleine App-Updates ohne neuen App-Download veröffentlichen:

```bash
publish_friday_mobile_update_preview.bat
```

Wichtig:
- `configure_friday_mobile_eas.bat` benötigt einen Expo-Login und schreibt die echte EAS `projectId`/Update-URL in `friday-mobile/app.json`.
- `build_friday_mobile_android_preview.bat` erzeugt den installierbaren Handy-Link.
- `publish_friday_mobile_update_preview.bat` verteilt JavaScript-/Asset-Updates über den `preview`-Kanal.
- Native Änderungen, neue Berechtigungen oder neue native Pakete brauchen weiterhin einen neuen Build.

## 3) Desktop (`friday-desktop`)

```bash
cd friday-desktop
npm install
npm run dev
```

Standardmäßig startet Electron den FastAPI-Server automatisch mit derselben Konfiguration.
Im Stack-Betrieb (`start_friday_stack.bat`) wird der eingebettete API-Start übersprungen, da die API bereits separat läuft.

## 4) Konsistenz-Check: Ports, CORS, JSON

### Port-Einheit

- API Host/Port: `0.0.0.0:8000`
- Mobile/Simulator/Devices: auf dasselbe API-Backend verweisen
- Desktop: startet Backend intern über `FRIDAY_API_PORT` (Standard 8000)

### CORS

- Mobile + Desktop-Ziele in `friday-api/.env.example#FRIDAY_CORS_ORIGINS` pflegen.
- Wenn `FRIDAY_CORS_ORIGINS` leer ist, erlaubt FastAPI standardmäßig `*`.

### Gemeinsames JSON-Schema

- Alle API-Antworten nutzen das gleiche Enveloping:

```json
{ "ok": true, "data": { ... } }
```

- Beide Clients lesen ausschließlich `data` aus den Antworten.

### Endpunkte die beide Clients nutzen

- `GET /health`
- `GET /api/dashboard`
- `GET /api/tasks`
- `GET /api/messages`
- `GET /api/calendar`
- `GET /api/contacts`
- `GET /api/privacy`

## 5) Linux/macOS & Docker

Neben den `.bat`-Skripten gibt es Shell-Äquivalente:

```bash
scripts/start_friday_api.sh        # API auf 0.0.0.0:8000
scripts/run_tests.sh               # friday/tests + friday-api/tests
scripts/start_whatsapp_bridge.sh   # WhatsApp-Bridge (npm install bei Bedarf)
```

Oder die API im Container:

```bash
docker compose up friday-api
```

## 6) Neue Funktionen (Kurzüberblick)

- **API-Token (optional)**: `FRIDAY_API_TOKEN` setzen, sobald die API im
  LAN erreichbar ist. Clients senden dann `Authorization: Bearer <token>`.
- **Metriken**: `GET /metrics` zeigt Cache-Trefferquote und Endpunkt-Latenzen.
- **Suche**: `GET /api/search?q=...` (Volltext) und
  `GET /api/search/semantic?q=...` (Ollama-Embeddings, vorher einmal
  `POST /api/search/semantic/reindex`).
- **Follow-ups**: `GET /api/mail/followups` listet gesendete Mails ohne Antwort.
- **Task-Snooze**: `POST /api/tasks/{id}/snooze` mit `{"until": "YYYY-MM-DD"}`;
  wiederkehrende Aufgaben (`taeglich`/`woechentlich`/`monatlich`) gab es schon.
- **Live-Updates**: `GET /api/events` (Server-Sent Events) statt Polling.
- **Verschlüsselte Backups**: `FRIDAY_BACKUP_PASSPHRASE=... python
  scripts/friday_encrypted_backup.py` — geeignet für Task Scheduler/cron.
  Wiederherstellen über `friday.app.backup_encryption.decrypt_backup_archive`.
- **Push-Erinnerungen**: In `friday/config.py` `ENABLE_PUSH_NOTIFICATIONS = True`
  setzen, App einmal öffnen (registriert das Gerät), dann
  `python scripts/friday_push_reminders.py` zeitgesteuert ausführen.
- **CalDAV**: `friday.app.calendar_provider_caldav.CaldavCalendarProvider`
  für Nextcloud/iCloud/Radicale (gleiche Schnittstelle wie Google/ICS).
- **Sprache**: In der Mobile-App unter „Mehr“ zwischen DE und EN umschalten.
- **CI**: GitHub Actions führt bei jedem Push alle Tests auf Linux und
  Windows aus (`.github/workflows/ci.yml`).

## 7) Sprachmodul (Push-to-Talk & gesprochenes Briefing)

Friday kann Sprachbefehle verstehen (lokales Whisper) und mit einer
menschlichen Stimme antworten (lokale TTS-Server, kein Abo, alles offline):

1. **Speech-to-Text**: `pip install -r friday-api/requirements-voice.txt`
   (faster-whisper; Modell `small` wird beim ersten Aufruf geladen).
2. **Deutsche Stimme (Orpheus „Kartoffel“, sehr natürlich, braucht GPU ≥8GB)**:
   [Orpheus-FastAPI](https://github.com/Lex-au/Orpheus-FastAPI) auf Port 5005
   starten und in `friday/config.py` bei Bedarf `VOICE_TTS_DE_*` anpassen.

   **VRAM-Budget bei einer 8-GB-GPU** — so passt alles gleichzeitig:
   - Orpheus als **Q4_K_M-GGUF** laden (≈3 GB Gewichte, mit SNAC-Decoder und
     KV-Cache ≈5 GB) — nicht FP16/vLLM, das braucht 16 GB+. Das deutsche
     Modell: `lex-au/Orpheus-3b-Kartoffel` bzw. die GGUF-Variante im
     Orpheus-FastAPI-Setup.
   - Whisper-STT läuft absichtlich auf der **CPU** (`VOICE_STT_DEVICE = "cpu"`),
     damit es der Stimme kein VRAM wegnimmt (~1–2 s pro Push-to-Talk-Satz).
   - Kokoro (Englisch) läuft auf der CPU — kein VRAM.
   - Ollama (`qwen3:8b`, ~5–6 GB) passt **nicht gleichzeitig** neben Orpheus.
     Ollama entlädt Modelle standardmäßig nach 5 Minuten Leerlauf; wer beides
     nutzt, kann `OLLAMA_KEEP_ALIVE=1m` setzen. Die Sprachbefehle brauchen
     kein LLM (deterministischer Parser) — nur KI-Entwürfe und semantische
     Suche laden qwen3/Embeddings bei Bedarf.
3. **Englische Stimme (Kokoro, läuft auf CPU)**:
   `docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest`
4. Testen ohne App:

```bash
curl -s "http://127.0.0.1:8000/api/voice/morning-briefing" | python -m json.tool
curl -s -X POST http://127.0.0.1:8000/api/voice/command \
  -H "Content-Type: application/json" \
  -d '{"text": "Was steht heute an?"}' | python -m json.tool
```

Endpunkte: `POST /api/voice/transcribe` (Audio-Upload), `POST /api/voice/speak`
(Text → WAV), `POST /api/voice/command` (Text → Intent → Antwort),
`POST /api/voice/command-audio` (kompletter Push-to-Talk-Roundtrip),
`GET /api/voice/morning-briefing?speak=true`, `GET /api/voice/status`.

Verstandene Befehle (Deutsch und Englisch): Tagesbriefing („Was steht heute
an?“), Termine, Aufgabe erstellen („Erstelle Aufgabe: …“, „Erinnere mich
an …“), erledigen („X ist erledigt“), verschieben („Verschiebe X auf
morgen/nächste Woche“), Suche („Suche nach …“).

In der Mobile-App gibt es auf dem Home-Screen einen Push-to-Talk-Button
(halten zum Sprechen). Dafür ist ein neuer EAS-Build nötig (expo-av und
Mikrofon-Berechtigung sind neue native Bestandteile).

## 8) Morgen-Wecker (nativer Alarm mit gesprochenem Briefing)

Unter „Mehr“ in der Mobile-App gibt es den **Morgen-Wecker**: Zeit als
`HH:MM` eintragen und einschalten. Der Wecker klingelt täglich als echter
Alarm (Android: AlarmManager mit Vollbild-Benachrichtigung, klingelt auch
im Doze-Modus; iOS: zeitkritische Benachrichtigung — Drittanbieter-Apps
dürfen dort den Lautlos-Modus nicht übersteuern). Beim Auslösen oder
Antippen spielt Friday das gesprochene Tages-Briefing ab
(`/api/voice/morning-briefing`) — snooze-bewusst, in der App-Sprache.

„Briefing jetzt abspielen" testet die Kette sofort ohne zu warten.

Voraussetzungen:
- Neuer EAS-Build (Notifee ist ein natives Modul): in `friday-mobile/`
  `npm install` und dann `npm run build:android:preview`.
- Damit das Briefing auch unterwegs abgespielt werden kann, muss der
  Friday-Server erreichbar sein (Tailscale-IP ist in `app.json` als
  API-Kandidat eingetragen).
