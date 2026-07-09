# Friday Local Ollama Manual Setup Check

## Ziel

Dieses Dokument haelt den aktuellen manuellen Setup-Check fuer lokale Ollama-Nutzung fest.
Friday wird dadurch nicht aktiviert und keine Projekt-Konfiguration wird geaendert.

## Selected Sub-Agents

| Sub-Agent | Beitrag |
|---|---|
| Architecture Sub-Agent | Haelt den Schritt dokumentationsfokussiert und ohne Produktlogik-Aenderung. |
| Local AI Setup Sub-Agent | Prueft lokale Ollama-Erreichbarkeit und Setup-Status. |
| Safety Sub-Agent | Stellt sicher, dass kein Cloud-Provider, kein echter Versand und keine automatische Aktivierung erfolgt. |
| Documentation Sub-Agent | Dokumentiert Ergebnis, Grenzen und naechste sichere Schritte. |
| QA Sub-Agent | Fuehrt Regression, Compilecheck, Safety Smoke und Diff-Check aus. |

## Gepruefter Zustand

| Check | Ergebnis |
|---|---|
| Ollama CLI | vorhanden, Client-Version `0.30.10` |
| Lokale Ollama-Instanz | nicht erreichbar |
| Lokaler Health-Endpunkt | `http://localhost:11434/api/tags` |
| Health-Ergebnis | Timeout |
| Exakter Aktivierungs-Token | nicht gegeben |
| Friday-Konfiguration | unveraendert |

## Entscheidung

Status: **Nicht aktivieren**

Gruende:

- Der Nutzer hat nicht exakt `OLLAMA AKTIVIEREN` als Aktivierungsbefehl gegeben.
- Die lokale Ollama-Instanz ist nicht erreichbar.
- Der Health-Check gegen `http://localhost:11434/api/tags` endete mit Timeout.
- Friday darf ohne erfolgreichen lokalen Health-Check nicht auf Ollama umgestellt werden.

## Aktueller sicherer Friday-Zustand

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

## Was noch noetig ist

Vor einer spaeteren Aktivierung muss Folgendes erfolgreich sein:

1. Ollama lokal starten.
2. Ein lokales Modell installieren, zum Beispiel mit `ollama pull llama3.1`.
3. Health-Check gegen `http://localhost:11434/api/tags` muss erfolgreich antworten.
4. Safety Smoke muss `PASS` melden.
5. Dry Run fuer die geplante Config-Aenderung muss erwartungsgemaess sein.
6. Der Nutzer muss exakt `OLLAMA AKTIVIEREN` bestaetigen.
7. Erst danach darf der isolierte Apply-Baustein die lokale Projekt-Config aendern.

## Safety-Bewertung

- Keine echte KI-Aktivierung.
- Keine Cloud- oder Provider-Anbindung.
- Kein API-Key.
- Kein echter Nachrichtenversand.
- Keine Kalenderaktion.
- Keine Datenbankschema-Aenderung.
- Keine Produktlogik-Aenderung.
- Keine Projekt-Config-Aenderung.
- `ENABLE_LOCAL_OLLAMA = False` bleibt erhalten.

## Empfehlung fuer den naechsten Schritt

Naechster sicherer Schritt: **Local Ollama Service Start Checklist**.

Dabei sollte dokumentiert werden, wie der lokale Ollama-Dienst gestartet und erneut geprueft wird, ohne Friday automatisch zu aktivieren.
