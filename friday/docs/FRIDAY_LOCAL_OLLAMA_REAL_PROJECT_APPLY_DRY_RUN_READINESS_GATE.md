# Friday Local Ollama Real Project Apply Dry Run Readiness Gate

## Ziel

Dieses Gate prueft den Dry-Run-Baustein fuer einen spaeteren echten Apply auf
`friday/config.py`.

Das Gate bestaetigt nur die Readiness. Es schreibt nichts und aktiviert Ollama
nicht.

## Gepruefte Bausteine

| Baustein | Ergebnis |
|---|---|
| `friday/app/local_ollama_real_project_apply_dry_run.py` | vorhanden, read-only, zeigt geplante Aenderungen |
| `friday/app/local_ollama_real_project_apply_guard.py` | vorhanden, read-only Guard fuer Projekt-Config |
| `friday/app/local_ollama_config_apply_writer.py` | vorhanden, isolierter Writer; echter Projekt-Write standardmaessig blockiert |
| `friday/tests/test_local_ollama_real_project_apply_dry_run.py` | vorhanden, prueft Dry Run ohne Write |
| `friday/config.py` | unveraendert, `ENABLE_LOCAL_OLLAMA = False` |

## Readiness-Ergebnis

- Dry Run ist umgesetzt.
- Geplante Config-Zeilen werden angezeigt.
- Rollback-Zeilen werden angezeigt.
- Blockierende Guard-Gruende werden angezeigt.
- Kein Write auf `friday/config.py`.
- Keine Backup- oder Temp-Datei.
- Kein Produkt-Apply.

## Weiterhin blockiert

- echter Write auf `friday/config.py`,
- automatische Ollama-Aktivierung,
- API-/CLI-/Mobile-Apply,
- Modellaufruf ohne separates Gate,
- Cloud-Fallback,
- echte externe Aktionen.

## Safety-Bewertung

- Keine externen Aktionen.
- Kein echter Modellaufruf.
- Kein Cloud-KI-Fallback.
- Kein API-Key.
- Kein Versand.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.
- Safety-Flags bleiben unveraendert.
- `ENABLE_LOCAL_OLLAMA` bleibt im echten Projekt `False`.

## Validierung

Fokus-Tests:

```powershell
python -m pytest friday/tests/test_local_ollama_real_project_apply_dry_run.py friday/tests/test_local_ollama_real_project_apply_guard.py friday/tests/test_local_ollama_config_apply_writer.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_ai_task_forwarding_draft.py
```

Full Regression:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

Zuletzt dokumentierter Stand:

- Fokus-Tests: `40 passed`
- Full Regression: `1139 passed, 4 skipped`
- Compilecheck: erfolgreich
- Safety Smoke: `PASS`
- Diff-Check: sauber

## Entscheidung

Der Dry Run ist readiness-geprueft.

Nicht freigegeben ist weiterhin:

- echter Write,
- echtes Aktivieren von Ollama,
- API-/CLI-/Mobile-Apply.

## Empfehlung fuer den naechsten Build Step

Local Ollama Real Project Apply Execution Plan:

- den echten Apply-Schritt als finalen Ablauf planen,
- Validierungs- und Rollback-Punkte nochmals festlegen,
- weiterhin keinen Write in der Planungsrunde ausfuehren.
