# Local Contact Context Prompt Plan 14B

## Ziel

Aufbau eines reinen Planungsdokuments für den nächsten Schritt in der Kontakt-Kontext-Funktionalität:

- Wann darf Friday später nach lokaler Kontakt-Einordnung fragen?
- Wie kann die Nachfrage minimal und nicht störend erfolgen?
- Wie wird Wiederholung vermieden?
- Welche Angaben sind sicherheitskritisch verboten?

Keine produktive Logik, keine Persistenz und keine CLI-Integration in 14B.

## Ausgangslage

- Build Step 14A ist abgeschlossen.
- Preview-Modell ist vorhanden (`ContactContextPreview`), noch ohne Persistenz.
- Kontakt-Kontext bleibt aktuell rein lokal und preview-basiert.
- Keine Integration in Message-/Task-/Review-Flows in diesem Schritt.
- Keine externen APIs, kein Kontaktimport, keine Datenbankschemaänderung.

## Wann darf Friday später fragen?

Empfohlene Regelung für spätere Implementierung:

| Situation | Fragen erlaubt? | Begründung |
|---|---|---|
| Unbekannter Absender im Nachrichten-Review | ja, in begrenztem Kontext | Kontext kann die Reviewqualität verbessern |
| Nutzer bearbeitet explizit eine Person | ja | klare Nutzerintention |
| Aufgabe basiert auf Nachricht mit unbekanntem Absender | ja, nach Bedarf | zusätzlicher Mehrwert für spätere Vorschläge |
| Nutzer fragt explizit nach Personendetails | ja | ausdrücklich initiiert |
| App-Start ohne konkreten Kontext | nein | zu störend |
| Jede neue Nachricht automatisch | nein | Wiederholungs- und Unterbrechungsrisiko |
| Kontaktart ist bereits bekannt | nein | keine Wiederholung notwendig |
| Keine klare Nutzerintention | nein | unnötige Abfrage |

## Minimaler Prompt-Entwurf

**Primäre Frage (minimal):**

`Wer ist {Name} für dich?`

Auswahl:

1. Kunde
2. Kollege
3. Mitarbeiter
4. Familie
5. Freund
6. Dienstleister
7. Sonstiges
8. Überspringen

**Optionale Folgefrage 1:**

`Optionaler Spitzname oder Kurzname für {Name} (leer = überspringen):`

**Optionale Folgefrage 2:**

`Kurzer Kontext zu {Name} (leer = überspringen):`

Prinzipien:

- Nur auf Nachfrage des Nutzers/konkreten Kontext.
- Alle Folgefragen sind überschreibbar und optional.
- Keine Pflichtantwort außer der eigentlichen Auswahl.
- Keine sensiblen personenbezogenen Kategorien.

## Wiederholungs-Vermeidung (Plan)

Geplanter späterer Status für Prompt-Kontrolle:

| Status | Beschreibung | Verhalten |
|---|---|---|
| unknown | Noch offen | kann später bei passendem Kontext erneut abgefragt werden |
| known | Kontaktart festgelegt | keine erneute automatische Nachfrage |
| skipped | Nutzer hat übersprungen | nicht in derselben Session erneut fragen |
| ask_later | später erneut prüfen | nur bei neuem relevantem Kontext erneut prüfen |

Regel:

- `skipped` verhindert erneute Nachfrage im selben Kontextdurchlauf.
- `ask_later` wird nur nach neuem signifikantem Kontext erneut geprüft.
- `known` bleibt bevorzugter Normalfall nach einmaliger Bestätigung.

## Was darf nicht gefragt werden

14B darf **keine** Fragen zu folgenden Bereichen enthalten:

- politische Zugehörigkeit
- Religion
- Ethnie
- Gesundheit
- sexuelle Orientierung
- Gewerkschaftszugehörigkeit
- strafrechtliche Details
- finanzielle Profile
- andere sensible Identitätskategorien

Erlaubt nur:

- Lokale Rollenbeziehungen in:
  - Kunde
  - Kollege
  - Mitarbeiter
  - Familie
  - Freund
  - Dienstleister
  - Sonstiges
  - Unbekannt

## Nicht-Ziele von 14B

14B bleibt eine reine Planungsrunde:

- Keine Implementierung
- Keine CLI-Prompt-Integration
- Keine Datenbank-Nutzung
- Keine DB-Migration
- Kein Contact Repository
- Keine Message-/Review-Flow-Integration
- Kein Kontaktimport
- Keine Obsidian-Write-Operation
- Keine externen Aktionen/APIs

## Vorgeplante Testideen (für spätere Schritte, nicht jetzt implementieren)

- Unbekannter Kontakt erzeugt potenziellen Prompt-Kandidaten.
- Bekannter Kontakt erzeugt keinen Prompt.
- Übersprungenes Feld wird nicht sofort erneut abgefragt.
- Neue Kontexte ändern den Prompt-Zustand.
- Ungültige Auswahl bleibt stabil (ohne Seiteneffekte).

## Empfohlener nächster Build Step 14C

**14C — Contact Context Prompt Candidate Model**

- In-Memory-Struktur für Prompt-Kandidaten definieren.
- Entscheidungskriterien für Fragefreigabe testen (ohne Persistenz).
- Wiederholungslogik dokumentiert als Zustandsmodell.
- Keine echte CLI- oder Flow-Anbindung.
