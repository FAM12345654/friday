# Friday Local Ollama User Action Wait Gate

## Ziel

Dieses Gate markiert den Punkt, an dem Friday nicht weiter automatisch in Richtung lokaler Ollama-Aktivierung gehen darf.
Ab hier braucht es eine echte Nutzeraktion ausserhalb von `continue`.

## Selected Sub-Agents

| Sub-Agent | Beitrag |
|---|---|
| Architecture Sub-Agent | Haelt den Schritt dokumentationsfokussiert und ohne Produktcode-Aenderung. |
| Local AI Readiness Sub-Agent | Prueft, ob die bekannten lokalen Ollama-Blocker weiterhin gelten. |
| User Action Gate Sub-Agent | Definiert, welche Nutzeraktion als naechster Fortschritt zaehlt. |
| Safety Sub-Agent | Bestaetigt, dass keine Aktivierung ohne Health-Check und Token erfolgt. |
| Documentation Sub-Agent | Dokumentiert Wait-State, erlaubte Aktionen und Stop-Regeln. |
| QA Sub-Agent | Validiert Tests, Compilecheck, Safety Smoke und Diff-Check. |

## Aktueller Status

| Bereich | Status |
|---|---|
| Friday KI-Modus | deaktiviert |
| `ENABLE_LOCAL_OLLAMA` | `False` |
| `OLLAMA_MODEL` | leer |
| Ollama-Dienst | zuletzt nicht erreichbar |
| Modell-Verfuegbarkeit | nicht bestaetigt |
| Aktivierungs-Token | nicht gegeben |
| Produkt-Config | unveraendert |

## Wichtige Entscheidung

`continue` ist keine Aktivierung.

Friday darf durch wiederholtes `continue` nicht:

- Ollama starten,
- ein Modell herunterladen,
- `friday/config.py` aktivieren,
- eine echte Modellanfrage in Produktflows ausfuehren,
- auf Cloud-/Provider-Fallbacks wechseln.

## Was jetzt als echte Nutzeraktion gilt

Eine der folgenden Aktionen muss bewusst erfolgen, bevor die Ollama-Kette weitergehen darf:

| Aktion | Bedeutung |
|---|---|
| Ollama lokal starten | Nutzer startet den lokalen Dienst manuell. |
| Modell installieren | Nutzer installiert bewusst ein lokales Modell, z. B. `ollama pull llama3.1`. |
| Health erneut pruefen lassen | Nutzer fordert explizit eine erneute lokale Pruefung an. |
| Exakter Token | Nutzer schreibt exakt `OLLAMA AKTIVIEREN`, nachdem Health und Modell bereit sind. |

## Sichere Antwort auf weiteres `continue`

Wenn der Nutzer erneut nur `continue` schreibt und Ollama weiterhin nicht erreichbar ist, soll Friday nicht endlos neue Aktivierungs-Dokumente erzeugen.

Stattdessen ist die sichere naechste Reaktion:

- Status knapp melden,
- sagen, dass lokale Nutzeraktion noetig ist,
- keine Config aendern,
- keine KI aktivieren,
- keine neuen Gates erzeugen, sofern kein neuer technischer Zustand vorliegt.

## Aktivierung bleibt blockiert bis

Alle Bedingungen muessen erfuellt sein:

1. Ollama-Dienst laeuft lokal.
2. `ollama list` ist erfolgreich.
3. Mindestens ein Modell ist sichtbar.
4. `check_ollama_health()` meldet `available=True`.
5. Dry Run fuer Config-Aenderung ist korrekt.
6. Safety Smoke ist `PASS`.
7. Nutzer bestaetigt exakt `OLLAMA AKTIVIEREN`.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Config geaendert.
- Keine KI aktiviert.
- Keine Cloud- oder Provider-Anbindung.
- Kein Modell-Download durch Friday.
- Keine Datenbankschema-Aenderung.
- Kein API-Key.
- `ENABLE_LOCAL_OLLAMA = False` bleibt erhalten.

## Empfehlung fuer den naechsten Schritt

Naechster sinnvoller Schritt erst nach Nutzeraktion:

- Wenn Ollama gestartet wurde: **Local Ollama Health Recheck**.
- Wenn ein Modell installiert wurde: **Local Ollama Model Recheck**.
- Wenn der Nutzer exakt `OLLAMA AKTIVIEREN` schreibt und Health gruen ist: **Local Ollama Activation Apply Gate**.
