# Contact CLI Edit Draft 15C

## Ziel

15C ergänzt im lokalen Kontakt-Kontext-Menü einen Bearbeiten-Pfad als reine Vorschau.

Der Schritt speichert keine Änderungen und löscht keine Daten.

## Umgesetzter CLI-Pfad

Im Kontakt-Kontext-Menü:

- `3. Kontakt bearbeiten (Vorschau)`

Der Flow:

1. Nutzer gibt eine lokale Kontakt-ID ein.
2. Friday zeigt den bestehenden Kontakt-Kontext-Prompt.
3. Nutzer wählt eine Kontaktart oder überspringt.
4. Friday zeigt nur eine Vorschau.
5. Storage bleibt unverändert.

## Abgesicherte Verhaltensweisen

- Auswahl `1-7` erzeugt eine Vorschau.
- Auswahl `8` überspringt den Draft.
- Ungültige Eingaben bleiben lokal und zeigen die Standardmeldung.
- `JA` ist im Kontakt-Kontext-Draft weiterhin ungültig.
- Es wird keine SQLite-Zeile geändert.
- Der Forget/Löschpfad bleibt deaktiviert.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine automatische Speicherung.
- Keine Löschung.
- Keine Datenbankschema-Änderung.
- Safety-Flags unverändert.
- Delete-Policy für Tasks unverändert.

## Tests

Ergänzt in `friday/tests/test_interface_main_menu_e2e.py`:

- Draft-Auswahl erzeugt Preview und verändert Storage nicht.
- Ungültige Draft-Eingabe verändert Storage nicht.
- Skip verändert Storage nicht.
- Forget-Pfad bleibt deaktiviert.

## Empfehlung für Build Step 15D

Nächster sinnvoller Schritt: `15D — Contact CLI Save Approval`.

Dabei darf Speicherung nur nach hartem Token wie `SPEICHERN` erfolgen.
