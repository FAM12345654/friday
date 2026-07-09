# Friday Local Ollama Activation Blocker Summary

## Ziel

Dieses Dokument fasst die aktuell offenen Blocker zusammen, bevor Friday spaeter optional mit lokaler Ollama-KI verbunden werden darf.
Es ist ein reines Readiness-Dokument und aktiviert Friday nicht.

## Selected Sub-Agents

| Sub-Agent | Beitrag |
|---|---|
| Architecture Sub-Agent | Stellt sicher, dass keine Produktlogik, Config oder Datenbank geaendert wird. |
| Local AI Readiness Sub-Agent | Ordnet die offenen lokalen Ollama-Voraussetzungen. |
| Safety Sub-Agent | Bestaetigt, dass keine KI-Aktivierung und keine externen Provider erfolgen. |
| Documentation Sub-Agent | Dokumentiert Blocker, Reihenfolge und Aktivierungsgrenzen. |
| QA Sub-Agent | Validiert Tests, Compilecheck, Safety Smoke und Diff-Check. |

## Aktueller Zustand

| Bereich | Status |
|---|---|
| Ollama CLI | installiert |
| Lokaler Ollama-Dienst | nicht erreichbar |
| Modell-Liste | nicht abrufbar |
| Lokales Modell fuer Friday | nicht bestaetigt |
| Exakter Aktivierungs-Token | nicht gegeben |
| Friday Config | unveraendert |
| Friday KI-Modus | deaktiviert |

Aktuelle sichere Konfiguration:

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

## Offene Blocker

| Prioritaet | Blocker | Bedeutung | Naechste Aktion |
|---|---|---|---|
| Hoch | Ollama-Dienst laeuft nicht erreichbar | Friday kann kein lokales Modell pruefen | Ollama lokal starten |
| Hoch | `ollama list` schlaegt fehl | Modellbestand ist unbekannt | Nach Dienststart erneut ausfuehren |
| Hoch | Kein Modell fuer Friday bestaetigt | Friday darf kein leeres Modell aktivieren | Lokales Modell installieren oder bestaetigen |
| Hoch | Health-Check nicht erfolgreich | Aktivierung waere unsicher | `check_ollama_health()` erneut ausfuehren |
| Hoch | Aktivierungs-Token fehlt | Keine explizite Freigabe | Nutzer muss exakt `OLLAMA AKTIVIEREN` schreiben |
| Mittel | Dry Run muss vor Apply passen | Config-Aenderung muss vorher sichtbar sein | Dry Run mit Zielwerten ausfuehren |
| Mittel | Rollback-Pfad muss bereit bleiben | Sichere Rueckkehr zu Mock/Disabled | Apply nur mit dokumentiertem Rollback |

## Erlaubte naechste Schritte

- Ollama lokal starten.
- `ollama list` erneut pruefen.
- Lokales Modell manuell installieren, falls gewuenscht.
- Localhost-Health-Check erneut ausfuehren.
- Dry Run fuer Config-Aenderung ausfuehren.
- Safety Smoke ausfuehren.

## Nicht erlaubte Schritte ohne weiteres Gate

- Friday automatisch aktivieren.
- `friday/config.py` ohne exakten Token aendern.
- Cloud-Provider anbinden.
- API-Key speichern.
- echtes Senden von Nachrichten aktivieren.
- echte Kalenderaktionen aktivieren.
- Fallback auf externe KI verwenden.

## Aktivierungsreihenfolge

1. Ollama lokal starten.
2. `ollama list` muss erfolgreich sein.
3. Mindestens ein lokales Modell muss sichtbar sein.
4. Health-Check muss `available=True` melden.
5. Dry Run muss die erwarteten Config-Zielwerte zeigen.
6. Safety Smoke muss `PASS` melden.
7. Nutzer gibt exakt `OLLAMA AKTIVIEREN`.
8. Erst dann darf ein gesonderter Apply-Schritt vorbereitet werden.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Config geaendert.
- Keine KI aktiviert.
- Keine Cloud- oder Provider-Anbindung.
- Keine Datenbankschema-Aenderung.
- Kein Modell-Download durch Friday.
- Kein API-Key.
- `ENABLE_LOCAL_OLLAMA = False` bleibt erhalten.

## Empfehlung fuer den naechsten Schritt

Naechster sicherer Schritt: **Local Ollama User Action Wait Gate**.

Friday sollte jetzt auf eine echte Nutzeraktion warten:

- entweder Ollama lokal starten und erneut pruefen lassen,
- oder exakt `OLLAMA AKTIVIEREN` erst dann senden, wenn Health und Modell verfuegbar sind.
