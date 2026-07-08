# Privacy Cleanup DB Preview Model

## Ziel

Dieser Step ergaenzt ein isoliertes read-only Modell fuer spaetere SQLite-Cleanup-Previews.

Das Modell darf nur sichere Kandidaten zaehlen und keine Daten veraendern:

- keine SQLite-Schreiboperation,
- keine SQLite-Loeschung,
- keine Datenbankschema-Aenderung,
- keine CLI-Anbindung,
- keine externen Aktionen.

## Umgesetzte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/privacy_cleanup_db_preview.py` | Read-only Preview-Modell fuer erlaubte SQLite-Cleanup-Kandidaten |
| `friday/tests/test_privacy_cleanup_db_preview.py` | Unit-Tests mit `tmp_path` SQLite |

## Abgesicherte Preview-Bereiche

| Bereich | Bedingung | Token fuer spaeteren Write |
|---|---|---|
| Review-History | `message_suggestions.status = rejected` und `task_suggestions.status = converted` mit vorhandener Aufgabe | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | exakt ausgewaehlter `contact_id` | `KONTAKT LÖSCHEN` |

## Bewusst blockierte Bereiche

- Aufgaben-Cleanup ohne eigenes Task-Gate,
- Nachrichten-Cleanup ohne eigenes Message-Gate,
- Kalender-Cleanup ohne eigenes Calendar-Gate,
- aktive SQLite-DB,
- Datenbankschema,
- unbekannte Tabellen,
- unbekannte Bereiche ohne Future Gate.

## Read-only-Eigenschaften

Das Modell:

- oeffnet SQLite mit `mode=ro`,
- zaehlt nur bekannte Tabellen und sichere Statusfilter,
- gibt keine Nachrichtentexte oder Kontakt-Freitexte aus,
- markiert alle Ergebnisse als `preview_only` oder `blocked`,
- meldet `writes_performed = False`,
- meldet `deletes_performed = False`,
- meldet `schema_changed = False`,
- meldet `external_lookup_used = False`.

## Tests

Die Tests pruefen:

- Preview bleibt read-only,
- erlaubte Review-History-Kandidaten werden korrekt gezaehlt,
- pending Vorschlaege werden nicht als Cleanup-Kandidaten gezaehlt,
- Kontakt-Kontext braucht exakte Auswahl,
- Aufgaben und Schema-Cleanup bleiben blockiert,
- unbekannte Bereiche bleiben blockiert,
- fehlende DB erzeugt keinen neuen SQLite-Write.

## Safety-Bewertung

- Keine Produktlogik mit CLI-Anbindung.
- Keine echte Cleanup-Ausfuehrung.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Tests nutzen lokale `tmp_path` SQLite-Datenbanken.
- Safety-Flags bleiben unveraendert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unveraendert:
  - `"ja"` loescht nicht,
  - `"JA"` loescht,
  - `" JA "` bleibt durch `strip()` erlaubt.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup DB Preview Readiness Gate**.

Ziel:

- pruefen, ob das DB-Preview-Modell isoliert, read-only und sicher bleibt,
- keine CLI-Anbindung,
- keine SQLite-Loeschung.
