# Task Contact Integration 17D

## Ziel

17D übernimmt bekannte Kontakt-Kontexte beim Umwandeln eines Aufgaben-Vorschlags in eine lokale Aufgabe.

## Umgesetztes Verhalten

- Bei `Aufgaben-Vorschlag als lokale Aufgabe erstellen`
- sucht Friday den lokalen Kontakt-Kontext zum Nachrichtenabsender.
- Wenn vorhanden, wird ein Snapshot an die Task-Notizen angehängt.
- Die Aufgabe bleibt eine normale lokale Aufgabe.
- Es gibt keine `contact_id`-Spalte und keine Schema-Migration.

## Snapshot-Format

```text
Kontakt-Snapshot:
Quelle: ...
Kontaktart: ...
Beziehungskontext: ...
```

Der Beziehungskontext wird nur übernommen, wenn Persistenz freigegeben und Sensitivity geprüft ist.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Änderung.
- Kein Kontaktimport.

## Empfehlung für Build Step 17E

Nächster Schritt: `17E — Task Contact Readiness Gate`.
