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

- Emulator (Android): `http://10.0.2.2:8000`
- Simulator (iOS): `http://127.0.0.1:8000`
- Physisches Gerät: `http://<pc-lan-ip>:8000`

### Handy-Download und automatische Updates

Für eine installierbare Handy-Version nutzt Friday Mobile EAS Build mit interner Distribution. Der Android-Preview-Build erzeugt eine direkt installierbare APK über einen EAS-Link.

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
