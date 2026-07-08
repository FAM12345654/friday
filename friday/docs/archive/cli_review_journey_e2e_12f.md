# CLI Review Journey E2E 12F

## Geprüfte Journey
- Start der CLI über `run()` mit echtem `TaskAgent`, `MessageAgent` und `CalendarAgent` auf `tmp_path` SQLite.
- Hauptmenüpunkt `6` öffnet den Review-Bereich.
- Nachrichten-Vorschlag wird im Review geprüft und lokal freigegeben.
- Aufgaben-Vorschlag wird danach lokal als Aufgabe umgewandelt.
- Nach Rücksprung über `z` geht die Oberfläche wieder ins Hauptmenü und beendet sauber mit `7`.

## Abgesicherte Verhaltensweisen
- `review_pending_suggestions()` kann per Hauptmenü gestartet werden (`6`) und zeigt die Review-Übersicht.
- Nachrichten-Vorschlag-Flow:
  - Vorschlag wird angezeigt.
  - Aktion `a` setzt den Vorschlag lokal auf `approved`.
  - Es wird kein externer Versand ausgelöst.
- Aufgaben-Vorschlag-Flow:
  - Vorschlag wird angezeigt.
  - Aktion `a` erstellt lokal eine Aufgabe.
  - Der Aufgaben-Vorschlag wird auf `converted` gesetzt und enthält `created_task_id`.
- Rücksprung und Exit bleiben stabil:
  - `z` verlässt den Review-Übersichtsbereich.
  - `7` beendet die Run-Loop mit `Friday wird beendet.`.

## Safety-Bewertung
- Keine externen Aktionen (kein echter Versand, keine Terminbuchung, keine Provider-Aufrufe).
- Lokale SQLite-DB auf `tmp_path`.
- Sicherheitsflags unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy unverändert (`ja` löscht nicht, `JA` löscht).
- Keine Datenbankschema-Änderung.

## Empfehlung für Build Step 12G
- Als nächsten Schritt Review-Flow auf ungültige Eingaben und Wiederholungs-Pfade im Review- und Suggestion-Loop robuster testen (z. B. ungültige IDs, Sonderzeichen, doppelte Rücksprünge).
