# Friday Local Ollama Real Project Apply Implementation Readiness Gate

## Ziel

Dieses Gate prueft den isolierten echten Apply-Baustein fuer einen lokalen
Ollama-Apply.

Das Gate fuehrt keinen Apply aus und verbindet den Baustein nicht mit CLI, API
oder Mobile.

## Gepruefte Bausteine

| Baustein | Ergebnis |
|---|---|
| `friday/app/local_ollama_real_project_apply.py` | vorhanden, isolierter Apply-Baustein |
| `friday/app/local_ollama_real_project_apply_dry_run.py` | vorhanden, Dry Run ohne Write |
| `friday/app/local_ollama_real_project_apply_guard.py` | vorhanden, read-only Projekt-Config-Guard |
| `friday/app/local_ollama_config_apply_writer.py` | vorhanden, Config Writer mit Allowlist-Zeilen |
| `friday/tests/test_local_ollama_real_project_apply.py` | vorhanden, Tests schreiben nur auf `tmp_path` |
| `friday/config.py` | unveraendert, `ENABLE_LOCAL_OLLAMA = False` |

## Readiness-Ergebnis

- Der Apply-Baustein ist isoliert umgesetzt.
- Der Apply-Baustein braucht explizit `execute_write=True`.
- Der Apply-Baustein braucht eine Post-Write-Validation.
- Bei fehlgeschlagener Validation wird Rollback ausgefuehrt.
- Tests schreiben nur temporaere `config.py`-Dateien unter `tmp_path`.
- Es gibt keine Produktanbindung an CLI, API oder Mobile.
- Die echte Projekt-`config.py` wurde nicht geaendert.

## Weiterhin blockiert

- automatischer Apply beim Start,
- CLI-Menuepunkt fuer echten Apply,
- API-Endpunkt fuer echten Apply,
- Mobile-Button fuer echten Apply,
- echter Write auf die aktuelle Projekt-`config.py` in diesem Gate,
- Modellaufruf ohne separaten lokalen Runtime-/Health-Gate,
- Cloud-Fallback,
- echte externe Aktionen.

## Safety-Bewertung

- Keine externen Aktionen.
- Kein echter Modellaufruf.
- Kein Cloud-KI-Fallback.
- Kein API-Key.
- Kein Versand.
- Keine Kalenderaktion.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.
- Safety-Flags bleiben unveraendert.
- `ENABLE_LOCAL_OLLAMA` bleibt im echten Projekt `False`.

## Validierung

Fokus-Tests:

```powershell
python -m pytest friday/tests/test_local_ollama_real_project_apply.py friday/tests/test_local_ollama_real_project_apply_dry_run.py friday/tests/test_local_ollama_real_project_apply_guard.py friday/tests/test_local_ollama_config_apply_writer.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_ai_task_forwarding_draft.py
```

Full Regression:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

Zuletzt dokumentierter Stand:

- Fokus-Tests: `46 passed`
- Full Regression: `1145 passed, 4 skipped`
- Compilecheck: erfolgreich
- Safety Smoke: `PASS`
- Diff-Check: sauber

## Entscheidung

Der isolierte Apply-Baustein ist readiness-geprueft.

Nicht freigegeben ist weiterhin:

- Produktanbindung,
- automatischer Apply,
- echter Apply auf die aktuelle Projekt-`config.py` ohne ausdrueckliche manuelle Entscheidung.

## Empfehlung fuer den naechsten Build Step

Local Ollama Manual Activation Decision Gate:

- entscheiden, ob die lokale Ollama-Aktivierung jetzt wirklich manuell
  ausgefuehrt werden soll,
- vorher Ollama lokal pruefen,
- weiterhin keine externen Aktionen,
- bei Nein bleibt Friday im Mock-Modus.
