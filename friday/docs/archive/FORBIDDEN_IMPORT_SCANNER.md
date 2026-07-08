# Forbidden Import Scanner

## Ziel

Lokaler AST-basierter Scanner fuer verbotene Imports in Python-Dateien.

## Umfang

- liest lokale Python-Quelldateien
- nutzt `ast.parse`
- fuehrt gescannte Dateien nicht aus
- importiert gescannte Module nicht
- schreibt keine Daten
- nutzt keine externen Dienste

## Blockierte Import-Roots

- `openai`
- `requests`
- `httpx`
- `twilio`
- `googleapiclient`
- `msgraph`
- `whatsapp`
- `smtplib`
- `imaplib`
- `poplib`
- `socket`

## Implementierte Bausteine

- `ForbiddenImportFinding`
- `ForbiddenImportScanResult`
- `scan_python_source_for_forbidden_imports`
- `scan_python_file_for_forbidden_imports`
- `scan_python_paths_for_forbidden_imports`

## Safety

- `preview_only=True`
- `persisted=False`
- `external_lookup_used=False`
- keine Netzwerkaktionen
- keine Modellaufrufe
- keine DB-Schreiboperation
- keine Produktlogik

## Tests

- `friday/tests/test_forbidden_import_scanner.py`

## Empfehlung

Naechster sinnvoller Schritt: No Network Scanner oder Integration des Forbidden Import Scanners in ein spaeteres Safety Smoke Script.
