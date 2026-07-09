# Friday Local Ollama Config Apply Readiness Gate

## Ziel

Dieses Gate prueft den isolierten lokalen Ollama Config Writer aus
`FRIDAY_LOCAL_OLLAMA_CONFIG_APPLY_IMPLEMENTATION.md`.

Das Ergebnis ist eine technische Freigabe fuer den isolierten Writer, nicht fuer
eine automatische Aktivierung von Ollama im echten Projekt.

## Gepruefte Bausteine

| Baustein | Ergebnis |
|---|---|
| `friday/app/local_ollama_config_apply_writer.py` | vorhanden, isoliert, nicht an CLI/Mobile/API-Apply angeschlossen |
| `friday/app/local_ollama_config_apply_guard.py` | vorhanden, Token-/Smoke-/Health-Gate bleibt vorgeschaltet |
| `friday/app/local_ollama_config_preview.py` | vorhanden, prueft Modell und lokale Base-URL ohne Write |
| `friday/tests/test_local_ollama_config_apply_writer.py` | vorhanden, schreibt nur auf `tmp_path` |
| `friday/config.py` | nicht geaendert, `ENABLE_LOCAL_OLLAMA = False` |

## Readiness-Ergebnis

- Der Writer darf eine explizit uebergebene `config.py` mit lokalen Ollama-Werten aktualisieren.
- Der Writer ersetzt nur Allowlist-Zeilen fuer:
  - `ENABLE_LOCAL_OLLAMA`
  - `OLLAMA_BASE_URL`
  - `OLLAMA_MODEL`
  - `OLLAMA_TIMEOUT_SECONDS`
- Die echte Projekt-`config.py` bleibt standardmaessig blockiert.
- Es gibt keine CLI-, Mobile- oder API-Funktion, die den echten Apply ausfuehrt.
- Der Schritt hat Friday nicht auf Ollama umgeschaltet.

## Weiterhin blockiert

- Automatisches Schreiben in `friday/config.py`
- Aktivieren von `ENABLE_LOCAL_OLLAMA = True` im echten Projekt
- Modellaufruf ohne separaten lokalen Health-/Apply-Schritt
- Cloud-Fallback
- E-Mail-/WhatsApp-/SMS-Versand
- Kalenderaktionen
- Externe Provider

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Kein Cloud-KI-Provider.
- Kein API-Key.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.
- Safety-Flags bleiben unveraendert.
- `ENABLE_LOCAL_OLLAMA` bleibt im echten Projekt `False`.

## Validierung

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

Zuletzt dokumentierter Stand:

- Fokus-Tests: `28 passed`
- Full Regression: `1127 passed, 4 skipped`
- Compilecheck: erfolgreich
- Safety Smoke: `PASS`
- Diff-Check: sauber

## Entscheidung

Der isolierte Writer ist readiness-geprueft.

Nicht freigegeben ist ein echter Produkt-Apply auf die Projekt-`config.py`.

## Empfehlung fuer den naechsten Build Step

Local Ollama Real Project Apply Gate Plan:

- planen, wie ein Nutzer die echte Projekt-`config.py` spaeter bewusst aktivieren darf,
- weiterhin nur lokal,
- weiterhin mit `OLLAMA AKTIVIEREN`,
- weiterhin mit Health Check und Safety Smoke,
- weiterhin ohne Versand und ohne Cloud-Fallback.
