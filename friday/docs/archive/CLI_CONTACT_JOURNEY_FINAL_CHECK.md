# CLI Contact Journey Final Check

## Ziel

Dieser Schritt prueft die lokale Kontakt-Kontext-Journey vom Hauptmenue bis zur Rueckkehr und zum Exit.

Der Schritt fuehrt keine neue Produktfunktion ein.

## Gepruefte Journey

1. Friday startet lokal.
2. Hauptmenuepunkt `9` oeffnet das Kontakt-Kontext-Menue.
3. Kontakt-Kontext-Menuepunkt `5` kehrt zum Hauptmenue zurueck.
4. Hauptmenuepunkt `7` beendet Friday sauber.

## Weitere abgesicherte Kontakt-Pfade

- Kontakte anzeigen.
- Kontakt suchen.
- Suche ohne Treffer bleibt read-only.
- Bearbeiten zeigt zuerst eine Vorschau.
- Speichern ist nur mit `SPEICHERN` moeglich.
- `ja` und `JA` speichern nicht.
- Kontakt vergessen ist nur mit `KONTAKT LÖSCHEN` moeglich.
- falsche Loeschbestaetigungen loeschen nicht.
- unbekannte Kontakt-ID bleibt stabil.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine echten E-Mails.
- Keine echten WhatsApp- oder SMS-Aktionen.
- Keine Wetter- oder Musikaktionen.
- Kein Kontaktimport.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Speichern nur mit hartem Token.
- Loeschen nur mit hartem Token.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Tests

Relevante Testbereiche:

- `friday/tests/test_interface_main_menu_e2e.py`
- `friday/tests/test_contact_context_repository.py`
- vollstaendige Suite `friday/tests`

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Task-Journey final pruefen.
