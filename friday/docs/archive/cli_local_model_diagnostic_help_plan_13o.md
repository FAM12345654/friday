# Local Model Diagnostic Help Plan 13O

## Ziel

Planung für einen optionalen, sehr kleinen Hilfe-Hinweis zum lokalen Modell-Diagnosemodus.

## Ausgangslage

- Sicherheitsstatus zeigt bereits:
  - Lokaler Modell-Diagnosemodus: Mock/Preview
  - Externe Modellaufrufe: False
  - Produktfluss angebunden: False
- Die Diagnose ist rein angezeigt und nicht in Produktflows eingebunden.
- Bisher gibt es keine echten Modellaufrufe.

## Bewertete Optionen

| Option | Nutzen | Risiko | Empfehlung |
|---|---|---|---|
| A. Kein Help-Hinweis | Kein zusätzliches UI-Risiko, Help bleibt kompakt | Nutzer findet Diagnose nur im Sicherheitsstatus | Sicherste Standardoption, falls Help-Minimalismus gewünscht ist |
| B. Kurzer Help-Hinweis | Bessere Sichtbarkeit; geringe Änderung im bestehenden Text | Leicht mehr technische Wörter in Help, aber beherrschbar | Empfohlen als nächster kleiner Produkt-Option (später in 13P) |
| C. Detail-Hinweis in Help | Hohe Transparenz in einem Schritt | Zu textlastig, Gefahr unnötiger Komplexität | Nicht empfohlen |
| D. Eigener Diagnose-Menüpunkt | Sehr explizit trennbar | Zusätzliche Menüoption für nur-informative Diagnosefunktion | Nicht empfohlen |

## Empfohlene Richtung

- 13O bleibt reines Planungsdokument.
- Kein Menüpunkt in 13O.
- Kein Produktfluss-Update.
- Kein Provider-Check.
- Für 13P ist Option B vorgesehen:
  - `Lokale Modell-Diagnose: siehe Sicherheitsstatus. Es werden keine externen Modellaufrufe genutzt.`

## Nicht-Ziele

- Keine echten Modellaufrufe.
- Keine Provider-/Netzwerkverbindungen.
- Keine API-Keys.
- Keine Task-/Message-/Review-Integration.
- Kein eigener Diagnose-Menüpunkt.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Ollama-/LiteLLM-/OpenAI-Aufrufe.
- Keine Cloud-Fallbacks.
- Safety-Flags bleiben unverändert.
- Delete-Policy bleibt unverändert:
  - `"ja"` löscht nicht.
  - `"JA"` löscht.
  - `" JA "` bleibt durch `strip()` erlaubt.

## Vorgeschlagener Testplan für spätere Implementierung

- Help-Ausgabe enthält einen kurzen Verweis auf die Diagnose.
- Run-Loop bleibt stabil (Help, dann Exit).
- Keine Netzwerk-/Provider-Aufrufe.
- Keine neuen externen Flows.

## Empfehlung für Build Step 13P

Build Step 13P: Local Model Diagnostic Help Hint

- Eine einzige kurze Help-Zeile ergänzen.
- Keine externen Modellaufrufe.
- Keine Provider-Aktivierung.
- Tests in Main-Menu-E2E um kurze Help-Assertion ergänzen.
