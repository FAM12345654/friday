# Review Contact Integration Plan 16A

## Ziel

16A plant, wie der Review-Flow später unbekannte Kontakte erkennt.

Dieser Schritt implementiert noch keine Review-Automatik und speichert nichts.

## Geplanter Source-Kontext

Für Nachrichten-Review gilt:

`nachrichten_review`

## Geplante Regeln

- Nur unbekannte Absender werden als Kontakt-Kontext-Kandidat betrachtet.
- Bekannte Kontakt-Kontexte erzeugen keine neue Rückfrage.
- Session-Suppression blockiert wiederholte Fragen im selben Lauf.
- Kein Prompt beim App-Start.
- Keine automatische Speicherung.
- Keine externen Lookup-/Provider-Aufrufe.

## Geplanter Ablauf für spätere Schritte

1. Review lädt lokale Nachricht.
2. Absender wird lokal normalisiert.
3. Repository prüft, ob Kontakt-Kontext bekannt ist.
4. Session-Suppression prüft, ob der Kontakt im Lauf übersprungen wurde.
5. Falls unbekannt und nicht unterdrückt: Candidate/Preview erzeugen.
6. In 16B nur Preview anzeigen.
7. In späterem Gate Draft-Prompt und Save-Approval ergänzen.

## Nicht-Ziele

- keine CLI-Eingabe im Review,
- keine Speicherung,
- keine Änderung an Message-/Task-Suggestion-Status,
- kein Kontaktimport,
- keine externen Aktionen.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine automatische Persistenz.
- Keine Datenbankschema-Änderung.
- Safety-Flags unverändert.
- Delete-Policy unverändert.

## Empfehlung für Build Step 16B

Nächster sinnvoller Schritt: `16B — Review Contact Candidate Preview`.

Dabei soll der Review nur einen lokalen Kandidatenhinweis anzeigen, ohne Eingabe und ohne Speicherung.
