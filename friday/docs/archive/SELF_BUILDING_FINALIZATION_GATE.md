# Self-Building Finalization Gate

## Status

`finalized_preview_ready_execution_disabled`

Der Self-Building-Block ist als lokaler Preview- und Safety-Gate-Block vorbereitet.
Friday fuehrt daraus keine Runner-, Git- oder Commit-Aktion aus.

## Abgeschlossene Checks

| Check | Status |
|---|---|
| Build Queue Preview | abgeschlossen |
| Test Runner Allowlist Preview | abgeschlossen |
| Git Status Viewer Preview | abgeschlossen |
| Commit Draft Preview | abgeschlossen |
| Hard Token fuer spaeteren Commit | abgeschlossen |
| Keine Runner-Ausfuehrung | abgeschlossen |
| Keine Git-Mutation | abgeschlossen |

## Erlaubte Test-Runner-Kommandos

Diese Kommandos sind nur als Allowlist fuer spaetere Ausfuehrungs-Gates dokumentiert:

- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

Das Preview-Modell fuehrt sie nicht aus.

## Read-only Git Viewer

Diese Git-Kommandos sind nur als read-only Viewer-Grenze dokumentiert:

- `git status --short`
- `git diff --stat`
- `git diff --check`

Nicht freigegeben:

- `git add`
- `git commit`
- `git push`
- `git pull`
- Branch-Wechsel
- Reset/Revert
- Pull Request Erstellung

## Commit Draft und harter Token

Commit Drafts sind nur Textvorschlaege.
Ein spaeterer Commit-Ausfuehrungspfad braucht ein eigenes Gate und den exakten Token:

```text
COMMIT ERSTELLEN
```

`JA`, `ok`, leere Eingaben oder weiche Bestaetigungen reichen nicht.

## Nicht freigegeben

- Arbitrary Shell Commands.
- Test Runner ohne Allowlist.
- Shell-Metazeichen oder verkettete Kommandos.
- Git-Mutationen.
- Commit-Ausfuehrung.
- Push oder Pull Request Erstellung.
- Netzwerkaktionen.
- Automatische Code-Aenderungen aus Modell-Ausgaben.

## Ausdruecklich ausserhalb des Safe-Runners

Diese vorhandenen Projektpfade duerfen nicht Teil eines Self-Building-Test-Runners sein:

- Mobile-Live- oder Publish-Skripte.
- Cloudflare-Tunnel-Skripte.
- EAS-/Expo-Publish- oder Build-Kommandos.
- `curl`, `Invoke-WebRequest` oder andere Download-Kommandos.
- `git add`, `git commit`, `git push`, `git pull`, `git reset`, `git checkout`.

## Tests

- `friday/tests/test_self_building_preview.py`
- `friday/tests/test_approval_token_scanner.py`
- `friday/tests/test_scanner_smoke_script.py`

## Validierung

Vor Release-Freigabe dieses Blocks:

```powershell
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Release Evidence

Stand: 2026-07-08

| Kommando | Ergebnis |
|---|---|
| `python -m pytest friday/tests` | `908 passed, 2 skipped` |
| `python -m compileall friday` | erfolgreich |
| `python scripts/friday_safety_smoke.py` | `Overall: PASS` |
| `git diff --check` | sauber |

## Ergebnis

Self-Building ist lokal als MVP-Preview-Block vorbereitet.
Ausfuehrung, Git-Mutation und echte Commits bleiben deaktiviert und brauchen spaetere eigene Gates.
