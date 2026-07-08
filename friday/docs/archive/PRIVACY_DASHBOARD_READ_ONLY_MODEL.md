# Privacy Dashboard Read-Only Model

## Ziel

Dieses Dokument beschreibt das isolierte read-only Modell fuer ein spaeteres Privacy Dashboard.

Das Modell sammelt nur lokale Statusinformationen und fuehrt keine Schreibaktion aus.

## Implementierte Datei

- `friday/app/privacy_dashboard.py`

## Modellumfang

Das Modell liefert:

- App-Name,
- Local-Mode,
- SQLite-Storage-Status,
- Projektpfad,
- lokalen Datenpfad,
- Datenbankpfad,
- Safety-Flags,
- lokale Datenbereiche,
- deaktivierte externe Aktionen,
- hart gegatete Aktionen,
- Safety-Scanner-Namen.

## Read-only-Regeln

- Kein `input()`.
- Kein `print()`.
- Keine Datenbankabfrage.
- Keine Datei wird geschrieben.
- Keine Ordner werden erstellt.
- Keine externen Dienste werden geprueft.
- Keine Netzwerkaktion.
- Keine Provider-Aktion.
- Keine personenbezogenen Details werden ausgegeben.

## Datenbereiche

| Bereich | Anzeige |
|---|---|
| Aufgaben | lokaler SQLite-Hinweis und optionale Anzahl |
| Kontakt-Kontexte | lokaler SQLite-Hinweis und optionale Anzahl |
| Review-Vorschlaege | lokaler SQLite-Hinweis und optionale Anzahl |
| Backups | `local_data/backups/` und optionale Anzahl |
| Restore-Kopien | `local_data/restores/` und optionale Anzahl |

## Safety-Flags

Das Modell zeigt die erwarteten lokalen Werte:

```python
ENABLE_REAL_EMAIL = False
ENABLE_REAL_WHATSAPP = False
ENABLE_REAL_SMS = False
ENABLE_REAL_CALENDAR = False
ENABLE_REAL_WEATHER = False
ENABLE_REAL_MUSIC = False
REQUIRE_USER_APPROVAL = True
USE_SQLITE_STORAGE = True
```

## Tests

- `friday/tests/test_privacy_dashboard.py`

Die Tests pruefen:

- lokaler read-only Status,
- keine Pfaderstellung,
- Safety-Flags,
- deaktivierte externe Aktionen,
- sensible Details bleiben verborgen,
- optionale Summenwerte,
- harte Tokens.

## Safety-Bewertung

- Keine externen Aktionen.
- Kein Netzwerk.
- Keine Provider.
- Keine Datenbankschema-Aenderung.
- Keine Schreibaktion.
- Keine CLI-Anbindung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Privacy Dashboard Read-Only Readiness Gate.
