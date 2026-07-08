# Pytest Runner Recovery Fix

## Ziel

Dieser Step verbessert den lokalen Windows-Test-Runner, damit reine Friday-Core-Tests nicht mehr versuchen, die kompletten API-/Service-Abhaengigkeiten zu installieren.

## Problem

`run_tests.bat` installierte bei fehlendem pytest bisher:

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` enthaelt inzwischen auch API-Abhaengigkeiten wie FastAPI und Uvicorn. Wenn Netzwerkzugriff oder API-Pakete nicht verfuegbar sind, blockiert das die reinen lokalen Friday-Tests.

## Aenderung

Neu:

- `requirements-test.txt` enthaelt nur die Test-Abhaengigkeit `pytest>=8.0,<9.0`.
- `run_tests.bat` installiert bei fehlendem pytest nur noch `requirements-test.txt`.
- `run_tests.bat` gibt bei Installationsfehlern eine klare Fehlermeldung aus.
- `run_tests.bat` unterstuetzt `--ci` und `--no-pause`, damit Validierung ohne Pause laufen kann.
- Der Exit-Code der pytest-Ausfuehrung wird korrekt zurueckgegeben.

## Geaenderte Dateien

| Datei | Zweck |
|---|---|
| `requirements-test.txt` | Minimale Test-Abhaengigkeiten fuer lokale Core-Tests |
| `run_tests.bat` | Windows-Test-Runner fuer `python -m pytest friday/tests` |

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine externen Friday-Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Validierung

Dieser Fix kann vollstaendig bestaetigt werden, sobald ein pytest-faehiger Python verfuegbar ist:

```bash
run_tests.bat --ci
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

Aktuell bleibt die vollstaendige pytest-Ausfuehrung in der Codex-Runner-Umgebung blockiert, weil der normale Windows-Shell-Runner mit `CreateProcessAsUserW failed: 5` nicht startet und der alternative Python kein pytest installiert hat.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Batch Selection CLI Apply Readiness Gate**, sobald `run_tests.bat --ci` oder `python -m pytest friday/tests` lokal erfolgreich laeuft.
