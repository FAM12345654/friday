# Friday Live Roadmap Gate

## Ziel

Dieses Gate legt fest, wie Friday vom stabilen lokalen Produkt in Richtung Live-Funktionen weiterentwickelt werden darf.

Der Schritt ist bewusst nur Planung:

- keine Produktlogik,
- keine Provider,
- keine Secrets,
- keine Netzwerkaktion,
- kein echter Versand,
- kein echter Kalender-Write,
- keine Datenbankschema-Aenderung.

## Ausgangslage

Friday ist lokal stabil:

- CLI und Hauptmenue sind getestet,
- lokale Aufgaben- und Review-Flows sind stabil,
- Backup/Restore, Privacy und Export/Import sind lokal und hart gegatet,
- Obsidian bleibt preview/gated,
- Local AI bleibt Mock/localhost-opt-in,
- Safety Smoke ist sauber.

Letzter validierter Stand:

| Check | Ergebnis |
|---|---|
| Full Regression | `1081 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Diff Check | sauber |

## Live-Ausbau-Grundregel

Friday darf Live-Funktionen nur in dieser Reihenfolge vorbereiten:

1. Plan
2. Draft-only Modell
3. Mock Provider
4. Guard + harte Tokens
5. lokaler Audit Trail
6. Dry Run / Preview
7. echte Aktion erst nach separatem Gate

Kein Schritt darf Plan, Mock, Guard, Audit und Preview ueberspringen.

## Bewertete Live-Kandidaten

| Kandidat | Nutzen | Risiko | Empfehlung |
|---|---|---|---|
| E-Mail Draft-only | hoch | mittel | guter erster Kandidat, solange kein Send gebaut wird |
| Kalender Draft-only | hoch | mittel bis hoch | sinnvoll nach E-Mail Draft, wegen Konfliktlogik komplexer |
| WhatsApp Draft-only | mittel | hoch | spaeter, da Kontakt-/Provider-Mapping sensibel ist |
| SMS Draft-only | niedrig bis mittel | hoch | spaeter, da Versandkosten/Provider-Risiko |
| Cloud-AI | mittel | hoch | nicht zuerst; Local AI/Validator weiter nutzen |
| Obsidian Batch Write | mittel | mittel | lokal, aber Write-Risiko; nach Audit/Approval sinnvoll |

## Gewaehlter erster Kandidat

**Erster Live-Vorbereitungsblock:** E-Mail Draft-only

Warum:

- hoher Produktnutzen,
- kann komplett ohne echten Versand vorbereitet werden,
- passt zu bestehenden Review-/Message-Flows,
- laesst sich gut mit Mock Provider und Approval/Audit planen,
- riskanter Send bleibt separat blockiert.

## Scope fuer den naechsten Schritt

Der naechste Schritt darf nur planen:

- welche Daten ein E-Mail-Entwurf enthalten darf,
- welche Daten nicht enthalten sein duerfen,
- wie ein Mock Provider spaeter aussehen koennte,
- welche harten Tokens fuer spaetere Writes/Sends noetig waeren,
- wie Audit Trail und Safety Scanner eingebunden werden.

Der naechste Schritt darf nicht bauen:

- SMTP,
- Gmail,
- Outlook,
- Mail API,
- echte Zugangsdaten,
- echten Versand,
- Provider-Login,
- Netzwerkaufrufe.

## Nicht freigegeben

| Aktion | Status |
|---|---|
| echte E-Mail senden | nicht freigegeben |
| Gmail/Outlook/SMTP verbinden | nicht freigegeben |
| OAuth/Login bauen | nicht freigegeben |
| Secrets speichern | nicht freigegeben |
| externe Kontakte importieren | nicht freigegeben |
| automatische Entwuerfe versenden | nicht freigegeben |
| Modellantworten direkt senden | nicht freigegeben |

## Safety-Anforderungen fuer spaetere Live-Schritte

Jeder spaetere Live-Step braucht:

- eigene Sub-Agent-Pruefung,
- separate Tests,
- Safety Smoke PASS,
- klare harte Tokens,
- Audit Trail,
- Mock Provider vor Real Provider,
- Dry Run vor echter Aktion,
- Dokumentation im User Guide und Safety Matrix.

## Empfohlene Folge-Gates

| Reihenfolge | Gate | Zweck |
|---|---|---|
| 1 | Email Draft-Only Plan | Datenmodell und UX fuer lokale E-Mail-Entwuerfe planen |
| 2 | Email Draft Model | isoliertes Entwurfsmodell ohne Provider bauen |
| 3 | Email Draft Renderer | lokale Vorschau fuer Entwurfstexte bauen |
| 4 | Email Mock Provider Plan | Mock-Schnittstelle planen, kein Netzwerk |
| 5 | Email Approval/Audit Plan | harte Tokens und Audit Trail planen |
| 6 | Email Send Readiness Gate | pruefen, ob echter Versand weiterhin blockiert bleibt |

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine externen Aktionen aktiviert.
- Keine Provider integriert.
- Keine Secrets verarbeitet.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Schritt: `Email Draft-Only Plan` als reines Planungsdokument.

Ziel: Lokale E-Mail-Entwuerfe fachlich und sicherheitlich planen, ohne Provider, Login, Netzwerk oder echten Versand.
