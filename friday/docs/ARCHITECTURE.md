# Architektur von Friday (lokale Version)

## Lokale Speicherung

Friday speichert Demo-Daten und Nutzerdaten lokal:

- `friday/data/` enthält nur JSON-Seed-Dateien.
- `local_data/friday.db` ist die lokale Arbeitsdatenbank.

## Wichtig: data/ ist nicht die Arbeitsdatenbank

- `friday/data/` enthält nur Demo-JSON-Dateien.
- `local_data/friday.db` ist die echte lokale Arbeitsdatenbank.
- Falls versehentlich eine Datenbank in `friday/data/` entsteht, soll sie gelöscht werden.

## Storage-Schichten

- `friday/storage/database.py`
  - erzeugt die Tabellen.
  - erstellt `local_data/friday.db` falls nötig.
  - lädt Seed-Daten aus `friday/data/`.
  - achtet darauf, bestehende `tasks`-Tabellen mit einer neuen `priority`-Spalte nachzurüsten.
- `friday/storage/repositories.py`
  - liest und schreibt lokale Daten in SQLite.
  - enthält Aufgaben-Queries für Suche, Filter, Archivieren und Löschen.
  - sortiert offene Aufgaben und Such-/Filterergebnisse nach Fälligkeitsdatum, Priorität und ID.
- `friday/storage/sqlite_storage.py`
  - bleibt als kleiner Kompatibilitäts-Layer für alte Imports.
  - Aufgaben tragen jetzt optional `priority` für lokale Sortierung (`low`, `normal`, `high`, `urgent`).

Die Trennung macht das Projekt einfacher zu verstehen und vermeidet doppelten Code.

## Lokale Nachrichten-Vorschläge

- `message_suggestions` ist eine neue lokale SQLite-Tabelle für Vorschlags-Reviews.
- `MessageSuggestionRepository` verwaltet diese Datensätze lokal:
  - Erstellung (mit Schutz gegen Duplikate pro Nachricht + Typ)
  - Lesen (einzeln, für Nachricht, offen oder vollständig)
  - Statuswechsel (`pending`, `approved`, `rejected`, `edited`)
  - Bearbeiten von Entwurfstexten
- `MessageAgent` nutzt die Vorschlags-Repository:
  - erkennt lokal relevante Nachrichten
  - erstellt lokale Reply-Entwürfe
  - verwaltet Freigabe, Ablehnung und Bearbeitung
- Die Oberfläche zeigt Vorschläge über `review_pending_suggestions` an, ohne externen Versand zu starten.
- Auch im freigegebenen Zustand werden keine realen Nachrichten gesendet.

## Lokale Aufgaben-Vorschläge

- `task_suggestions` ist eine neue lokale SQLite-Tabelle für aufgabenartige Nachrichtenvorschläge.
- `TaskSuggestionRepository` verwaltet diese Datensätze lokal:
  - Erstellung (mit Schutz gegen Duplikate pro Nachricht)
  - Lesen (einzeln, offen oder vollständig)
  - Statuswechsel (`pending`, `approved`, `rejected`, `edited`, `converted`)
  - Bearbeitung von Feldern (Titel, Kategorie, Datum, Notiz, Priorität)
- `MessageAgent` erstellt daraus lokale Vorschläge, wenn `detect_intent(text) == "task"`.
- `TaskAgent` erstellt die echten lokalen Tasks erst nach Freigabe im Review-Flow.
- Bei Freigabe (`converted`) wird die erzeugte Task-ID im `created_task_id` gespeichert.

## Kombinierter Review-Flow

- `FridayInterface.review_pending_suggestions()` koordiniert jetzt Nachrichtens- und Aufgaben-Vorschläge in einer gemeinsamen Übersicht.
- Vor dem Review werden beide Vorschlagstypen lokal erzeugt:
  - Termin-Reply-Entwürfe (`generate_local_suggestions`)
  - Aufgaben-Vorschläge (`generate_local_task_suggestions`)
- Die Oberfläche zeigt offene Vorschläge je Bereich und lässt den Nutzer gezielt auf einen Bereich wechseln.
- Message- und Task-Workflows bleiben lokal:
  - Nachrichten: Freigabe/Abwertung/Bearbeitung bleibt lokal.
  - Aufgaben: Aufgabe wird erst nach Bestätigung lokal als Task erstellt.
  - Kalender-Slots werden nur als Entwurfstext verknüpft.
- Nach der Konvertierung wird ein Task-Vorschlag lokal auf `converted` gesetzt und bleibt nicht mehr im offenen Review.

## Lokale Intent-Erkennung

- `MessageAgent` klassifiziert eingehende Nachrichten mit einfachen Regeln in:
  - `scheduling`
  - `task`
  - `question`
  - `info`
  - `unclear`
- Die Erkennung ist lokal, regelbasiert und nutzt keine KI oder externen Dienst.
- Die Kategorie bestimmt aktuell, ob automatisch ein Antwort-Entwurf erzeugt wird.
- Nur die Klasse `MessageAgent` enthält die Intent-Logik, andere Bereiche bleiben unverändert.

## Lokale Kalender-Vorschläge im Review

- `calendar_suggestions` speichert lokale Terminvorschläge je Nachricht in SQLite.
- `CalendarSuggestionRepository` verwaltet diese Datensätze lokal:
  - Erstellen von Slots pro Nachricht/Datum/Uhrzeit
  - Abruf aller Slots oder nur offener (`pending`) Slots
  - Statuswechsel auf `selected` und `rejected`
- `CalendarAgent` nutzt lokale Kalenderdaten und ergänzt Slot-Vorschläge für ein Nachricht-Datum.
- In der Nachrichtenprüfung werden die Slots angezeigt und per ID auswählbar gemacht.
- Die Auswahl eines Slots ergänzt den lokalen Entwurfstext, z. B.:
  - `Möglicher Termin: 2026-07-05 von 10:00 bis 11:00.`
- Es werden keine echten Kalenderereignisse erstellt.

## Sicherheitsrahmen

- Externe Dienste sind deaktiviert.
- Keine echten Nachrichten.
- Keine echten Kalender-Ereignisse.
- Keine echten WhatsApp-, E-Mail-, SMS-, Wetter- oder Musik-API-Aufrufe.

## Aufgabenverwaltung

- `TaskRepository` kapselt SQL für Tasks:
  - Laden von offenen Aufgaben (ohne `done` und `archived`)
  - Suche in `title` und `notes`
  - Filter nach `status`, `category`, `due_date`
  - Archivieren (`status = 'archived'`)
  - Permanentes Löschen
- `TaskAgent` ist eine dünne Schicht über `TaskRepository` und gibt Methoden für die Oberfläche weiter.
- Die Oberfläche (`friday/app/interface.py`) ruft diese Methoden lokal über kurze Eingabe-Flows auf.
- Lokale Aufgabenkorrekturen laufen ohne ApprovalAgent.
- Die Freigaben im Programm bleiben für Nachrichten- und Kalender-Vorschläge getrennt.

## Aufgaben suchen, archivieren und löschen

- Suche + Filter laufen vollständig lokal über SQLite `LIKE` und optionale `WHERE`-Filter.
- Archivieren ist der sichere Standardweg: Task bleibt erhalten, Status ändert sich auf `archived`.
- Löschen ist bewusst separat und verlangt zusätzliche Bestätigung, bevor der Datensatz aus `tasks` entfernt wird.
