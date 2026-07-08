# Privacy Cleanup DB Writer Model

## Ziel

Dieser Step ergaenzt ein isoliertes SQLite Privacy Cleanup DB Writer Model.

Der Writer fuehrt nur dann lokale SQLite-Deletes aus, wenn ein zuvor erlaubtes DB-Guard-Ergebnis vorliegt.

## Umgesetzte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/privacy_cleanup_db_writer.py` | Guarded SQLite-Cleanup-Writer mit Transaktion und Rollback |
| `friday/tests/test_privacy_cleanup_db_writer.py` | Fokus-Tests fuer Review-History- und Kontakt-Kontext-Cleanup |

## Erlaubte Writer-Bereiche

| Bereich | Loeschumfang |
|---|---|
| Review-History | Nur `message_suggestions.status = rejected` und `task_suggestions.status = converted` mit vorhandener lokaler Aufgabe |
| Kontakt-Kontext | Nur exakt ausgewaehlter `contact_id` |

## Sicherheitsregeln

Der Writer:

- akzeptiert nur `guard_result.allowed is True`,
- verwendet eine explizite SQLite-Transaktion,
- nutzt nur feste, bekannte SQL-Statements,
- nutzt parameterisierte SQL-Werte,
- loescht keine pending Vorschlaege,
- loescht keine Aufgaben,
- loescht keine Nachrichten,
- loescht keine Kalenderdaten,
- aendert kein Datenbankschema,
- rollt bei Kandidaten-Abweichungen zurueck,
- gibt nur sichere Zaehler zurueck.

## Tests

Die Tests pruefen:

- Review-History-Cleanup loescht nur sichere Kandidaten,
- pending Vorschlaege bleiben erhalten,
- lokale Aufgaben bleiben erhalten,
- Kontakt-Kontext-Cleanup loescht nur den ausgewaehlten Kontakt,
- nicht erlaubter Guard blockiert,
- Kontakt-Cleanup ohne Auswahl blockiert,
- Kandidaten-Abweichung fuehrt zu Rollback,
- Side-Effect-Flags bleiben sicher.

## Nicht verbunden

Der Writer ist noch nicht verbunden mit:

- CLI,
- Privacy Dashboard,
- automatischem Cleanup,
- externen Diensten.

## Safety-Bewertung

- SQLite-Deletes nur in isoliertem Writer und nur mit Guard-Freigabe.
- Keine CLI-Anbindung.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine sensiblen Inhalte in Ergebnisdaten.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB Writer Readiness Gate**.

Ziel:

- Writer-Modell final pruefen und dokumentieren,
- weiterhin keine CLI-Anbindung,
- weiterhin keine automatische Bereinigung.
