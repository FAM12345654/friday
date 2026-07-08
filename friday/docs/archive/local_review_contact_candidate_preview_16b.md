# Review Contact Candidate Preview 16B

## Ziel

16B ergänzt im Review-Flow eine lokale Vorschau für unbekannte Absender.

Der Schritt zeigt nur Hinweise und speichert nichts.

## Umgesetzter Ablauf

1. Review lädt lokale Nachrichten.
2. Friday prüft pro Absender das lokale `ContactContextRepository`.
3. Bekannte Kontakt-Kontexte werden übersprungen.
4. Unbekannte Absender erzeugen einen lokalen Hinweis:
   `Kontakt-Kontext möglich: ... ist noch unbekannt.`
5. Es gibt keine Eingabe und keine Speicherung.

## Nicht-Ziele

- kein Prompt im Review,
- keine Kontaktart-Auswahl,
- keine automatische Persistenz,
- kein Kontaktimport,
- keine externen Lookups.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Speicherung.
- Keine Datenbankschema-Änderung.
- Session-Suppression wird berücksichtigt, aber in diesem Schritt nicht verändert.
- Safety-Flags unverändert.

## Tests

Ergänzt in `friday/tests/test_interface_combined_review.py`:

- unbekannter Absender zeigt Kontakt-Kontext-Hinweis,
- bekannter Kontakt-Kontext blockiert den Hinweis,
- Preview erzeugt keine neue Kontakt-Kontext-Zeile.

## Empfehlung für Build Step 16C

Nächster sinnvoller Schritt: `16C — Review Contact Draft Prompt`.

Dann darf der Review den vorhandenen Draft-Flow verwenden, aber weiterhin ohne Speicherung.
