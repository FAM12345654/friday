# Friday Desktop (Electron)

## Setup

```bash
cd friday-desktop
npm install
```

## Start

Mit dem zentralen Startskript:

```bash
cd ..
start_friday_stack.bat
```

oder nur Desktop:

```bash
npm run dev
```

oder Desktop ohne eingebetteten API-Start:

```bash
cd ..
start_friday_desktop_skip_api.bat
```

Der Electron-Prozess startet den API-Server im Projekt-Root standardmäßig via:

`python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

Im Stack-Modus (`start_friday_stack.bat`) wird der eingebettete API-Start übersprungen, weil der API-Dienst separat läuft.

## UI-Zielbild

- Dashboard
- Tasks
- Nachrichten / Vorschläge
- Kalender
- Kontakte
- Datenschutz

## Optionale Umgebungsvariablen

- `FRIDAY_API_HOST` (Server-Hinrichtung, Standard: `0.0.0.0`)
- `FRIDAY_API_PORT` (Server-Hinrichtung, Standard: `8000`)
- `FRIDAY_API_CLIENT_HOST` (Renderer-Ziel für API-Aufrufe, Standard: `127.0.0.1`)
- `FRIDAY_PYTHON` (Python-Binary, Standard: `python`)
- `FRIDAY_SKIP_EMBEDDED_API` (setzt den eingebetteten API-Start aus, z. B. `1` oder `true`)
