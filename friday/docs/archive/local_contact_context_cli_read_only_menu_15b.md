# Contact CLI Read-Only Menu 15B

## Ziel

15B bindet den Kontakt-Kontext erstmals sichtbar in die lokale CLI ein.

Der Schritt bleibt bewusst **read-only**:

- Kontakte anzeigen,
- Kontakt-Kontexte suchen,
- zurück zum Hauptmenü,
- keine Bearbeitung,
- kein Löschen,
- keine automatische Speicherung.

## Umgesetzter CLI-Pfad

Im Hauptmenü wurde ergänzt:

- `9. Kontakt-Kontext anzeigen`

Im Kontakt-Kontext-Menü gibt es:

- `1. Kontakte anzeigen`
- `2. Kontakt suchen`
- `3. Kontakt bearbeiten (noch nicht aktiviert)`
- `4. Kontakt vergessen (noch nicht aktiviert)`
- `5. Zurück zum Hauptmenü`

## Read-Only-Verhalten

- Leere Kontaktliste zeigt: `Keine lokalen Kontakt-Kontexte vorhanden.`
- Suche ohne Treffer zeigt: `Keine passenden Kontakt-Kontexte gefunden.`
- Bearbeiten ist sichtbar, aber deaktiviert.
- Vergessen/Löschen ist sichtbar, aber deaktiviert.
- Kein Menüpfad schreibt oder löscht Daten.

## Tests

Ergänzt in `friday/tests/test_interface_main_menu_e2e.py`:

- Hauptmenüpunkt `9` öffnet Kontakt-Kontext und kehrt zurück.
- Leere Kontakt-Kontext-Liste bleibt stabil.
- Suche findet einen lokalen `tmp_path` SQLite Kontakt-Kontext.
- Deaktivierte Schreibpfade ändern Storage nicht.
- Hilfe erwähnt Kontakt-Kontext.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Änderung in diesem Schritt.
- Lokale SQLite-Preview wird nur gelesen.
- Delete-Policy unverändert.
- Safety-Flags unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`

## Empfehlung für Build Step 15C

Nächster sinnvoller Schritt: `15C — Contact CLI Edit Draft`.

Dabei soll Bearbeiten weiterhin nur als Vorschau/Draft funktionieren, ohne Speicherung.
