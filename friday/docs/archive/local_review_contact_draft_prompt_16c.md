# Review Contact Draft Prompt 16C

## Ziel

16C erlaubt im Review-Flow eine lokale Kontakt-Kontext-Auswahl als Draft.

Der Schritt nutzt den bestehenden Prompt-Renderer und Parser.

## Umgesetzter Ablauf

- Review zeigt unbekannte Absender als Kontakt-Kontext-Hinweise.
- Bereich `4. Kontakt-Kontext prüfen` öffnet den Draft.
- Nutzer kann Kontaktart auswählen oder überspringen.
- Ungültige Eingaben zeigen die Standardmeldung.
- Ohne Save-Token wird nichts gespeichert.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine automatische Speicherung.
- Session-Skip bleibt nur im aktuellen Lauf.
- Keine Datenbankschema-Änderung.

## Empfehlung für Build Step 16D

Nächster Schritt: `16D — Review Contact Save Approval`.
