# No Input / Print Scanner

## Ziel

Lokaler Scanner fuer direkte `input()`- und `print()`-Nutzung in isolierten Friday-Python-Modulen.

## Umfang

- liest lokale Python-Dateien
- nutzt AST
- erkennt direkte `input()`-Calls
- erkennt direkte `print()`-Calls
- erkennt einfache `builtins`-Aliase
- fuehrt keine Dateien aus
- importiert keine gescannten Module
- veraendert keine Dateien
- nutzt keine externen Dienste

## Erkannte Muster

- `input(...)`
- `print(...)`
- `builtins.input(...)`
- `builtins.print(...)`
- `from builtins import input as ...`
- `from builtins import print as ...`

## Ausnahmen

Der Standard-Smoke schliesst diese bekannten interaktiven CLI-Dateien aus:

- `friday/agents/approval_agent.py`
- `friday/app/interface.py`
- `friday/app/menu.py`

Andere isolierte Module bleiben im No-Input/Print-Scanner blockierend.

## Implementierte Bausteine

- `InputPrintFinding`
- `NoInputPrintScanResult`
- `scan_python_source_for_input_print`
- `scan_python_file_for_input_print`
- `scan_paths_for_input_print`

## Safety

- keine Netzwerkaktionen
- keine Provideraufrufe
- keine Ausfuehrung gepruefter Dateien
- keine Produktlogik
- keine DB-Schreiboperation
- keine Obsidian-Schreiboperation

## Tests

- `test_no_input_print_scanner.py`

## Empfehlung

Naechster sinnvoller Schritt:

Safety Flag Regression Scanner oder Scanner Smoke Script.
