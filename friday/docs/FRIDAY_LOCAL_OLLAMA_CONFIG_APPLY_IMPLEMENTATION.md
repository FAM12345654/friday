# Friday Local Ollama Config Apply Implementation

## Ziel

Dieser Schritt setzt den technischen Writer fuer lokale Ollama-Konfiguration um, ohne Friday automatisch auf Ollama umzuschalten.

## Umgesetzt

- Neuer isolierter Baustein: `friday/app/local_ollama_config_apply_writer.py`
- Neue Tests: `friday/tests/test_local_ollama_config_apply_writer.py`
- Schreiblogik nur fuer eine explizit uebergebene `config.py`
- Tests schreiben nur in `tmp_path`
- Die echte Projektdatei `friday/config.py` bleibt standardmaessig blockiert

## Erlaubte Schreibwerte

Der Writer darf nur diese vier Allowlist-Zeilen ersetzen:

```python
ENABLE_LOCAL_OLLAMA = True
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"
OLLAMA_TIMEOUT_SECONDS = 5
```

Andere Safety-Flags werden nicht veraendert.

## Blockierregeln

Der Writer blockiert, wenn:

- das Token nicht exakt `OLLAMA AKTIVIEREN` ist,
- Safety Smoke nicht als bestanden uebergeben wurde,
- Health Check nicht als bestanden uebergeben wurde,
- Modellname leer ist,
- Base-URL nicht lokal ist,
- `config.py` fehlt,
- Pflichtzeilen fehlen oder doppelt sind,
- die echte Projekt-`config.py` ohne separates Apply-Gate beschrieben werden soll.

## Safety-Bewertung

- Kein Cloud-Fallback.
- Kein API-Key.
- Kein Modellaufruf.
- Kein Versand.
- Keine Datenbankschema-Aenderung.
- Keine CLI- oder Mobile-Anbindung.
- Keine Aenderung an `friday/config.py`.
- `ENABLE_LOCAL_OLLAMA` bleibt im echten Projekt weiterhin `False`.

## Tests

Fokus-Tests:

```powershell
python -m pytest friday/tests/test_local_ollama_config_apply_writer.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_ai_task_forwarding_draft.py
```

Full Regression:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Local Ollama Config Apply Readiness Gate:

- Writer gegen Guard, Preview und Safety Smoke dokumentiert pruefen.
- Sicherstellen, dass echte Projekt-Config weiterhin nicht automatisch geschrieben wird.
- Erst danach entscheiden, ob ein separates Nutzer-Apply-Gate fuer die echte Projekt-Config gebaut wird.

Status danach: Das Readiness Gate ist in `FRIDAY_LOCAL_OLLAMA_CONFIG_APPLY_READINESS_GATE.md` dokumentiert.
