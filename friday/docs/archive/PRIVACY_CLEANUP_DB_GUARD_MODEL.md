# Privacy Cleanup DB Guard Model

## Ziel

Dieser Step ergaenzt ein isoliertes Guard-Modell fuer spaetere SQLite-basierte Privacy-Cleanup-Writes.

Das Modell prueft nur, ob ein spaeterer Write theoretisch erlaubt waere. Es fuehrt keinen Write aus.

## Umgesetzte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/privacy_cleanup_db_guard.py` | Side-effect-free Guard fuer spaetere SQLite-Cleanup-Writes |
| `friday/tests/test_privacy_cleanup_db_guard.py` | Fokus-Tests fuer Guard-Regeln |

## Guard-Regeln

Der Guard erlaubt nur, wenn alle Bedingungen erfuellt sind:

- Cleanup-Bereich ist bekannt,
- passende read-only Preview liegt vor,
- Preview-Item ist `preview_only`,
- Tabellen- und Statusfilter entsprechen der sicheren Policy,
- sensible Inhalte sind ausgeblendet,
- Kandidatenanzahl ist groesser als `0`,
- Backup ist vorhanden,
- Transaktion ist verfuegbar,
- Rollback ist verfuegbar,
- Safety Smoke ist `PASS`,
- externe Aktionen sind deaktiviert,
- harter Token passt exakt.

## Erlaubte Bereiche

| Bereich | Token |
|---|---|
| Review-History | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `KONTAKT LÖSCHEN` |

## Bewusst blockiert

- unbekannte Cleanup-Bereiche,
- fehlende Preview,
- blockierte Preview-Items,
- unsichere Tabellenbereiche,
- unsichere Statusfilter,
- sichtbare sensible Inhalte,
- fehlendes Backup,
- fehlende Transaktion,
- fehlender Rollback,
- Safety-Smoke-Fehler,
- externe Aktionen,
- leere Kandidatenmenge,
- falsche Tokens wie `ja`, `JA` oder Tokens mit Leerzeichen.

## Side-Effect-Grenzen

Das Guard-Modell:

- oeffnet keine SQLite-Verbindung,
- loescht keine Datensaetze,
- schreibt keine Dateien,
- aendert kein Datenbankschema,
- fragt keine Eingabe ab,
- gibt nichts per `print()` aus,
- nutzt keine externen Dienste.

## Safety-Bewertung

- Keine SQLite-Schreiboperation.
- Keine SQLite-Loeschung.
- Keine Datenbankschema-Aenderung.
- Keine CLI-Anbindung.
- Keine externen Aktionen.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB Guard Readiness Gate**.

Ziel:

- Guard-Modell final pruefen und dokumentieren,
- keine SQLite-Loeschung,
- keine CLI-Anbindung,
- keine Writer-Implementierung.
