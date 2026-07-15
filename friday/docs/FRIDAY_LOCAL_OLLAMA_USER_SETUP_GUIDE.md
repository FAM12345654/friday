# Friday Local Ollama User Setup Guide

## Ziel

Diese Anleitung beschreibt, wie du Friday spaeter mit einem lokalen Ollama-Modell vorbereiten kannst.
Der Schritt aktiviert noch keinen echten KI-Live-Betrieb in Friday.

Friday bleibt standardmaessig sicher:

- Mock-Provider bleibt Default.
- `ENABLE_LOCAL_OLLAMA = False` bleibt unveraendert.
- Kein Cloud-Modell wird genutzt.
- Keine E-Mail oder WhatsApp wird gesendet.
- Keine Modellantwort wird automatisch gespeichert.

## Voraussetzungen

- Windows-PC mit lokal laufendem Friday-Projekt.
- Ollama lokal installiert.
- Ein lokal geladenes Modell.
- Friday API laeuft lokal oder per Tailscale erreichbar.

## Ollama installieren

1. Ollama fuer Windows installieren:

```powershell
winget install Ollama.Ollama
```

Falls `winget` nicht verfuegbar ist, Ollama manuell ueber die offizielle Website installieren.

## Lokales Modell laden

Empfohlener erster Test:

```powershell
ollama pull llama3.1
```

Alternativ kann ein kleineres Modell verwendet werden, wenn der PC wenig Leistung hat.

## Ollama lokal testen

Pruefen, ob Ollama antwortet:

```powershell
ollama list
```

Optionaler lokaler API-Test:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Wichtig:

- Erlaubt ist nur `localhost` oder `127.0.0.1`.
- Keine Cloud-URL verwenden.
- Keine API-Keys eintragen.

## Friday Status pruefen

Friday stellt einen read-only Status-Endpunkt bereit:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/api/ai/status"
```

Dieser Standardaufruf startet keinen Live-Health-Check.

Optionaler lokaler Health-Check:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/api/ai/status?run_health_check=true"
```

Der Health-Check darf nur lokal gegen Ollama laufen.

## Noch nicht automatisch aktivieren

In diesem Schritt nicht aendern:

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_MODEL = ""
```

Warum:

- Die technische Readiness ist da.
- Der echte Produktbetrieb braucht ein separates Freigabe-Gate.
- Danach muss Friday weiterhin auf Mock zurueckfallen, wenn Ollama nicht erreichbar ist.

## Was schon funktioniert

- Friday kann KI-Drafts fuer Aufgaben-Weiterleitung ueber die lokale Provider-Schicht vorbereiten.
- Der sichere Mock-Provider ist aktiv.
- Der Ollama-Status kann read-only geprueft werden.
- Validator und Logic Check bleiben zwischen Modellantwort und Produktfluss.

## Was noch nicht freigegeben ist

- Echter Cloud-KI-Betrieb.
- Automatischer Ollama-Produktbetrieb.
- Echte E-Mail.
- Echtes WhatsApp.
- Automatisches Senden.
- Persistente Modell-Audit-Historie.

## Safety Check

Folgende Flags bleiben unveraendert:

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`
- `ENABLE_LOCAL_OLLAMA = False`

## Empfohlene Tests nach lokaler Ollama-Vorbereitung

```powershell
python -m pytest friday/tests/test_local_ollama_activation_gate.py friday/tests/test_local_ollama_runtime.py friday/tests/test_ai_task_forwarding_draft.py
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Naechster sinnvoller Schritt

Local Ollama Config Preview:

- Konfigurationsvorschau fuer ein konkretes Modell,
- weiterhin kein dauerhaftes Umschalten,
- kein Cloud-Fallback,
- kein echter Versand.

Status danach: Die Config Preview ist in `FRIDAY_LOCAL_OLLAMA_CONFIG_PREVIEW.md` dokumentiert.
