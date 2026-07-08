# Review Activity Search CLI Implementation

## Ziel

Dieser Schritt bindet die lokale Review Activity Search read-only in den bestehenden Review-Bereich der CLI ein.

## Umsetzung

Geaenderte Datei:

`friday/app/interface.py`

Ergaenzungen:

- Import von `build_review_activity_search`.
- Neuer Review-Menuepunkt `10. Review-Aktivitaet durchsuchen`.
- Neue Methode `_show_review_activity_search()`.
- Leere Eingabe oder `z` kehrt ohne Aenderung zur Review-Uebersicht zurueck.
- Zu kurze Suchbegriffe zeigen eine sichere Fehlermeldung.
- Trefferlisten bleiben read-only und nutzen die bestehende Detail-Item-Ausgabe.
- Begrenzte Trefferlisten zeigen die Begrenzung sichtbar an.

## Tests

Erweiterte Testdatei:

`friday/tests/test_interface_combined_review.py`

Abgesicherte Faelle:

- Suche nach `converted` zeigt passende lokale Review-Items.
- Suche ohne Treffer zeigt eine sichere Leermeldung.
- Zu kurze Suchbegriffe bleiben read-only.
- Es wird kein Token verlangt.
- Pending-Vorschlaege bleiben bei Suchpfaden unveraendert.

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

Naechster sinnvoller Build Step: Review Activity Search CLI Readiness Gate.
