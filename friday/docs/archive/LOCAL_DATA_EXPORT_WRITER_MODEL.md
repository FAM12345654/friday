# Local Data Export Writer Model

## Ziel

Dieses Dokument beschreibt das isolierte Writer-Modell fuer den lokalen Datenexport.

Der Writer ist noch nicht an die CLI angebunden. Er liest keine Datenbank, ruft keine externen Dienste auf und arbeitet nur mit explizit uebergebenen Daten.

## Implementierte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/local_data_export_writer.py` | Guarded Writer fuer lokalen Datenexport |
| `friday/tests/test_local_data_export_writer.py` | Tests fuer Writer, Guard-Pflicht, Inhalte und Ausschluesse |

## Writer-Verhalten

Der Writer erstellt nur dann Dateien, wenn:

- ein gueltiges Preview vorhanden ist,
- der Guard `allowed=True` liefert,
- der Token exakt `DATEN EXPORTIEREN` ist,
- Safety Smoke PASS uebergeben wurde,
- der Zielpfad unter `local_data/exports` liegt,
- alle Pflicht-Ausschluesse im Preview vorhanden sind,
- der Zielordner noch nicht existiert.

## Geschriebene Dateien

| Datei | Inhalt |
|---|---|
| `manifest.json` | Metadaten, Counts, Safety Smoke Status, Ausschluesse und Dateiliste |
| `tasks/tasks.json` | explizit uebergebene lokale Task-Daten |
| `tasks/tasks.md` | lesbare Markdown-Aufgabenuebersicht |
| `contacts/contact_contexts.json` | gefilterte Kontakt-Kontext-Zusammenfassung |
| `review/review_suggestions.json` | gefilterte Review-Zusammenfassung ohne rohe Nachrichtentexte |
| `safety/safety_status.json` | uebergebene lokale Safety-Flags |
| `docs/export_notes.md` | kurze lokale Exportnotizen |

## Gefilterte Inhalte

Kontakt-Kontexte werden auf erlaubte Felder reduziert:

- `contact_id`
- `display_name`
- `normalized_name`
- `contact_type`
- `nickname`
- `relationship_context`
- `source_context`
- `updated_at`

Review-Vorschlaege werden auf erlaubte Felder reduziert:

- `suggestion_id`
- `id`
- `type`
- `status`
- `created_task_id`
- `source`
- `title`

Rohe private Nachrichtentexte und sensible Kontakt-Freitexte werden nicht exportiert.

## Blockierfaelle

Der Writer blockiert:

- fehlendes Preview,
- falschen Token,
- Safety Smoke FAIL,
- Zielpfad ausserhalb `local_data/exports`,
- fehlende Pflicht-Ausschluesse,
- vorhandenen Zielordner.

## Nicht-Ziele

- Keine CLI-Anbindung.
- Keine Datenbankabfrage.
- Kein Repository-Lesen.
- Kein ZIP.
- Kein Cloud-Export.
- Kein Obsidian Export.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Kein Modell-/Provider-Aufruf.

## Tests

Abgedeckt durch `friday/tests/test_local_data_export_writer.py`:

- erfolgreicher Export schreibt erwartete Dateien,
- falscher Token schreibt nichts,
- Safety Smoke FAIL schreibt nichts,
- Ziel ausserhalb `local_data/exports` schreibt nichts,
- vorhandener Zielordner wird nicht ueberschrieben,
- Manifest enthaelt Counts und Ausschluesse,
- Kontaktdaten werden gefiltert,
- rohe Review-Nachrichtentexte werden gefiltert,
- Task-Markdown wird erzeugt,
- ZIP und Secrets werden nicht erzeugt,
- Safe-Flags bleiben korrekt.

## Safety-Bewertung

- Keine externe Aktion.
- Keine Netzwerkaktion.
- Keine Datenbankabfrage.
- Keine CLI-Anbindung.
- Keine Datenbankschema-Aenderung.
- Keine Safety-Flag-Aenderung.
- Delete-Policy unveraendert.
- Export nur aus explizit uebergebenen Daten.
- Guard-Pflicht vor Dateioperation.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export Writer Readiness Gate` folgen.

Das Gate sollte pruefen:

- Writer nutzt zwingend Guard,
- Writer liest keine Datenbank,
- Writer nutzt keine externen Aktionen,
- Writer schreibt nur unter `local_data/exports`,
- Tests und Safety Smoke bleiben gruen,
- CLI-Anbindung bleibt noch nicht freigegeben.
