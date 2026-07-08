# Friday Local MVP Release Gate

## Status

`local_mvp_release_ready_with_documented_deferred_items`

Dieses Gate fasst den lokalen MVP-Stand von Friday zusammen.
Die App heisst Friday.

## Eingeschlossene Finalization Gates

| Gate | Status |
|---|---|
| `OBSIDIAN_BRAIN_FINALIZATION_GATE.md` | abgeschlossen |
| `LOCAL_AI_FINALIZATION_GATE.md` | abgeschlossen |
| `SELF_BUILDING_FINALIZATION_GATE.md` | abgeschlossen |

## Release Scope

Freigegeben:

- lokale CLI-/App-Funktionen mit SQLite-Speicher,
- Obsidian Brain Preview und guarded Write-Grenze,
- Local AI Mock/Preview/Validator/Logic-Check ohne Live Calls,
- Self-Building Preview ohne Runner- oder Git-Ausfuehrung,
- Backup/Restore/Import/Export nur innerhalb vorhandener lokaler Gates,
- Safety Smoke als lokaler Scanner-Verbund.

Nicht freigegeben:

- echte E-Mails,
- echtes WhatsApp,
- echte SMS,
- echte Kalenderaktionen,
- echte Wetter-/Musikaktionen,
- Cloud-Provider,
- externe AI-Modellaufrufe,
- Obsidian Write ohne Vault-, Flag-, Guard- und Token-Gate,
- Local-AI Live-Calls im Produktfluss,
- Self-Building Runner-Ausfuehrung ohne eigenes Gate,
- Git-Mutationen, Commits, Pushes oder Pull Requests ohne spaeteres eigenes Gate.

Ausdruecklich nicht Teil dieses lokalen MVP-Gates:

- EAS-/Expo-Builds,
- Mobile-Publish- oder Live-Update-Skripte,
- Cloudflare-Tunnel,
- externe API-URLs,
- Cloud-Provider-Konfiguration,
- Download- oder Publish-Kommandos.

Die Validierungsbefehle in diesem Dokument sind manuelle Release Evidence.
Sie sind keine Freigabe fuer den Self-Building-Runner.

## Safety Flags

Diese Flags muessen fuer das lokale MVP unveraendert bleiben:

| Flag | Erwarteter Wert |
|---|---|
| `ENABLE_REAL_EMAIL` | `False` |
| `ENABLE_REAL_WHATSAPP` | `False` |
| `ENABLE_REAL_SMS` | `False` |
| `ENABLE_REAL_CALENDAR` | `False` |
| `ENABLE_REAL_WEATHER` | `False` |
| `ENABLE_REAL_MUSIC` | `False` |
| `REQUIRE_USER_APPROVAL` | `True` |
| `USE_SQLITE_STORAGE` | `True` |
| `OBSIDIAN_WRITE_ENABLED` | `False` |
| `ENABLE_LOCAL_OLLAMA` | `False` |

## Validation Evidence

Stand: 2026-07-08

| Kommando | Ergebnis |
|---|---|
| `python -m pytest friday/tests` | `972 passed, 4 skipped` |
| `python -m compileall friday` | erfolgreich |
| `python scripts/friday_safety_smoke.py` | `Overall: PASS` |
| `git diff --check` | sauber |

## Bekannte Skips

Die vier Skips kommen aus Backup-/Restore-Symlink-Schutztests unter Windows:

- `test_backup_restore_path_safety.py`: Symlink-Erstellung fuer verbotenen Backup-/Restore-Pfad nicht erlaubt.
- `test_backup_writer.py`: Symlink-Erstellung fuer externe SQLite-Datei nicht erlaubt.
- `test_backup_writer.py`: Symlink-Erstellung fuer externe Markdown-Datei nicht erlaubt.
- `test_restore_dry_run.py`: Symlink-Erstellung fuer externen Restore-Testpfad nicht erlaubt.

Grund: Windows meldet `WinError 1314`, weil dem Client das erforderliche Recht zur Symlink-Erstellung fehlt.
Die Schutztests werden dadurch uebersprungen, nicht fehlgeschlagen.

## Windows Start / Setup

Die Windows-Start- und Setup-Doku bleibt in `README_USER.md` beschrieben:

- `setup_friday.bat`
- `start_friday.bat`
- `start_friday_stack.bat`
- `start_friday_desktop.bat`
- `start_friday_desktop_skip_api.bat`
- `run_tests.bat`
- `verify_friday_services_ci.bat`
- `verify_friday_shortcuts.bat`

Diese Release-Freigabe aktiviert keine neuen Windows-Autostarts, keine Cloud-Tunnel und keine mobilen Publish-Flows.

## Kanonische Doku-Quellen

- Architektur: `FRIDAY_ARCHITECTURE.md`
- Datenmodelle: `DATA_MODELS.md`
- Safety: `SAFETY_MATRIX.md`
- Nutzer-Doku: `README_USER.md`
- Developer Smoke: `cli_developer_smoke_guide_12j.md`

## Bekannte Deferred Items

| Bereich | Verschoben |
|---|---|
| Obsidian | Batch Write, Vault Sync History, Obsidian Cleanup |
| Local AI | Ollama Live Execution Gate, Produktfluss-Integration, Modell-Audit-Log |
| Self-Building | Runner-Ausfuehrung, Git Runtime Adapter, Commit Execution Gate |
| Release Safety | Standard-Smoke-Integration des JS-/PowerShell-/Package-Script-Netzwerkscanners; Preview und Readiness Gate sind vorhanden |
| API Hardening | lokale API-Auth/CORS-Haertung fuer spaetere Gates |
| Mobile/Cloud Scripts | Live-/Publish-/Tunnel-Skripte bleiben ausserhalb des lokalen MVP-Gates |

## Release Entscheidung

Friday ist lokal als MVP freigabefaehig, solange die Safety-Flags unveraendert bleiben und alle echten externen Aktionen, Modellaufrufe, Obsidian Writes und Self-Building-Ausfuehrungen weiter nur ueber eigene spaetere Gates geplant werden.
