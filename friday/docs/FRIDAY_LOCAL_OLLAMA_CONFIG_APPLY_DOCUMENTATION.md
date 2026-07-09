# Friday Local Ollama Config Apply Documentation

## Ziel

Dieses Dokument beschreibt, welche lokale Konfigurationsaenderung spaeter noetig waere, um Friday auf lokales Ollama vorzubereiten.
Es ist eine Anleitung, kein automatischer Apply-Schritt.

## Wichtig

In diesem Schritt wurde nichts aktiviert:

- `config.py` wurde nicht geaendert.
- `ENABLE_LOCAL_OLLAMA` bleibt `False`.
- `OLLAMA_MODEL` bleibt leer.
- Es wurde kein Ollama-Modell aufgerufen.
- Es wurde kein Cloud-Modell eingebunden.
- Es wurde keine Nachricht gesendet.

## Aktueller Implementierungsstand

- `FRIDAY_LOCAL_OLLAMA_CONFIG_APPLY_IMPLEMENTATION_PLAN.md` dokumentiert den sicheren Apply-Ablauf.
- `FRIDAY_LOCAL_OLLAMA_CONFIG_APPLY_IMPLEMENTATION.md` beschreibt den isolierten Writer.
- Der Writer schreibt in Tests nur auf `tmp_path`.
- Die echte Projekt-`config.py` bleibt ohne separates Apply-Gate blockiert.

## Voraussetzungen vor einer spaeteren manuellen Aenderung

Vor jeder echten manuellen Aktivierung muessen alle Punkte erfuellt sein:

- Ollama ist lokal installiert.
- Ein lokales Modell ist geladen, z. B. `llama3.1`.
- `GET /api/ai/ollama/config-preview` ist fuer das Modell gruen.
- `POST /api/ai/ollama/config-apply-gate` liefert `allowed=True`.
- Safety Smoke ist gruen.
- Der lokale Health Check ist gruen.
- Der Nutzer bestaetigt bewusst mit `OLLAMA AKTIVIEREN`.

## Manuelle Config-Zeilen

Aktueller sicherer Standard in `friday/config.py`:

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

Spaetere manuelle Zielkonfiguration fuer ein lokales Modell:

```python
ENABLE_LOCAL_OLLAMA = True
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"
OLLAMA_TIMEOUT_SECONDS = 5
```

Diese Aenderung darf erst in einem separaten technischen Apply-Schritt erfolgen.

## Rueckfall-Regel

Auch nach einer spaeteren Aktivierung muss Friday weiter sicher zurueckfallen:

- Ollama nicht erreichbar -> Mock Provider
- Modell leer -> Mock Provider
- Health Check fehlgeschlagen -> Mock Provider
- nicht-lokale URL -> blockiert
- Validator blockiert Antwort -> sicherer Fallback-Draft

## Verbotene Varianten

Nicht verwenden:

```python
OLLAMA_BASE_URL = "https://..."
OLLAMA_BASE_URL = "http://example.com"
OLLAMA_MODEL = ""
```

Ebenfalls nicht erlaubt:

- OpenAI-/Claude-/Anthropic-Keys
- Cloud-Fallback
- echte E-Mail-/WhatsApp-Sends
- automatisches Schreiben von `config.py` ohne separates Gate

## Tests vor einem spaeteren Apply

```powershell
python -m pytest friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_ai_task_forwarding_draft.py
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Nach einem spaeteren Apply

Nach einem separaten Apply-Schritt muss geprueft werden:

- `GET /api/ai/status?run_health_check=true`
- Task-Weiterleiten-Draft mit lokalem Ollama
- Fallback auf Mock, wenn Ollama gestoppt wird
- keine echten Nachrichten
- keine Cloud-Aufrufe

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine externe Aktion.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.
- Safety-Flags bleiben unveraendert.
- Dieses Dokument ist nur eine manuelle Anleitung.

## Naechster sinnvoller Schritt

Local Ollama Config Apply Implementation Plan:

- nur planen, wie ein spaeterer technischer Apply-Schritt aussehen duerfte,
- weiterhin keine automatische Aktivierung,
- klarer Rollback-Pfad zur Mock-Konfiguration.

Status danach: Der Apply-Implementierungsplan ist in `FRIDAY_LOCAL_OLLAMA_CONFIG_APPLY_IMPLEMENTATION_PLAN.md` dokumentiert.
