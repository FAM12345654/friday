# Friday Calendar Sources and Flow Gate

## Ziel

Dieses Gate dokumentiert den aktuellen Kalender-Stand fuer Friday: Outlook-ICS als read-only Quelle, Google-Kalender als hart gegatetes Write-Ziel, Termin-aus-Nachricht als Review-Flow und Termin-Loeschen als eigener harter Guard.

## Kalenderquellen

| Quelle | Modus | Zweck | Safety |
|---|---|---|---|
| Google Calendar | Lesen und gated Schreiben | Hauptkalender fuer echte Termin-Erstellung | Write nur mit `TERMIN SPEICHERN`, Haupt-Policy und Verbindung OK |
| Outlook ICS | Nur Lesen | z. B. PH-Termine aus veroeffentlichtem ICS-Feed | Keine Erstellung, kein Loeschen, keine Graph-API |
| Lokale SQLite-Termine | Lokal | Demo-/Preview- und lokale Referenzen | Keine externe Aktion |

## Outlook-ICS

- Provider: `friday/app/calendar_provider_ics.py`.
- Netzwerkzugriff ist nur in diesem Modul erlaubt und wird vom No-Network-Scanner eng allowlisted.
- Die ICS-URL wird lokal verschluesselt unter `local_data/accounts` gespeichert.
- Die URL wird nicht in API-Statusantworten, Tests oder Dokumentation ausgegeben.
- ICS ist read-only:
  - kein ICS-Write,
  - kein ICS-Delete,
  - keine Outlook Graph API,
  - kein automatischer Sync-Write.

## PH-Policy

Eine Outlook-ICS-Policy kann als Quelle gespeichert werden, z. B.:

```json
{
  "provider": "outlook_ics",
  "role": "source",
  "access": "read",
  "include_filters": {"title_contains": ["PH"]},
  "notes": "PH-Termine nur als Kontext verwenden."
}
```

Die Policy wird nur mit `POLICY SPEICHERN` gespeichert. Der Kalender-Merge liest Quellen isoliert: Eine defekte Quelle blockiert die restliche Kalenderansicht nicht.

## Termin aus Nachricht

Ablauf:

1. Nachricht wird lokal gelesen.
2. KI darf Rohsignale liefern; Python loest Datum und Uhrzeit deterministisch auf.
3. Friday erstellt eine reviewbare Vorschau.
4. Nutzer kann Titel, Datum, Uhrzeit und Ort bearbeiten.
5. Erst `TERMIN SPEICHERN` schreibt genau einen Google-Termin.

Es gibt keinen automatischen Kalender-Write aus einer Nachricht.

## Termin loeschen

- Neuer Guard: `friday/app/calendar_event_delete_guard.py`.
- Erforderlicher Token: `TERMIN LOESCHEN`.
- Loeschen prueft:
  - `ENABLE_REAL_CALENDAR=True`,
  - Haupt-Policy vorhanden,
  - Google-Verbindung OK,
  - exakter Delete-Token.
- Erst danach ruft Friday `GoogleCalendarProvider.delete_event(...)` auf.
- Lokale `calendar_entries`-Referenzen werden nur nach erfolgreichem Provider-Delete entfernt.

## Mobile Flow

Die Android-App zeigt:

- Kalenderquellen inklusive gefilterter Outlook-ICS-Termine,
- Termin-aus-Nachricht mit editierbaren Feldern,
- Token-Feld `TERMIN SPEICHERN`,
- Delete-Feld `TERMIN LOESCHEN` pro Google-Termin,
- Outlook-ICS-URL-Feld in der Account-Policy-Konfiguration.

## Safety-Bewertung

- `ENABLE_REAL_CALENDAR=True` bleibt eine bewusste Ausnahme.
- Diese Flags bleiben aus:
  - `ENABLE_REAL_EMAIL=False`
  - `ENABLE_REAL_WHATSAPP=False`
  - `ENABLE_REAL_SMS=False`
  - `ENABLE_REAL_WEATHER=False`
  - `ENABLE_REAL_MUSIC=False`
- Keine echten Nachrichten werden gesendet.
- Keine WhatsApp-/E-Mail-/SMS-Aktion wird aktiviert.
- ICS bleibt read-only.
- Google-Write und Google-Delete bleiben pro Event hart gegatet.

## Tests

Abgedeckt durch:

- `friday/tests/test_calendar_provider_ics.py`
- `friday/tests/test_calendar_ics_account_store.py`
- `friday/tests/test_calendar_event_delete_guard.py`
- `friday/tests/test_calendar_provider_google.py`
- `friday/tests/test_friday_api_setup_calendar_contact.py`
- Scanner-Tests fuer Netzwerk-Allowlist und Approval-Tokens

## Rollback

- Mobile: neue Eingabefelder nicht verwenden.
- Outlook-ICS: Policy deaktivieren oder loeschen.
- Google-Write/Delete: `ENABLE_REAL_CALENDAR=False` setzen und Scanner-Baseline entsprechend zuruecksetzen.
