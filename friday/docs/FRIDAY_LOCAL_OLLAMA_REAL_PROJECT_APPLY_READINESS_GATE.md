# Friday Local Ollama Real Project Apply Readiness Gate

## Ziel

Dieses Gate prueft den aktuellen Stand fuer einen spaeteren echten Apply auf
die Projektdatei `friday/config.py`.

Das Gate ist eine Readiness-Pruefung. Es aktiviert Ollama nicht und schreibt
nichts in die echte Projekt-Konfiguration.

## Gepruefte Bausteine

| Baustein | Ergebnis |
|---|---|
| `friday/app/local_ollama_config_preview.py` | prueft Modellname und lokale Base-URL ohne Write |
| `friday/app/local_ollama_config_apply_guard.py` | prueft Token, Safety Smoke und Health Check ohne Write |
| `friday/app/local_ollama_config_apply_writer.py` | isolierter Writer; echte Projekt-`config.py` standardmaessig blockiert |
| `friday/app/local_ollama_real_project_apply_guard.py` | read-only Guard fuer spaeteren echten Projekt-Apply |
| `friday/config.py` | unveraendert, `ENABLE_LOCAL_OLLAMA = False` |

## Readiness-Ergebnis

- Der Preview-Baustein ist vorhanden.
- Das Apply Gate ist vorhanden.
- Der isolierte Writer ist vorhanden.
- Der Real Project Apply Guard ist vorhanden.
- Der echte Projekt-Apply ist weiterhin nicht freigegeben.
- Es gibt weiterhin keine CLI-, Mobile- oder API-Funktion, die die echte Projekt-`config.py` beschreibt.

## Weiterhin blockiert

- Automatischer Write auf `friday/config.py`
- Aktivieren von `ENABLE_LOCAL_OLLAMA = True`
- Modellaufruf ohne separaten lokalen Health-/Apply-Schritt
- Cloud-Fallback
- echte E-Mail-/WhatsApp-/SMS-Aktionen
- echte Kalenderaktionen
- API-Key-basierte Provider
- Mobile-Apply-Button

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Kein Cloud-KI-Fallback.
- Kein API-Key.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.
- Safety-Flags bleiben unveraendert.
- `ENABLE_LOCAL_OLLAMA` bleibt im echten Projekt `False`.

## Validierung

Fokus-Tests:

```powershell
python -m pytest friday/tests/test_local_ollama_real_project_apply_guard.py friday/tests/test_local_ollama_config_apply_writer.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_ai_task_forwarding_draft.py
```

Full Regression:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

Zuletzt dokumentierter Stand:

- Fokus-Tests: `35 passed`
- Full Regression: `1134 passed, 4 skipped`
- Compilecheck: erfolgreich
- Safety Smoke: `PASS`
- Diff-Check: sauber

## Entscheidung

Die Real-Project-Apply-Kette ist readiness-geprueft bis zum read-only Guard.

Nicht freigegeben ist:

- ein echter Write auf `friday/config.py`,
- eine Produkt-/API-/CLI-Anbindung,
- ein automatischer Wechsel von Mock auf Ollama.

## Empfehlung fuer den naechsten Build Step

Local Ollama Real Project Apply Implementation Plan:

- exakt planen, wie der echte Write auf `friday/config.py` spaeter sicher
  ausgefuehrt und validiert wird,
- Rollback verbindlich definieren,
- weiterhin keinen Write in der Planungsrunde ausfuehren.
