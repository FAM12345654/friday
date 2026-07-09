# Friday Local Ollama Model Availability Check

## Ziel

Dieses Dokument haelt fest, ob auf dem lokalen Windows-PC ein Ollama-Modell fuer Friday sichtbar ist.
Der Check ist read-only und aktiviert Friday nicht.

## Selected Sub-Agents

| Sub-Agent | Beitrag |
|---|---|
| Architecture Sub-Agent | Haelt den Schritt klein, dokumentationsfokussiert und ohne Produktcode-Aenderung. |
| Local AI Setup Sub-Agent | Prueft lokale Ollama-Erreichbarkeit. |
| Model Availability Sub-Agent | Bewertet, ob ein lokales Modell fuer Friday sichtbar ist. |
| Safety Sub-Agent | Bestaetigt, dass keine KI-Aktivierung, kein Download und kein Cloud-Zugriff erfolgt. |
| Documentation Sub-Agent | Dokumentiert Status, Blocker und naechste Schritte. |
| QA Sub-Agent | Validiert Tests, Compilecheck, Safety Smoke und Diff-Check. |

## Gepruefter Zustand

| Check | Ergebnis |
|---|---|
| `ollama list` | fehlgeschlagen |
| Lokale Ollama-URL | `http://127.0.0.1:11434/` |
| Fehler | Verbindung verweigert |
| Health-Endpunkt | `http://localhost:11434/api/tags` |
| Health-Ergebnis | nicht verfuegbar |
| Sichtbare Modelle | keine, weil Ollama lokal nicht erreichbar ist |
| Friday-Aktivierung | nicht erfolgt |

## Aktuelle Friday-Konfiguration

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

## Entscheidung

Status: **Kein lokales Modell fuer Friday verfuegbar**

Diese Entscheidung bedeutet nicht, dass kein Modell installiert werden kann.
Sie bedeutet nur, dass Friday aktuell kein lokales Modell sicher erkennen kann, weil der Ollama-Dienst nicht erreichbar ist.

## Was nicht gemacht wurde

- Kein Modell heruntergeladen.
- Kein Modell gestartet.
- Keine Friday-Konfiguration geaendert.
- Keine echte KI aktiviert.
- Kein externer Provider verbunden.
- Kein API-Key gespeichert.
- Kein Produktfluss umgestellt.

## Naechste manuelle Schritte

Vor einer spaeteren Aktivierung sollte der Nutzer manuell:

1. Ollama starten.
2. `ollama list` erneut ausfuehren.
3. Falls kein Modell vorhanden ist, ein lokales Modell installieren, zum Beispiel:

```powershell
ollama pull llama3.1
```

4. Danach den Health-Check erneut ausfuehren.
5. Erst nach erfolgreichem Health-Check und exaktem Token `OLLAMA AKTIVIEREN` darf ein Apply-Schritt vorbereitet werden.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Config geaendert.
- Keine KI aktiviert.
- Keine Cloud- oder Provider-Anbindung.
- Keine Netzwerkaktion durch Friday.
- Keine Datenbankschema-Aenderung.
- `ENABLE_LOCAL_OLLAMA = False` bleibt erhalten.

## Empfehlung fuer den naechsten Schritt

Naechster sicherer Schritt: **Local Ollama Activation Blocker Summary**.

Dabei werden alle verbleibenden Blocker bis zur spaeteren lokalen Aktivierung knapp zusammengefasst.
