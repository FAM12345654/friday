# Task Contact Snapshot Preview 17B

## Ziel

17B zeigt Kontakt-Kontext bei Aufgaben-Vorschlägen als lokalen Snapshot.

Der Schritt ändert kein Datenbankschema.

## Umgesetztes Verhalten

- Wenn ein Aufgaben-Vorschlag aus einer Nachricht kommt,
- und der Absender als lokaler Kontakt-Kontext bekannt ist,
- zeigt Friday im Task-Review:
  - Quelle,
  - Kontaktart,
  - Beziehungskontext nur, wenn Persistenz freigegeben und Sensitivity geprüft ist.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine Datenbankschema-Änderung.
- Keine automatische Kontaktanlage.
- Nur lokale Anzeige.

## Empfehlung für Build Step 17C

Nächster Schritt: `17C — Task Contact Export Gate`.
