# Friday Local Ollama Service Start Checklist

## Ziel

Diese Checkliste beschreibt, wie Ollama lokal gestartet und geprueft werden kann, bevor Friday spaeter optional auf lokale KI umgestellt wird.
Dieser Schritt aktiviert Friday nicht und aendert keine Projekt-Konfiguration.

## Selected Sub-Agents

| Sub-Agent | Beitrag |
|---|---|
| Architecture Sub-Agent | Haelt den Schritt dokumentationsfokussiert und ohne Produktcode-Aenderung. |
| Local AI Setup Sub-Agent | Dokumentiert lokale Start- und Health-Checks fuer Ollama. |
| Safety Sub-Agent | Bestaetigt, dass keine automatische KI-Aktivierung erfolgt. |
| Documentation Sub-Agent | Erstellt die Start-Checkliste und verlinkt sie im Doku-Index. |
| QA Sub-Agent | Prueft Tests, Compilecheck, Safety Smoke und Diff-Check. |

## Aktueller lokaler Zustand

| Check | Ergebnis |
|---|---|
| `ollama list` | lokale Verbindung verweigert |
| Ollama-Prozess | kein laufender Prozess gefunden |
| Lokaler Endpunkt | `http://127.0.0.1:11434/` nicht erreichbar |
| Friday-Aktivierung | nicht erfolgt |

## Windows-Startoptionen

### Option A: Ollama-App starten

1. Windows-Startmenue oeffnen.
2. `Ollama` suchen.
3. Ollama starten.
4. Einige Sekunden warten.
5. Danach in PowerShell pruefen:

```powershell
ollama list
```

### Option B: Ollama-Service in einem Terminal starten

In einem separaten PowerShell-Fenster:

```powershell
ollama serve
```

Dieses Fenster offen lassen, solange der lokale Ollama-Dienst laufen soll.

## Modell pruefen oder installieren

Wenn `ollama list` funktioniert, sollte mindestens ein lokales Modell vorhanden sein.

Beispiel fuer ein spaeteres lokales Modell:

```powershell
ollama pull llama3.1
```

Wichtig: Das Installieren eines Modells ist ein manueller Nutzer-Schritt und aktiviert Friday noch nicht.

## Health-Check vor Aktivierung

Friday darf erst dann auf Ollama umgestellt werden, wenn der lokale Health-Check erfolgreich ist:

```powershell
python - <<'PY'
from friday.app.local_ollama_runtime import check_ollama_health

result = check_ollama_health("http://localhost:11434", 5)
print(result)
PY
```

Erwartung vor einer spaeteren Aktivierung:

- `available=True`
- lokaler Endpunkt erreichbar
- mindestens ein Modell installiert
- Safety Smoke bleibt `PASS`

## Aktivierungsregel

Friday darf nicht automatisch aktiviert werden.

Eine spaetere Aktivierung braucht alle Bedingungen:

1. Ollama laeuft lokal.
2. Health-Check ist erfolgreich.
3. Modell ist lokal installiert.
4. Dry Run fuer Config-Aenderung ist plausibel.
5. Safety Smoke ist `PASS`.
6. Nutzer bestaetigt exakt:

```text
OLLAMA AKTIVIEREN
```

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Config geaendert.
- Keine echte KI aktiviert.
- Keine Cloud- oder Provider-Anbindung.
- Kein API-Key.
- Keine Netzwerkaktion durch Friday.
- Keine Datenbankschema-Aenderung.
- `ENABLE_LOCAL_OLLAMA = False` bleibt erhalten.

## Empfehlung fuer den naechsten Schritt

Naechster sicherer Schritt: **Local Ollama Model Availability Check**.

Dabei wird nur geprueft und dokumentiert, ob nach manuellem Start ein lokales Modell sichtbar ist.
