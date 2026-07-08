# Contact CLI Save Approval 15D

## Ziel

15D ergänzt Speichern im Kontakt-Kontext-Menü nur nach expliziter harter Freigabe.

Der sichere Token lautet:

`SPEICHERN`

Alle anderen Eingaben brechen ab.

## Umgesetzter Ablauf

1. Nutzer öffnet `Kontakt-Kontext anzeigen`.
2. Nutzer wählt `Kontakt bearbeiten (Vorschau)`.
3. Nutzer wählt eine Kontaktart.
4. Friday zeigt eine Vorschau.
5. Friday fragt nach dem Speichertoken.
6. Nur exakt `SPEICHERN` aktualisiert den lokalen Kontakt-Kontext.

## Bewusst blockierte Eingaben

- Enter speichert nicht.
- `ja` speichert nicht.
- `JA` speichert nicht.
- Whitespace oder andere Texte speichern nicht.

## Gespeicherte Felder

Nur nach `SPEICHERN`:

- `contact_type`
- `source_context = person_bearbeiten`
- `user_approved_persistence = 1`
- `sensitivity_checked = 1`

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine automatische Speicherung.
- Kein Speichern ohne harten Token.
- Keine Datenbankschema-Änderung.
- Delete-Policy für Tasks unverändert.

## Tests

Ergänzt in `friday/tests/test_interface_main_menu_e2e.py`:

- `SPEICHERN` speichert lokal.
- Enter bricht ab.
- `JA` bricht ab.
- `ja` bricht ab.
- Storage bleibt bei Abbruch unverändert.

## Empfehlung für Build Step 15E

Nächster sinnvoller Schritt: `15E — Contact CLI Forget Flow`.

Der Lösch-/Vergessen-Pfad braucht einen eigenen harten Token, z. B. `KONTAKT LÖSCHEN`.
