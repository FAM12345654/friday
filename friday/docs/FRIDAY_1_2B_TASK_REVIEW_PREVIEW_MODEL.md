# Friday 1.2B Task Review Preview Model

## Ziel

Build Step 1.2B ergaenzt ein isoliertes, lokales Read-only-Modell fuer Aufgaben-Reviews.

Das Modell fasst vorhandene Task-Daten zusammen, ohne Aufgaben zu aendern, ohne Datenbankzugriff und ohne CLI-Anbindung.

## Umgesetzte Bausteine

- Neues Modul: `friday/app/task_review_preview.py`
- Neue Tests: `friday/tests/test_task_review_preview.py`
- Read-only-Datenklassen:
  - `TaskReviewItem`
  - `TaskReviewSummary`
  - `TaskReviewPreview`
- Neue Funktion:
  - `build_task_review_preview(tasks, today)`

## Abgesicherte Vorschauwerte

- Gesamtanzahl der Aufgaben
- offene Aufgaben
- erledigte Aufgaben
- archivierte Aufgaben
- heute faellige offene Aufgaben
- ueberfaellige offene Aufgaben
- offene Aufgaben ohne gueltiges Faelligkeitsdatum
- offene Aufgaben mit hoher oder dringender Prioritaet

## Safety-Bewertung

- Keine Produktlogik fuer bestehende Task-Aktionen geaendert.
- Keine Datenbankschema-Aenderung.
- Kein Schreibzugriff.
- Kein `input()`.
- Kein `print()`.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Testabdeckung

Die neuen Tests pruefen:

- Status-Zaehler fuer offene, erledigte und archivierte Aufgaben.
- Erkennung von heute faelligen und ueberfaelligen Aufgaben.
- stabiles Verhalten bei fehlenden oder ungueltigen Faelligkeitsdaten.
- Prioritaetszaehler fuer `high` und `urgent`.
- Read-only-/No-External-Flags.
- keine Mutation der uebergebenen Task-Daten.

## Empfehlung fuer Build Step 1.2C

Build Step 1.2C sollte die Task-Review-Preview als lokalen CLI-Plan oder read-only CLI-Pfad vorbereiten.

Empfohlener Umfang:

- keine Task-Aenderungen,
- keine DB-Schema-Aenderung,
- keine externen Aktionen,
- Preview nur anzeigen,
- Rueckkehr ins Aufgabenmenue stabil testen.
