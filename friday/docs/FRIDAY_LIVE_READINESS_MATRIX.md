# Friday Live Readiness Matrix

## Ziel

Diese Matrix zeigt, was fuer den lokalen Friday-Stand bereits stabil ist und was noch fehlt, bevor Friday als echtes Live-Produkt mit externen Integrationen betrieben werden darf.

Der aktuelle Stand bleibt lokal-first:

- keine echten Nachrichten,
- keine echten Kalendertermine,
- keine Cloud-AI,
- keine unkontrollierten Writes,
- keine Git-Mutationen,
- keine externen Provider ohne eigenes Gate.

## Aktueller lokaler Stand

| Bereich | Status | Hinweis |
|---|---|---|
| Lokale CLI | stabil | Hauptmenue, Aufgaben, Review, Backup/Restore, Privacy und Safety Status sind getestet |
| Lokale SQLite-Datenhaltung | stabil | Arbeitsdatenbank und Demo-Datenbank sind getrennt |
| Aufgabenverwaltung | stabil | Create/Edit/Search/Done/Archive/Delete, Quick Add und Recurrence sind lokal abgesichert |
| Review-/Suggestion-Flows | stabil | Nachrichten- und Aufgaben-Vorschlaege bleiben lokal |
| Kontakt-Kontext | lokal nutzbar | Speichern und Vergessen bleiben hart gegatet |
| Obsidian | preview/gated | Preview stabil; Write nur mit Vault, Guard und hartem Token |
| Backup/Restore | lokal/gated | Backup, Restore Copy, Export/Import-Apply bleiben lokal und token-geschuetzt |
| Privacy Dashboard | lokal/gated | Read-only Anzeige plus getrennte Cleanup-Pfade |
| Local AI | mock/opt-in | Mock Default; Ollama nur localhost, opt-in und validiert |
| Safety Scanner | stabil | Smoke prueft Imports, Netzwerk, input/print, Flags und Tokens |

## Offene Punkte bis Live

| Prioritaet | Bereich | Was fehlt | Warum wichtig | Naechster Schritt |
|---|---|---|---|---|
| Hoch | Live-Freigabe-Policy | Klare Entscheidung, welche Live-Funktionen zuerst erlaubt werden | Ohne Reihenfolge steigt Safety-Risiko | Live-Roadmap in kleine Gates schneiden |
| Hoch | E-Mail/WhatsApp/SMS | Draft-only Provider-Plan, Mock Provider, Approval-Gate, Audit | Echter Versand ist riskant und irreversibel | Erst Draft-only planen, kein Send |
| Hoch | Kalender | Draft Event, Konfliktpruefung, Approval, Mock Provider | Kalender-Write kann reale Termine erzeugen | Erst lokales Event-Draft-Modell bauen |
| Hoch | Secrets/Config | Sichere lokale Credential-Policy, keine Secrets in Git/Backup/Export | Live-Provider brauchen Zugangsdaten | Secrets-Plan und Scanner-Gate bauen |
| Hoch | Audit Trail | Lokales Audit fuer riskante Freigaben und Writes | Nachvollziehbarkeit bei Live-Aktionen | Audit-Repository planen |
| Mittel | Local AI Produktnutzung | Klarer read-only Einsatzbereich fuer Ollama/Mock im Produktfluss | Modellantworten duerfen keine Writes ausloesen | Erst harmlose Diagnose/Preview-Flows |
| Mittel | Obsidian Write Ausbau | Batch-/Update-/Overwrite-Regeln | Write ist lokal, kann aber Wissen ueberschreiben | Write-Gates weiter verfeinern |
| Mittel | Backup/Restore | Echter In-Place-Restore bleibt nicht freigegeben | Restore kann aktive Daten ersetzen | Separates Restore-Approval-Gate planen |
| Mittel | Mobile/Desktop/API | Live-Release-Check, Start-/Health-Checks, Nutzerfluss | Produktbetrieb braucht stabile Oberflaechen | Runtime-Checkliste aktualisieren |
| Mittel | Documentation | Live-Betriebsanleitung und Support-Checkliste | Nutzer braucht klare Bedienung | User Guide fuer Live-Modus planen |
| Niedrig | UX Polish | Kurze Status-/Hilfe-/Fehlermeldungsverbesserungen | Reduziert Bedienfehler | Schrittweise nach Testmatrix |

## Nicht freigegeben ohne eigenes Gate

| Aktion | Status |
|---|---|
| echte E-Mail senden | nicht freigegeben |
| echtes WhatsApp senden | nicht freigegeben |
| echte SMS senden | nicht freigegeben |
| echten Kalendertermin erstellen | nicht freigegeben |
| Cloud-AI nutzen | nicht freigegeben |
| externe Provider automatisch aufrufen | nicht freigegeben |
| Secrets speichern/importieren | nicht freigegeben |
| In-Place-Restore in aktive Daten | nicht freigegeben |
| Git Commit/Push aus Friday | nicht freigegeben |

## Empfohlene Reihenfolge

1. Live-Roadmap Gate: entscheiden, welche externe Funktion zuerst kommt.
2. Secrets/Config Safety Gate: Zugangsdaten-Policy ohne echte Provider.
3. Draft-only Provider Gate: E-Mail/Kalender/WhatsApp nur als Entwurf, kein Send.
4. Mock Provider Gate: Provider-Schnittstelle mit Fake-Backend.
5. Approval/Audit Gate: harte Tokens, Audit Trail, Regression.
6. Real Provider Preview Gate: Health Check und Dry Run, kein Write/Send.
7. Real Action Gate: erst nach expliziter Nutzerfreigabe und separater Abnahme.

## Safety-Bewertung

- Dieses Dokument aendert keine Produktlogik.
- Es aktiviert keine externen Dienste.
- Es fuehrt keine Tests oder Shell-Befehle aus.
- Es aendert kein Datenbankschema.
- Es veraendert keine Safety-Flags.
- Delete-Policy und harte Tokens bleiben unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Schritt: `Live-Roadmap Gate` als reines Planungsdokument erstellen. Darin wird genau eine Live-Funktion als erster Kandidat gewaehlt, ohne sie bereits zu implementieren.
