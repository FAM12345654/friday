# Safety Scanner Finalization Gate

## Ziel

Dieses Gate friert den lokalen Safety-Scanner-Stand fuer Friday als releasefaehigen Standard-Smoke ein.

## Standard-Smoke

Der Befehl lautet:

```powershell
python scripts/friday_safety_smoke.py
```

Der Standard-Smoke enthaelt diese Checks in fester Reihenfolge:

1. `forbidden_imports`
2. `no_network`
3. `no_input_print`
4. `safety_flags`
5. `approval_tokens`

## Approval Token Coverage

Der Approval-Token-Scanner prueft diese harten Tokens:

- `SPEICHERN`
- `KONTAKT LÖSCHEN`
- `PERSON VERGESSEN`
- `OBSIDIAN SCHREIBEN`
- `BACKUP ERSTELLEN`
- `RESTORE AUSFUEHREN`
- `DATEN EXPORTIEREN`
- `IMPORT ANWENDEN`
- `EXPORT AUFRAEUMEN`
- `BACKUP AUFRAEUMEN`
- `RESTORE AUFRAEUMEN`
- `REVIEW AUFRAEUMEN`
- `COMMIT ERSTELLEN`

Weiche Tokens wie `ja`, `JA`, `ok`, `yes`, `speichern`, `loeschen`, `löschen`, `write`, `schreiben`, `confirm`, `bestätigen` und `bestaetigen` bleiben blockierend, sofern sie nicht ausdruecklich fuer Legacy-Delete-Policy-Kompatibilitaet allowlisted sind.

## Lokale Safety-Grenzen

- Scanner lesen nur lokale Dateien.
- Scanner fuehren gescannte Dateien nicht aus.
- Scanner importieren gescannte Module nicht.
- Scanner schreiben keine Dateien.
- Scanner schreiben keine Datenbank.
- Scanner rufen keine Provider auf.
- Scanner starten keine Netzwerkaktionen.
- Scanner starten keine AI-Modellaufrufe.
- Safety-Flags bleiben unveraendert.

## Bewusst ausserhalb des Standard-Smoke

Der Script Network Scanner Preview fuer JS, PowerShell, Batch/CMD und `package.json` bleibt preview-only und ist nicht Teil des Standard-Smoke.

Grund: Im lokalen Projekt existieren bekannte Mobile-/Publish-/Cloudflare-Skripte, die nicht zum lokalen Friday-Release-Gate gehoeren. Ein spaeteres Script-Surface-Gate muss entscheiden, ob diese Pfade allowlisted, ausgelagert oder blockierend in den Smoke aufgenommen werden.

## Optionaler Markdown Link Checker Plan

Ein spaeterer Markdown Link Checker darf nur lokal arbeiten:

- keine HTTP-Requests,
- keine Netzwerkvalidierung,
- keine Auto-Fixes,
- keine Writes ohne separates Gate,
- Pruefung nur auf lokale Anker, relative Doku-Dateien und offensichtliche kaputte interne Links.

Der Checker ist in diesem Gate geplant, aber nicht implementiert.

## Validierung

Fokus:

```powershell
python -m pytest friday/tests/test_approval_token_scanner.py friday/tests/test_scanner_smoke_script.py friday/tests/test_forbidden_import_scanner.py friday/tests/test_no_network_scanner.py friday/tests/test_no_input_print_scanner.py friday/tests/test_safety_flag_regression_scanner.py friday/tests/test_script_network_scanner.py
```

Pflicht:

```powershell
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Gate Status

Freigegeben fuer lokalen Release-Kandidaten, solange der Standard-Smoke PASS bleibt und neue riskante Scanner-Surfaces ein eigenes Gate bekommen.
