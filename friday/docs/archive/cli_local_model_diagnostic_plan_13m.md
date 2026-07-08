# Local Model Diagnostic CLI Plan 13M

## Ziel

Planung eines möglichen späteren lokalen Diagnosehinweises für die Modell-Readiness ohne Produktintegration.

## Ausgangslage

- `LocalModelMockAdapter` ist vorhanden.
- `LocalModelPreview` und `preview_local_model_response` sind vorhanden.
- Readiness-Gate 13L ist abgeschlossen.
- Keine echten Modellprovider aktiv.
- Keine Task-/Message-/Review-Anbindung der Mock-/Preview-Funktion.

## Bewertete Optionen

| Option | Nutzen | Risiko | Empfehlung |
|---|---|---|---|
| Diagnose im Sicherheitsstatus | Sichtbar für Nutzer, guter Ort für lokale Readiness-Hinweise | Sicherheitsbereich wird länger, braucht kompakte Darstellung | Empfohlen für späteren minimalen Schritt |
| Diagnose in Hilfe/Übersicht | Schnell auffindbar für Nutzer, ohne Hauptablauf zu ändern | Gefahr, den Hilfebereich stärker aufzublähen | Nur als kurzer Verweis denkbar |
| Separater Diagnose-Menüpunkt | Sehr klar getrennt, gute Struktur | Zusätzliche Menüoption für noch nicht produktives Feature | Nicht im nächsten Schritt empfohlen |
| Kein UI-Pfad (nur Planungs-/Dokuabgleich) | Maximale Sicherheit, keine UX-Veränderung | Keine sichtbare Diagnose für Nutzer | Aktuell als sicherster Minimalweg empfohlen |

## Empfohlene Richtung

### Für den nächsten Schritt (13M)

- **Kein neuer Menüpunkt in 13M.**
- Die Implementierung bleibt bewusst auf Dokumentation geplant.
- Erst nach späterer Providerplanung: kurzer Diagnose-Hinweis im Sicherheitsstatus.

### Diagnoseinhalt (spätere Umsetzung)

- `Lokaler Modell-Diagnosemodus: Mock/Preview`
- `Externe Modellaufrufe: False`
- `Produktfluss angebunden: False`
- `external_call_used`: False (Preview-Pfad)

## Nicht-Ziele in 13M

- Keine echten Modellaufrufe (Ollama, LiteLLM, OpenAI).
- Keine Provider-Aktivierung.
- Keine API-Keys.
- Keine Netzwerkaufrufe.
- Keine Datenbankschema-Änderung.
- Keine Produktlogik.
- Keine CLI-Menüintegration.
- Keine Änderung von Task-/Message-/Review-Flows.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten und keine echten Kalendertermine.
- Keine externen Modellprovider.
- Keine Cloud-Fallbacks.
- Safety-Flags bleiben unverändert local-first.
- Delete-Policy unverändert:
  - `"ja"` löscht nicht.
  - `"JA"` löscht.
  - `" JA "` bleibt durch `strip()` erlaubt.

## Vorgeschlagener Testplan für spätere Implementierung

- Wenn später ein Diagnosepunkt umgesetzt wird:
  - Ausgabe enthält Mock/Preview-Status klar und vollständig.
  - Ausgabe enthält `external_call_used=False`.
  - Run-Loop und bestehende CLI-Stabilität bleibt erhalten.
  - Sicherheitsstatus-Ausgabe ist stabil.
  - Keine Netzwerk-/Provider-Aufrufe erfolgen.

## Empfehlung für Build Step 13N

Build Step 13N soll als **Local Model Diagnostic Status in Safety View** starten:
- kurzer, kurzer Sicherheitsstatus-Eintrag,
- weiterhin ohne neue Menüoption,
- weiterhin ohne echte Modellaufrufe,
- anschließende Testabdeckung für Ausgabe und Stabilität.
