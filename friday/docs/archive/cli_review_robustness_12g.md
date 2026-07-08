# CLI Review Robustness 12G (Negativ- und Wiederholungsfälle)

## Geprüfte Review-Robustheit
- Nachrichten-Vorschlags-Review:
  - Ungültige Action (`x`) in der Detailansicht bleibt stabil.
  - Leere Action bleibt stabil.
  - Die betroffene Nachrichtenvorschlags-ID bleibt im Pending-Status.
- Aufgaben-Vorschlag-Review:
  - Ungültige Action (`x`) in der Detailansicht bleibt stabil.
  - Leere Action bleibt stabil.
  - Die betroffene Aufgaben-Vorschlag-ID bleibt im Pending-Status.

## Erwartete Texte/Verhalten
- Bei ungültiger Action wird `Ungültige Auswahl. Bitte erneut versuchen.` ausgegeben.
- Die Schleifen kehren ohne Absturz zurück und behalten lokale Pending-Daten.
- Kein externer Versand oder externe Aktion ist erforderlich.

## Safety
- Nur lokale SQLite auf `tmp_path` in Tests.
- Keine Änderungen an Produktlogik.
- Sicherheitsflags unverändert (`LOCAL`/`Sicherheitsmodi` bleiben aus).
- Keine Änderungen am Datenbankschema.
