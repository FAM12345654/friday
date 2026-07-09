# Friday Local Ollama Manual Activation Decision Gate

## Ziel

Dieses Gate entscheidet, ob Friday jetzt wirklich lokal auf Ollama umgeschaltet
werden darf.

In diesem Schritt wurde nichts aktiviert.

## Entscheidung

**Entscheidung: Nicht aktivieren.**

Gruende:

- Das harte Aktivierungs-Token `OLLAMA AKTIVIEREN` wurde in diesem Schritt nicht
  als ausdruecklicher Nutzerbefehl gegeben.
- Die lokale Health-Vorpruefung gegen `http://localhost:11434/api/tags` war
  nicht erfolgreich.
- `friday/config.py` bleibt unveraendert.
- `ENABLE_LOCAL_OLLAMA = False` bleibt aktiv.

## Lokale Health-Vorpruefung

Gepruefter Endpoint:

```text
http://localhost:11434/api/tags
```

Ergebnis:

| Feld | Wert |
|---|---|
| available | `False` |
| refused | `False` |
| local health call attempted | `True` |
| error | `<urlopen error timed out>` |

Diese Pruefung ist nur ein lokaler localhost-Health-Check. Es wurde kein Modell
aufgerufen und kein Cloud-Provider genutzt.

## Aktueller sicherer Zustand

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

Friday bleibt damit im Mock-Fallback.

## Voraussetzungen fuer spaetere Aktivierung

Vor einer echten Aktivierung muessen alle Punkte erfuellt sein:

- Ollama laeuft lokal auf dem Windows-PC.
- `http://localhost:11434/api/tags` antwortet erfolgreich.
- Ein lokales Modell ist vorhanden, z. B. `llama3.1`.
- Safety Smoke ist `PASS`.
- Dry Run zeigt die erwarteten vier Config-Zeilen.
- Nutzer gibt bewusst und exakt den Token `OLLAMA AKTIVIEREN`.
- Post-Write-Validation ist definiert.
- Rollback ist technisch moeglich.

## Weiterhin blockiert

- echter Write auf `friday/config.py`,
- automatisches Aktivieren beim App-Start,
- API-/CLI-/Mobile-Apply,
- Cloud-Fallback,
- API-Key-basierte Provider,
- echte E-Mail-/WhatsApp-/SMS-Aktionen,
- echte Kalenderaktionen.

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

Full Regression:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Local Ollama Manual Setup Check:

- Ollama lokal starten,
- Modell lokal ziehen, z. B. `ollama pull llama3.1`,
- Health Check erneut ausfuehren,
- erst danach bei bewusstem Token `OLLAMA AKTIVIEREN` den echten Apply erneut
  entscheiden.
