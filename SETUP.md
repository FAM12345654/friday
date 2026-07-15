# Friday Plattform-Setup (API, Mobile, Desktop)

## 0) Alles auf einmal starten

```bash
start_friday_stack.bat
```

Startet die geschützte Loopback-API (8001), Mobile und Desktop in separaten Fenstern.

Optionaler Check:

```bash
verify_friday_services.bat
```

Kontrolliert, ob Port `8001` nur lokal offen ist, die geschützten API-Endpunkte erreichbar sind und ob `friday-mobile/.env` die HTTPS-Geräteadresse enthält.

Ein-Befehl-Checkliste:

```bash
run_friday_checklist.bat
run_friday_checklist.bat --repair
run_friday_checklist.bat --start --repair
run_friday_checklist.bat --repair --mobile-release
run_friday_checklist.bat --install --repair --start
```

Die Checkliste kann Setup/Install ausführen, Shortcuts/Dateien prüfen, den Stack starten und danach die Service-Verifikation ausführen.
Mit `--repair` werden fehlende Shortcuts repariert und `friday-mobile/.env` mit `EXPO_PUBLIC_FRIDAY_API_URL=https://pc.tail4c6152.ts.net` angelegt, falls sie fehlt.
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
- Prüfe, ob Port `8001` von einem anderen Dienst belegt ist.
- Wenn Desktop im Stack läuft, nutzt er `FRIDAY_SKIP_EMBEDDED_API=1`, damit kein zweiter API-Prozess startet.

### Port 8001 ist belegt

- Stoppe den alten API-Prozess und starte den Stack neu.
- Alternativ kann der API-Port über `FRIDAY_API_PORT` im Desktop-Lauf geändert werden.

### Mobile kann nicht verbinden

- Prüfe `friday-mobile/.env` (`EXPO_PUBLIC_FRIDAY_API_URL`).
- Android/iOS/Tablet: `https://pc.tail4c6152.ts.net`
- Direkter LAN-HTTP-Zugriff ist absichtlich deaktiviert.

### Desktop startet nicht (Skip-API-Modus)

- `start_friday_desktop_skip_api.bat` erwartet einen laufenden API-Dienst auf `FRIDAY_API_PORT` (Standard `8001`).
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
cd ..
scripts\Start-Friday-API-Autostart.ps1 -Port 8001
```

Sicherstellen:

- Port 8001 frei
- `http://127.0.0.1:8001/health` liefert `{"ok":true,...}`
- Geschützte Routen benötigen `Authorization: Bearer <FRIDAY_API_TOKEN>`.
- CORS erlaubt die Mobile/Desktop-Origins (`FRIDAY_CORS_ORIGINS`)

## 2) Mobile (`friday-mobile`)

```bash
cd friday-mobile
npm install
copy .env.example .env
npm start
```

`EXPO_PUBLIC_FRIDAY_API_URL` muss auf die API zeigen:

Standard für ein physisches Handy: die HTTPS-Adresse von Tailscale Serve oder
einem abgesicherten Tunnel. Friday sendet API-Tokens nicht über unverschlüsseltes
WLAN-HTTP. Die aktuelle Geräteadresse ist `https://pc.tail4c6152.ts.net`.

Der vollstaendige Mobile-/Desktop-Guide steht hier:

```text
friday/docs/FRIDAY_MOBILE_DESKTOP_GUIDE.md
```

- Alle Geräte: `https://pc.tail4c6152.ts.net`
- Lokal bleibt die API ausschließlich auf `127.0.0.1:8001` gebunden.

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

- API Host/Port: `127.0.0.1:8001`
- Mobile/Simulator/Devices: geschütztes Tailscale-HTTPS verwenden
- Desktop: startet Backend intern über `FRIDAY_API_PORT` (Standard 8001)

### CORS

- Mobile + Desktop-Ziele in `friday-api/.env.example#FRIDAY_CORS_ORIGINS` pflegen.
- Wenn `FRIDAY_CORS_ORIGINS` leer ist, gelten nur die fest definierten lokalen Origins.

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
scripts/start_friday_api.sh        # API auf 127.0.0.1:8001
scripts/run_tests.sh               # friday/tests + friday-api/tests
scripts/start_whatsapp_bridge.sh   # WhatsApp-Bridge (npm install bei Bedarf)
```

Oder die API im Container:

```bash
docker compose up friday-api
```

## 6) Neue Funktionen (Kurzüberblick)

- **API-Token (für Netzwerkzugriff erforderlich)**: Ohne `FRIDAY_API_TOKEN`
  akzeptiert die API ausschließlich direkte Loopback-Anfragen. Für WLAN,
  Tailscale, Docker oder Tunnel einen zufälligen Token mit mindestens 32
  Zeichen setzen. Mobile speichert ihn unter **Mehr > Datenschutz** im
  Geräte-Keystore; Desktop übernimmt ihn aus der Prozessumgebung.
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
4. **Optionaler Voicebox-Pilot (nicht standardmäßig aktiv)**:
   Gemeint ist [jamiepine/voicebox](https://github.com/jamiepine/voicebox),
   der lokale Multi-Engine-Host — nicht Metas unveröffentlichtes
   Voicebox-Forschungsmodell. Voicebox ab v0.5 stellt WAV-Audio synchron über
   `POST /generate/stream` bereit und kann deshalb als Friday-TTS-Backend
   getestet werden.

   - Voicebox lokal auf `127.0.0.1:17493` starten.
   - In Voicebox ein deutsches Qwen-Base-Referenzprofil für Jana anlegen; die
     0.6B-Variante benötigt laut Voicebox ungefähr 2 GB VRAM. CustomVoice ist
     hierfür ungeeignet, weil es Preset-Stimmen statt Janas Referenzstimme nutzt.
   - In `friday/config.py` `VOICEBOX_DE_PROFILE_ID` setzen und danach
     `VOICE_TTS_DE_PROVIDER = "voicebox"` aktivieren. Englisch bleibt direkt
     auf Kokoro.
   - Orpheus/Kokoro bleibt der Standard, bis ein lokaler A/B-Hörtest Qualität,
     erste Audio-Latenz, Gesamt-Latenz und Stabilität auf dem Ziel-PC belegt.

   `/generate/stream` liefert Friday kompatibles WAV, puffert aber die gesamte
   Erzeugung vor der Antwort und ist kein echtes Low-Latency-Streaming.
   Voicebox ist kein automatisch besseres Modell, sondern bündelt mehrere
   Engines. Für Deutsch sind Qwen3-TTS und Chatterbox interessant; ein
   belastbarer direkter Benchmark gegen Orpheus-Kartoffel ist nicht
   veröffentlicht und muss deshalb mit Fridays echten Sätzen gemessen werden.

   Der reproduzierbare Benchmark läuft bewusst mit nur einer GPU-Engine pro
   Prozess. Zuerst Orpheus messen, anschließend Orpheus vollständig stoppen und
   erst dann Voicebox starten:

```powershell
python scripts\benchmark_voice_tts.py --engine orpheus --format json --output local_data\voice-bench-orpheus.json
python scripts\benchmark_voice_tts.py --engine voicebox --profile-id <PROFILE_ID> --model-size 0.6B --format json --output local_data\voice-bench-voicebox.json
```

   Der Harness akzeptiert ausschließlich Loopback-Endpunkte, folgt keinen
   Redirects und misst vollständige WAV-Latenz, p50/p95, WAV-Dauer, Real-Time-
   Factor und Fehlerrate. Für CSV `--format csv` verwenden.
5. Testen ohne App:

```bash
curl -s "http://127.0.0.1:8001/api/voice/morning-briefing" -H "Authorization: Bearer $FRIDAY_API_TOKEN" | python -m json.tool
curl -s -X POST http://127.0.0.1:8001/api/voice/command \
  -H "Authorization: Bearer $FRIDAY_API_TOKEN" \
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

Hinweis zum Neustart: Der Wecker richtet sich bei jedem App-Start
automatisch aus den gespeicherten Einstellungen neu ein. Nach einem
Neustart des Handys überleben die Benachrichtigungs-Trigger jedoch nicht
(Plattform-Grenze) — die App muss nach einem Reboot einmal geöffnet
werden, damit der Wecker wieder aktiv ist. Ein manuelles Aus-/Einschalten
ist dafür nicht mehr nötig.
