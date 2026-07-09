# Friday Local Ollama Real Project Apply Implementation Plan

## Ziel

Dieser Plan beschreibt den spaeteren technischen Schritt, der die echte
Projektdatei `friday/config.py` fuer lokales Ollama aktivieren koennte.

In diesem Schritt wird weiterhin nichts geschrieben und nichts aktiviert.

## Aktueller sicherer Stand

- `ENABLE_LOCAL_OLLAMA = False`
- Mock-Fallback bleibt aktiv
- kein echter Modellaufruf
- kein Cloud-Fallback
- kein API-Key
- keine externen Aktionen
- keine Mobile-/CLI-/API-Apply-Anbindung

## Bereits vorhandene Sicherheitsbausteine

| Baustein | Zweck |
|---|---|
| `local_ollama_config_preview.py` | Vorschau fuer Modell, lokale URL und Zielwerte |
| `local_ollama_config_apply_guard.py` | Token-, Safety-Smoke- und Health-Check-Gate |
| `local_ollama_config_apply_writer.py` | isolierter Writer fuer explizite `config.py`-Pfade |
| `local_ollama_real_project_apply_guard.py` | read-only Guard fuer echten Projekt-Config-Pfad |
| `local_ollama_runtime.py` | lokaler Health Check und lokaler Runtime-Zugriff |

## Geplanter echter Apply-Ablauf

Ein spaeterer technischer Apply darf nur diese Reihenfolge ausfuehren:

1. Projekt-`config.py` Pfad ermitteln.
2. Aktuelle Config lesen.
3. Sicherstellen, dass alle Ollama-Pflichtzeilen genau einmal vorhanden sind.
4. Config Preview mit Zielmodell und lokaler Base-URL bauen.
5. Safety Smoke ausfuehren und PASS erzwingen.
6. Lokalen Ollama Health Check ausfuehren und PASS erzwingen.
7. Real Project Apply Guard ausfuehren.
8. Exaktes Token `OLLAMA AKTIVIEREN` verlangen.
9. Backup der bisherigen `friday/config.py` erstellen.
10. Nur die vier erlaubten Ollama-Zeilen schreiben.
11. `python -m compileall friday friday-api` ausfuehren.
12. Ollama-/AI-Fokus-Tests ausfuehren.
13. `python scripts/friday_safety_smoke.py` ausfuehren.
14. Bei jedem Fehler automatisch Rollback auf Mock-Konfiguration.
15. Ergebnis dokumentiert ausgeben.

## Erlaubte Zielwerte

Der spaetere Apply darf nur diese Werte setzen:

```python
ENABLE_LOCAL_OLLAMA = True
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"
OLLAMA_TIMEOUT_SECONDS = 5
```

Optional darf `OLLAMA_BASE_URL` auch `http://127.0.0.1:11434` sein, wenn alle
lokalen URL-Gates bestehen.

## Verbindlicher Rollback

Rollback muss auf diese sichere Mock-Konfiguration gehen:

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

Rollback ist Pflicht bei:

- fehlgeschlagenem Compilecheck,
- fehlgeschlagenen Fokus-Tests,
- fehlgeschlagenem Safety Smoke,
- fehlgeschlagenem lokalen Health Check,
- falschem Token,
- nicht-lokaler Base-URL,
- fehlenden oder doppelten Config-Zeilen,
- unerwarteter Aenderung an externen Safety-Flags.

## Nicht-Ziele

- Kein Cloud-Fallback.
- Kein OpenAI-/Claude-/Anthropic-Key.
- Kein echter Versand von E-Mail, WhatsApp oder SMS.
- Keine Kalenderaktion.
- Keine Datenbankschema-Aenderung.
- Keine automatische Aktivierung beim App-Start.
- Keine Mobile-Aktivierung ohne eigenes spaeteres Gate.

## Tests fuer den spaeteren Apply

Ein spaeterer echter Apply muss mindestens diese Befehle ausfuehren:

```powershell
python -m pytest friday/tests/test_local_ollama_real_project_apply_guard.py friday/tests/test_local_ollama_config_apply_writer.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_local_ollama_runtime.py friday/tests/test_ai_task_forwarding_draft.py
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Safety-Bewertung

- Keine Produktlogik in diesem Schritt geaendert.
- Keine externe Aktion.
- Kein echter Modellaufruf.
- Kein Write auf `friday/config.py`.
- `ENABLE_LOCAL_OLLAMA` bleibt `False`.
- Die Real-Project-Apply-Implementierung bleibt geplant, aber noch nicht freigegeben.

## Entscheidung

Der echte Projekt-Apply ist implementierungsreif geplant, aber weiterhin nicht
ausgefuehrt.

## Empfehlung fuer den naechsten Build Step

Local Ollama Real Project Apply Writer Dry Run:

- einen Dry-Run-Baustein bauen, der die geplante echte Config-Aenderung
  simuliert,
- keinen echten Write ausfuehren,
- geplante Diff-Zeilen und Rollback-Plan ausgeben,
- weiterhin keine Aktivierung.
