# No Network Scanner

## Ziel

Lokaler Scanner fuer direkte Netzwerk-Nutzungsmuster in Friday-Python-Dateien.

## Umfang

- liest lokale Python-Dateien
- nutzt AST
- erkennt bekannte Netzwerkaufrufe
- fuehrt keine Dateien aus
- importiert keine gescannten Module
- veraendert keine Dateien
- nutzt keine externen Dienste

## Erkannte Muster

- `requests.get`
- `requests.post`
- `requests.request`
- `httpx.get`
- `httpx.post`
- `httpx.Client`
- `httpx.AsyncClient`
- `urllib.request.urlopen`
- `urllib.request.Request`
- `socket.socket`
- `socket.create_connection`
- `aiohttp.ClientSession`
- `websocket.WebSocket`
- `websockets.connect`

## Implementierte Bausteine

- `NetworkUsageFinding`
- `NoNetworkScanResult`
- `scan_python_source_for_network_usage`
- `scan_python_file_for_network_usage`
- `scan_paths_for_network_usage`

## Safety

- keine Netzwerkaktionen
- keine Provideraufrufe
- keine Ausfuehrung gepruefter Dateien
- keine Produktlogik
- keine DB-Schreiboperation
- keine Obsidian-Schreiboperation

## Tests

- `test_no_network_scanner.py`

## Empfehlung

Naechster sinnvoller Schritt:

No Input/Print Scanner oder Scanner Smoke Script.
