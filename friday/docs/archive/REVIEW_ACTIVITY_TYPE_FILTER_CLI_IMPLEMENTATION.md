# Review Activity Type Filter CLI Implementation

## Ziel

Dieser Schritt bindet den lokalen Review Activity Type Filter read-only in den bestehenden Review-Bereich der CLI ein.

## Umsetzung

Geaenderte Datei:

`friday/app/interface.py`

Ergaenzungen:

- Import von `build_review_activity_type_filter`.
- Neuer Review-Menuepunkt `9. Review-Aktivitaet nach Typ filtern`.
- Neue Methode `_show_review_activity_type_filter()`.
- Eingabe `all`, `message`, `task`.
- Leere Eingabe oder `z` kehrt ohne Aenderung zur Review-Uebersicht zurueck.
- Ungueltige Eingaben zeigen eine sichere Fehlermeldung.

## Tests

Erweiterte Testdatei:

`friday/tests/test_interface_combined_review.py`

Abgesicherte Faelle:

- Typfilter `message` zeigt Nachrichten-Items.
- Typfilter `task` zeigt Aufgaben-Items.
- Ungueltiger Typfilter bleibt read-only.
- Es wird kein Token verlangt.
- Pending-Vorschlaege bleiben bei ungueltiger Eingabe unveraendert.

## Safety-Bewertung

- CLI-Anbindung bleibt read-only.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine echten E-Mails.
- Keine echten WhatsApp- oder SMS-Aktionen.
- Keine Wetter- oder Musikaktionen.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Keine Schreiboperation.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Type Filter CLI Readiness Gate.
