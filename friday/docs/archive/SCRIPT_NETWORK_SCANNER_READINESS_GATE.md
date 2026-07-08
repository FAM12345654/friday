# Script Network Scanner Readiness Gate

## Status

`preview_ready_standard_smoke_blocked`

Dieses Gate bewertet den lokalen Script Network Scanner fuer Friday.
Es aktiviert keine Standard-Safety-Smoke-Integration.

## Scope

Freigegeben ist nur ein bounded Preview-Scan:

- lokaler Projekt-Root muss explizit gesetzt sein,
- einzelne Script-Dateien muessen unterhalb des Size-Limits liegen,
- erkannte Kandidaten werden nur als Text gelesen,
- `package.json`-Scripts werden nur geparst,
- PowerShell-, Batch- und JavaScript-Dateien werden nicht ausgefuehrt.

## Safety Flags

Dieses Gate aendert keine Safety-Flags.

## Runtime Safety

| Eigenschaft | Status |
|---|---|
| Preview-only | ja |
| Lokaler Scope | ja |
| Script-Ausfuehrung | nein |
| Netzwerkaktion | nein |
| Persistenz | nein |
| Externe Lookups | nein |
| Standard-Smoke-Integration | blockiert |

## Boundary Rules

- `project_root` begrenzt Kandidaten per kanonischem Pfadvergleich.
- Kandidaten ausserhalb des Projekt-Roots werden uebersprungen.
- `DEFAULT_MAX_SCRIPT_FILE_BYTES` ist `1000000`.
- Dateien oberhalb des Size-Limits werden uebersprungen.
- Cache-, Build-, Dist-, Venv-, Git- und `node_modules`-Pfade bleiben ausgeschlossen.

## Blocked Reasons

Das Gate blockiert, wenn:

- kein Projekt-Root gesetzt ist,
- kein positives Size-Limit gesetzt ist,
- Standard-Smoke-Integration angefordert wird,
- keine separate Smoke-Allowlist vorhanden ist.

## Nicht freigegeben

- Standard-Safety-Smoke-Integration.
- Blockierender Repo-weiter Script-Network-Smoke.
- Ausfuehrung von `npm`, `npx`, `eas`, `cloudflared`, `curl` oder PowerShell.
- Mobile Publish, EAS/Expo Build, Live Update oder Cloudflare Tunnel.

## Tests

- `friday/tests/test_script_network_scanner.py`

## Naechstes Gate

Vor einer Standard-Smoke-Integration braucht Friday ein separates:

`SCRIPT_NETWORK_SCANNER_STANDARD_SMOKE_GATE`

Dieses spaetere Gate muss Scope, Allowlist, False-Positive-Handling und Mobile/EAS/Cloudflare-Ausnahmen bewusst entscheiden.
