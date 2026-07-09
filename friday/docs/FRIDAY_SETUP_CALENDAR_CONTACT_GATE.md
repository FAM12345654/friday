# Friday Setup, Calendar Extraction and Contact Category Gate

## Ziel

Dieses Gate dokumentiert den neuen lokalen Setup-Status, die deterministische Termin-Erkennung und die vereinheitlichten Kontakt-Kategorien in Friday.

## Umgesetzte Bereiche

| Bereich | Status |
|---|---|
| Setup-Status API | umgesetzt |
| Mobile Setup-Screen | umgesetzt |
| Termin-Erkennung aus Nachrichtentext | umgesetzt als Review-Vorschlag |
| Deterministische Datum-/Zeit-Aufloesung | umgesetzt in Python |
| Kalender-Link | umgesetzt als Vorschau-Link |
| Kontakt-Kategorien | `familie`, `arbeit`, `freund`, `kunde`, `dienstleister`, `sonstiges`, `unbekannt` |

## Architekturentscheidung fuer Termine

Die lokale KI darf nur Rohinformationen liefern oder als Vorschlagsquelle dienen. Die finale Datum-/Zeit-Aufloesung passiert deterministisch in Python.

Abgesicherte Beispiele:

- `15.07.2026 10:00` wird als explizites Datum mit Uhrzeit erkannt.
- `Donnerstag um 10 Uhr` wird relativ zu einem Python-Basisdatum berechnet.
- `morgen halb 4` wird deterministisch zu `15:30`, nicht durch das Modell geraten.
- Texte ohne vollstaendigen Termin erzeugen keinen Kalender-Vorschlag.

## Review-Flow

Ein erkannter Termin wird nur als lokaler Vorschlag gespeichert:

- Status: `pending`
- Typ: `calendar_event`
- Kein echter Kalendertermin
- Kein externer API-Aufruf
- Nutzer muss den Vorschlag spaeter pruefen

## Mobile Setup-Screen

Der neue Setup-Screen zeigt:

- lokalen Friday-Status,
- lokale KI-/Modell-Information,
- Kalender-Status,
- E-Mail-/WhatsApp-Status,
- Safety-Flags,
- Setup-Schritte.

## Kontakt-Kategorien

Kontakt-Kategorien werden lokal normalisiert:

- `family` -> `familie`
- `work` -> `arbeit`
- `friend` -> `freund`
- `customer` -> `kunde`
- `other` -> `sonstiges`

Die Klassifizierung ist Preview-only:

- keine Speicherung,
- keine externe Suche,
- kein Provider-Aufruf.

## Safety-Bewertung

- `ENABLE_REAL_CALENDAR = False`
- Kein echter Kalender-Write.
- Kein echter Nachrichtenversand.
- Kein WhatsApp-Senden.
- Kein SMS-Senden.
- Keine Cloud-KI.
- Keine neuen Credentials.
- Keine Datenbankschema-Aenderung.
- Kalender-Links sind nur Vorschau/Komfort, kein automatisches Erstellen.

## Validierung

Relevante Tests:

- `friday/tests/test_calendar_event_extraction.py`
- `friday/tests/test_contact_category_classifier.py`
- `friday/tests/test_friday_api_setup_calendar_contact.py`

Empfohlene Smoke Checks:

```powershell
python -m pytest friday/tests/test_calendar_event_extraction.py friday/tests/test_contact_category_classifier.py friday/tests/test_friday_api_setup_calendar_contact.py
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Naechster sinnvoller Schritt

Termin-Vorschlaege koennen spaeter im bestehenden Review-/Suggestion-Flow sichtbarer gemacht und editierbar gemacht werden. Auch dann bleibt echter Kalender-Write blockiert, bis ein separates hartes Kalender-Gate beschlossen wird.

