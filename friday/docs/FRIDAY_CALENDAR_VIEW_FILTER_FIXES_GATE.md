# Friday Calendar View Filter Fixes Gate

## Ziel

Dieses Gate stabilisiert die Kalenderansicht nach der Google-/Outlook-Kalenderanbindung.
Es behebt Anzeige- und Filterfehler ohne neue externe Aktionen zu aktivieren.

## Umgesetzte Fixes

| Bereich | Ergebnis |
|---|---|
| Mobile Kalenderliste | Die App rendert die zusammengefuehrte `merged_items`-Liste statt nur lokaler `items`. |
| Google Hauptkalender | `/api/calendar` sammelt jetzt aktivierte Kalender-Policies mit Rolle `main` und `source`. |
| Outlook PH-Filter | `title_contains: ["PH"]` matcht tokenbasiert: `PH`, `PH+D` und `PH-Dienst`, aber nicht `Philip`, `GRAPH` oder `graphisch`. |
| Datumsspanne | `/api/calendar` akzeptiert `range_start` und `range_end` fuer Mehrtagesansichten. |
| Tageszeitfenster | `/api/calendar` akzeptiert `day_start` und `day_end`; Events und freie Slots werden danach gefiltert. |
| Mobile Filter | Die App kann Heute, 7 Tage, 30 Tage oder einen eigenen Zeitraum mit Tageszeitfenster speichern und laden. |
| Dashboard | Die Terminanzahl nutzt die gemergte Kalenderansicht fuer den aktuellen Tag. |

## API-Verhalten

`GET /api/calendar` unterstuetzt weiterhin rueckwaerts kompatibel:

```text
/api/calendar?date=2026-07-15
```

Zusaetzlich:

```text
/api/calendar?range_start=2026-07-15&range_end=2026-07-16&day_start=08:00&day_end=18:00
```

Die Antwort enthaelt:

- `items` fuer lokale Kalenderitems,
- `source_events` fuer gelesene externe Quellen nach Policy-Filter,
- `merged_items` fuer die eigentliche Kalenderansicht,
- `free_slots` passend zum Datums- und Zeitfenster,
- `range_start`, `range_end`, `day_start`, `day_end`.

## Lokale Ansichtspraeferenzen

Die Kalenderansicht speichert nur lokale Anzeigeeinstellungen:

- Preset: `heute`, `7tage`, `30tage`, `custom`,
- Custom-Datum von/bis,
- Tagesstart und Tagesende.

Speicherort:

```text
calendar_view_prefs
```

Diese Tabelle enthaelt keine Termine, keine Zugangsdaten und keine externen Provider-Daten.

## Safety-Bewertung

- Keine neuen externen Aktionen.
- Kein automatisches Kalender-Schreiben.
- Kein automatisches Kalender-Loeschen.
- Google-Schreiben bleibt pro Termin hart gegatet mit `TERMIN SPEICHERN`.
- Google-Loeschen bleibt hart gegatet mit `TERMIN LOESCHEN`.
- Outlook-ICS bleibt read-only.
- E-Mail, WhatsApp, SMS, Wetter und Musik bleiben deaktiviert.
- Tests mocken Provider und fuehren keine Netzwerkzugriffe aus.

## Mobile Update

Die Aenderung ist JavaScript-/API-kompatibel und kann per Expo Preview OTA verteilt werden.

```powershell
eas update --channel preview --message "Kalender-Ansicht + Filter-Fixes" --non-interactive
```

## Empfehlung fuer naechsten Schritt

Als naechster Schritt ist ein kleiner Kalender-UX-Check sinnvoll:

- Gruppierung der `merged_items` pro Tag,
- sichtbarere Quellen-Chips,
- optionaler Refresh-Button direkt im Kalenderbereich.
