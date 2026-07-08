# Scanner Smoke Script

## Ziel

Lokaler Sammelcheck fuer Friday-Safety-Scanner.

## Befehl

```powershell
python scripts/friday_safety_smoke.py
```

## Enthaltene Checks

- Forbidden Import Scanner
- No Network Scanner
- No Input/Print Scanner
- Safety Flag Regression Scanner
- Approval Token Scanner

Nicht im Standard-Smoke enthalten:

- Script Network Scanner Preview fuer JS/PowerShell/Batch/`package.json`

Grund: Im lokalen Projekt existieren bekannte Mobile-/Publish-/Cloudflare-Skripte. Diese bleiben ausserhalb des lokalen Friday-Release-Gates, bis ein eigenes Script-Surface-Gate entscheidet, ob sie allowlisted, ausgelagert oder blockierend gescannt werden.

## Verhalten

- gibt PASS/FAIL pro Scanner aus
- gibt Gesamtstatus aus
- Exit-Code `0` bei PASS
- Exit-Code `1` bei FAIL
- nutzt eng definierte Ausnahmen fuer bekannte interaktive CLI-Dateien und Scanner-Definitionen:
  - `friday/agents/approval_agent.py`
  - `friday/app/interface.py`
  - `friday/app/menu.py`
  - `friday/agents/message_agent.py`
  - `friday/app/approval_token_scanner.py`
- prueft harte Tokens inklusive `PERSON VERGESSEN`, `BACKUP ERSTELLEN`, `RESTORE AUSFUEHREN`, `DATEN EXPORTIEREN`, `IMPORT ANWENDEN`, `EXPORT AUFRAEUMEN`, `BACKUP AUFRAEUMEN`, `RESTORE AUFRAEUMEN` und `REVIEW AUFRAEUMEN`

## Safety

- keine Netzwerkaktionen
- keine Provideraufrufe
- keine Ausfuehrung gescannter Dateien
- keine Produktlogik
- keine DB-Schreiboperation
- keine Obsidian-Schreiboperation

## Tests

- `test_scanner_smoke_script.py`

## Empfehlung

Dieses Script sollte vor riskanteren Build-Steps lokal ausgefuehrt werden.
