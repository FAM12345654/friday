# Friday Local MVP Release Closure

## Status

`chat_3_release_gate_closed`

Release-Status:

`local_mvp_release_ready_with_documented_deferred_items`

Chat 3 hat die lokalen MVP-Gates fuer Obsidian Brain, Local AI, Self-Building Preview und Release-Dokumentation abgeschlossen.
Die App heisst Friday.

## Geschlossene Gates

| Gate | Status |
|---|---|
| `OBSIDIAN_BRAIN_FINALIZATION_GATE.md` | geschlossen |
| `LOCAL_AI_FINALIZATION_GATE.md` | geschlossen |
| `SELF_BUILDING_FINALIZATION_GATE.md` | geschlossen |
| `FRIDAY_LOCAL_MVP_RELEASE_GATE.md` | geschlossen |

## Finale Release Evidence

Stand: 2026-07-08

| Kommando | Ergebnis |
|---|---|
| `python -m pytest friday/tests` | `972 passed, 4 skipped` |
| `python -m compileall friday` | erfolgreich |
| `python scripts/friday_safety_smoke.py` | `Overall: PASS` |
| `git diff --check` | sauber |

## Bekannte Skips

Die vier Skips sind Windows-Symlink-Rechtefaelle in Backup-/Restore-Schutztests.
Windows meldet `WinError 1314`, wenn der aktuelle Nutzer keine Symlinks erstellen darf.
Das ist fuer das lokale MVP kein Release-Blocker.

## Lokale MVP-Grenzen

Freigegeben ist nur die lokale MVP-Nutzung.

- Python-only Produktpfad.
- SQLite ueber Python-Standardbibliothek `sqlite3`.
- Keine Cloud-Datenbank.
- Kein ORM.
- Kein externer Datenbankserver.
- Keine echten externen Aktionen.
- Keine echten AI-Modellaufrufe.
- Keine Self-Building-Ausfuehrung.
- Keine Git-Mutation.

## Safety-Abbruchregeln

Release bleibt blockiert, wenn eine dieser Grenzen verletzt wird:

- `ENABLE_REAL_EMAIL` ist nicht `False`.
- `ENABLE_REAL_WHATSAPP` ist nicht `False`.
- `ENABLE_REAL_SMS` ist nicht `False`.
- `ENABLE_REAL_CALENDAR` ist nicht `False`.
- `ENABLE_REAL_WEATHER` ist nicht `False`.
- `ENABLE_REAL_MUSIC` ist nicht `False`.
- `REQUIRE_USER_APPROVAL` ist nicht `True`.
- `USE_SQLITE_STORAGE` ist nicht `True`.
- `OBSIDIAN_WRITE_ENABLED` ist nicht `False`.
- `ENABLE_LOCAL_OLLAMA` ist nicht `False`.

## Nicht freigegeben

- E-Mail senden.
- WhatsApp senden.
- SMS senden.
- Kalenderaktionen ausfuehren.
- Wetter- oder Musikaktionen ausfuehren.
- Cloud-Provider nutzen.
- OpenAI-, Anthropic- oder andere Cloud-Modellaufrufe.
- Ollama Live-Calls im Produktfluss.
- Obsidian Write ohne Vault-, Flag-, Guard- und Token-Gate.
- Automatischer Obsidian Batch Write.
- Self-Building Runner-Ausfuehrung.
- Arbitrary Shell Commands.
- `git add`, `git commit`, `git push`, `git pull`, Branch-Wechsel, Reset/Revert oder Pull Request Erstellung.
- EAS-/Expo-Builds, Mobile-Publish, Live-Updates oder Cloudflare-Tunnel als Teil dieses lokalen Gates.

## Kanonische Dokuquellen

| Thema | Datei |
|---|---|
| Architektur | `FRIDAY_ARCHITECTURE.md` |
| Datenmodelle | `DATA_MODELS.md` |
| Safety Matrix | `SAFETY_MATRIX.md` |
| Test Matrix | `TEST_MATRIX.md` |
| Build History | `BUILD_HISTORY.md` |
| Nutzer-Doku | `README_USER.md` |
| Developer Smoke | `cli_developer_smoke_guide_12j.md` |

## Deferred Items

Diese Punkte sind bewusst verschoben und brauchen eigene spaetere Gates:

- Obsidian Batch Write, Vault Sync History und Obsidian Cleanup.
- Ollama Live Execution Gate und Local-AI-Produktfluss-Integration.
- Modell-Audit-Log.
- Self-Building Runner Execution Gate.
- Git Runtime Adapter.
- Commit Execution Gate.
- Standard-Smoke-Integration des JS-/PowerShell-/Package-Script-Netzwerkscanners.
- Scope-/Allowlist-Gate fuer Script Network Scanner Standard-Smoke.
- API-Auth/CORS-Haertung.
- Mobile/EAS/Expo/Cloudflare Release-Pfade.

## Handoff

Naechster Chat oder naechster Build-Block kann auf diesem Stand starten:

1. `FRIDAY_LOCAL_MVP_RELEASE_GATE.md` als aktuelle Release-Entscheidung lesen.
2. `BUILD_HISTORY.md` fuer die letzte Evidence lesen.
3. `SAFETY_MATRIX.md` vor jeder neuen Write- oder Integrationserweiterung pruefen.
4. Fuer jeden deferred Bereich ein eigenes Plan-/Readiness-Gate erstellen.
5. Keine Safety-Flags, Delete-Policy oder externen Aktionen ohne eigenes Gate aendern.

## Ergebnis

Chat 3 ist fuer das lokale MVP geschlossen.
Friday bleibt lokal, guarded und release-dokumentiert.
