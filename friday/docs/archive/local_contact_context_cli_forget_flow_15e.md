# Contact CLI Forget Flow 15E

## Ziel

15E ergänzt im lokalen Kontakt-Kontext-Menü einen kontrollierten Vergessen-/Löschpfad.

Der Löschvorgang ist lokal und erfordert einen harten Token:

`KONTAKT LÖSCHEN`

## Umgesetzter Ablauf

1. Nutzer öffnet `Kontakt-Kontext anzeigen`.
2. Nutzer wählt `Kontakt vergessen`.
3. Nutzer gibt eine Kontakt-ID ein.
4. Friday zeigt eine Warnung und den Namen.
5. Nur exakt `KONTAKT LÖSCHEN` entfernt den lokalen Kontakt-Kontext.

## Blockierte Eingaben

- Enter löscht nicht.
- `ja` löscht nicht.
- `JA` löscht nicht.
- Jeder andere Text löscht nicht.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Kein Kontaktimport.
- Löschen nur lokal.
- Löschen nur mit hartem Token.
- Keine Datenbankschema-Änderung.
- Task-Delete-Policy unverändert.

## Tests

Ergänzt in `friday/tests/test_interface_main_menu_e2e.py`:

- falscher Token löscht nicht,
- `KONTAKT LÖSCHEN` löscht lokal,
- unbekannte Kontakt-ID bleibt stabil.

## Empfehlung für Build Step 15F

Nächster sinnvoller Schritt: `15F — Contact CLI Readiness Gate`.

Darin sollte der komplette Contact-CLI-Block 15A-15E final geprüft und dokumentiert werden.
