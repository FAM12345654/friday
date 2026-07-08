# CLI Main Menu Paths Final Check

## Ziel

Dieser Schritt prueft die wichtigsten lokalen Hauptmenue- und Ruecksprungpfade nach dem Review-Activity- und Kontakt-Kontext-Ausbau.

Der Schritt fuehrt keine neue Produktfunktion ein.

## Gepruefte Hauptpfade

| Bereich | Hauptmenuepunkt | Status |
|---|---|---|
| Aufgaben | `1` | abgesichert |
| Nachrichten | `2` | abgesichert |
| Kalender-Vorschau | `3` | abgesichert |
| Morgenbriefing | `4` | abgesichert |
| Sicherheitsstatus | `5` | abgesichert |
| Review | `6` | abgesichert |
| Beenden | `7` | abgesichert |
| Hilfe | `8` | abgesichert |
| Kontakt-Kontext | `9` | abgesichert |
| Obsidian Brain Preview | `10` | abgesichert |
| Backup / Restore | `11` | abgesichert |
| Privacy Dashboard | `12` | abgesichert |

## Gepruefte Journey-Bereiche

- Hauptmenue startet und beendet sauber.
- Ungueltige Eingaben bleiben im Loop.
- Aufgabenmenue kann geoeffnet, genutzt und verlassen werden.
- Review-Journey kann vom Hauptmenue gestartet und verlassen werden.
- Review Activity Summary, Detail View, Statusfilter, Typfilter und Suche sind read-only nutzbar.
- Kontakt-Kontext-Menue kann vom Hauptmenue gestartet und verlassen werden.
- Kontakt anzeigen, suchen, bearbeiten und vergessen sind lokal abgesichert.
- Backup-/Restore- und Privacy-Menues kehren stabil zurueck.

## Neue Absicherung

Ergaenzt wurde ein Run-Level-Test fuer den Kontakt-Kontext-Pfad:

- Hauptmenue `9` oeffnet Kontakt-Kontext.
- Kontakt-Menue `5` kehrt ins Hauptmenue zurueck.
- Hauptmenue `7` beendet Friday sauber.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine echten E-Mails.
- Keine echten WhatsApp- oder SMS-Aktionen.
- Keine Wetter- oder Musikaktionen.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Tests

Relevante Testbereiche:

- `friday/tests/test_interface_main_menu_e2e.py`
- `friday/tests/test_interface_combined_review.py`
- `friday/tests/test_task_interface_flow.py`
- vollstaendige Suite `friday/tests`

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review-Journey komplett final pruefen.
