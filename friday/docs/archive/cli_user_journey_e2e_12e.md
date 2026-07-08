# CLI User Journey E2E 12E

## Geprüfte Journey
- Start der CLI über `run()` mit echtem `TaskAgent` auf `tmp_path` SQLite.
- Hauptmenü aufrufen, Aufgabenmenü öffnen, Aufgabe erstellen.
- Aufgabe im Suchpfad anzeigen lassen, Aufgabe als erledigt markieren.
- Zurück ins Hauptmenü und sauber beenden.

## Abgesicherte Verhaltensweisen
- Hauptmenüpfad `1` öffnet zuverlässig das Aufgabenmenü.
- Eine neue Aufgabe kann lokal erstellt werden (`Aufgabe wurde erstellt.`).
- Die Suche/Filterung reagiert auf Suchtext (`Journey Aufgabe` wird im Ausgabe-Pfad gefunden).
- Das Erledigen lokal funktioniert (`Aufgabe wurde als erledigt markiert.`).
- Rückkehr vom Aufgabenmenü und Exit aus der Hauptschleife bleiben stabil (`Friday wird beendet.`).

## Safety-Bewertung
- Keine externen Aktionen.
- Lokale Datenhaltung über SQLite auf `tmp_path`.
- Sicherheitsflags unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Keine Datenbankschema-Änderung.
- Delete-Policy bleibt unverändert (`ja` löscht nicht, `JA` löscht).

## Empfehlung für Build Step 12F
- Als nächster Schritt eine lokale User-Journey für den Review-/Suggestion-Workflow ergänzen:
  Start → Review öffnen → Vorschlag prüfen → lokal freigeben/ablehnen → Aufgaben-Vorschlag umwandeln → zurück → Exit.
