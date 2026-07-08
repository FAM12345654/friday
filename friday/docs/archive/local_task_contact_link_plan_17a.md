# Task Contact Link Plan 17A

## Ziel

17A plant, wie Aufgaben später einen Kontaktbezug bekommen können.

Dieser Schritt implementiert noch keine Task-Änderung.

## Bewertete Varianten

| Variante | Vorteil | Nachteil | Empfehlung |
|---|---|---|---|
| `contact_id` im Task | sauber relational | Datenbankschema-Änderung nötig | später |
| Snapshot in Task-Notizen | keine Migration | weniger robust | zuerst |

## Empfehlung

Für den nächsten kleinen Schritt wird ein Snapshot empfohlen:

- Quelle/Absender,
- Kontaktart,
- optionaler Beziehungskontext nur nach Freigabe.

Damit bleibt der erste Task-Kontaktbezug ohne Datenbankschema-Änderung möglich.

## Safety-Grenzen

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Kein Kontaktimport.
- Keine automatische Übernahme sensibler Daten.
- Keine Datenbankschema-Änderung in 17A.

## Nächster Schritt

`17B — Task Contact Snapshot Preview`

Dabei soll nur eine lokale Vorschau entstehen, bevor Kontaktinfos in Tasks übernommen werden.
