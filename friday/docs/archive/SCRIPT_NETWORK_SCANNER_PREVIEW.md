# Script Network Scanner Preview

## Ziel

Dieser Scanner bereitet eine lokale Preview fuer Netzwerk-Muster in JavaScript-, PowerShell- und `package.json`-Skripten vor.

Er fuehrt keine Skripte aus.

## Gepruefte Flaechen

| Flaeche | Beispiele |
|---|---|
| JavaScript / TypeScript | `fetch`, `XMLHttpRequest`, `axios`, `WebSocket`, `http://`, `https://` |
| PowerShell | `Invoke-WebRequest`, `Invoke-RestMethod`, `curl`, `cloudflared`, `npx eas` |
| Batch / CMD | `curl`, `powershell`, `cloudflared`, `npx eas`, external URLs |
| `package.json` scripts | `eas`, `expo publish`, `expo export`, `cloudflared`, `curl` |

## Safety

- Preview-only.
- Keine Ausfuehrung gescannter Dateien.
- Keine Netzwerkaktion.
- Keine Provideraufrufe.
- Keine Datei- oder Datenbankwrites.
- `node_modules`, `.cache`, `cache`, Caches, Build- und Dist-Ordner werden uebersprungen.

## Aktueller Scope

Der Scanner ist noch nicht Teil des Standard-Safety-Smoke.

Grund:
Im Repository existieren bekannte Mobile-/Publish-/Cloudflare-Pfade, die fuer das lokale MVP ausdruecklich ausserhalb des Release-Gates liegen.
Ein spaeteres Gate muss entscheiden, ob diese Pfade allowlisted, ausgelagert oder blockierend in den Smoke aufgenommen werden.

## Readiness Gate

Das zugehoerige Gate ist `SCRIPT_NETWORK_SCANNER_READINESS_GATE.md`.

Status:

`preview_ready_standard_smoke_blocked`

Das Gate bestaetigt nur bounded Preview-Scans.
Standard-Safety-Smoke-Integration bleibt blockiert.

## Boundary Checks

- `project_root` begrenzt Scan-Kandidaten auf einen lokalen Projektbaum.
- `DEFAULT_MAX_SCRIPT_FILE_BYTES` begrenzt einzelne Dateien auf `1000000` Bytes.
- Dateien ausserhalb des Projekt-Roots oder oberhalb des Size-Limits werden uebersprungen.

## Tests

- `friday/tests/test_script_network_scanner.py`

## Nicht freigegeben

- Mobile Publish.
- EAS-/Expo-Builds.
- Cloudflare-Tunnel.
- Download-Kommandos.
- Runtime-Ausfuehrung von JS-/PowerShell-/Package-Skripten.
