# Local Contact Context Plan 13E

## Ziel

Planung für eine lokale Kontakt-Kontext-Funktion, damit Friday Personen über wiederholte Konversationen hinweg konsistent einordnen kann, ohne dabei neue DB-Strukturen oder Produktlogik in diesem Schritt zu ändern.

## Warum Kontakt-Kontext

Friday soll relevante Personen lokal besser erkennen und einordnen können:

- Weniger Rückfragen bei wiederkehrenden Personen.
- Bessere Kontextqualität für Nachrichten- und Aufgabenvorschläge.
- Klar erkennbare lokale Beziehungsklassen.

## Nicht-Ziele in 13E

- Keine Implementierung.
- Keine neue DB-Tabelle.
- Keine Migration.
- Kein Kontaktimport.
- Keine externen APIs.
- Keine WhatsApp-/E-Mail-/SMS-Integration.
- Keine sensiblen Personenprofile ohne explizite Freigabe.

## Vorgeschlagene Kontaktarten

| Kontaktart | Bedeutung |
|---|---|
| kunde | Geschäftlicher Kunde |
| kollege | Kollegin/Kollege |
| mitarbeiter | Mitarbeiter/in |
| familie | Familie |
| freund | Freund/Bekannter |
| dienstleister | Dienstleister |
| sonstiges | Sonstige Beziehung |
| unbekannt | Noch nicht eingeordnet |

## Mögliche Datenfelder

| Feld | Zweck | Sensitivität |
|---|---|---|
| contact_id | interne ID | niedrig |
| display_name | angezeigter Name | mittel |
| normalized_name | Such-/Vergleichsname | mittel |
| contact_type | lokale Beziehungskategorie | mittel |
| nickname | Kurzname/Spitzname | mittel |
| relationship_context | kurzer Nutzerkontext | mittel |
| source_context | woher Kontext stammt (`manuell`, `nachricht`, `aufgabe`, `kalender`, `importiert_später`) | niedrig |
| notes | optionale lokale Notiz | mittel bis hoch |
| last_seen_at | letzte lokale Sichtung | niedrig |
| created_at | Erstellung | niedrig |
| updated_at | letzte Änderung | niedrig |

## UX-Entwurf

- Wenn Friday auf eine relevante unbekannte Person trifft, wird eine kurze Frage gestellt:
  - „Wer ist X für dich? (Kunde/Kollege/Mitarbeiter/Familie/Freund/Dienstleister/Sonstiges)“
- Optional nach einem Spitznamen.
- Optional nach typischem Kontext.
- Friday merkt die Antwort lokal und fragt bei stabilen Treffern nicht erneut.
- Nutzer kann später nachfragen und Kontext korrigieren.

## Safety- und Privacy-Grenzen

- Local-only.
- Kein externer Kontaktimport.
- Keine automatische Erhebung sensibler Rollen.
- Keine Speicherung von politischen/religiösen/gesundheitlichen/ethnischen Attributen.
- Keine Weitergabe an externe Dienste.
- Keine echten WhatsApp-/E-Mail-Aktionen.
- Nutzerfreigabe bleibt Pflicht.
- Keine neue Datenbankschema-Änderung.

## Vorgeschlagener Testplan für spätere Implementierung

- Unbekannter Kontakt erzeugt lokalen Fragebedarf.
- Kontaktart kann lokal gespeichert werden.
- Spitzname kann lokal gespeichert werden.
- Bekanntes Kontaktprofil verhindert erneute Rückfrage im selben Kontext.
- Ungültige Kontaktart wird stabil abgefangen.
- Keine externen Aktionen.
- Lokale Speicherung nur mit Zustimmung.

## Empfohlene spätere Implementierungsreihenfolge

1. Reines Planungs-/Preview-Modell ohne DB-Migration.
2. In-Memory- oder Repository-Test für Kontakt-Kontext.
3. Danach lokale SQLite-Nutzung in kleinem Scope.
4. Danach Kontakt-Kontext in Nachrichten-Review integrieren.
5. Externe Kontakte bleiben bis zu separater Freigabe ausgeschlossen.

## Empfohlene Sicherheitsflags

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Empfehlung für Build Step 13F

13F – Obsidian Brain Preview Planning (noch ohne Write-Operation):

- lokale Vorschau-Struktur für Wissenskontext planen,
- nur Planungs- und Sicherheitsabgrenzungen,
- kein Vault-Write in diesem Schritt.
