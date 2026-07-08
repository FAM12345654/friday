# Local Day Planning User Guide Update

## Ziel

Dieses Dokument haelt fest, dass die Nutzer-Dokumentation fuer die lokale Tagesplanung aktualisiert wurde.

## Aktualisierte Bereiche

| Datei | Aktualisierung |
|---|---|
| `README_USER.md` | Tagesplanung in Funktionsliste ergaenzt |
| `README_USER.md` | Neuer Abschnitt `Lokale Tagesplanung anzeigen` ergaenzt |
| `README_USER.md` | Read-only-Grenzen und Rueckkehr ueber `12` dokumentiert |

## Nutzerpfad

```text
Hauptmenue -> 1. Aufgaben verwalten -> 11. Lokale Tagesplanung anzeigen
```

Rueckkehr:

```text
12. Zurück zum Hauptmenü
```

## Nutzererklaerung

Friday zeigt eine lokale Tagesplan-Vorschau aus offenen Aufgaben.

Die Ansicht:

- sortiert Aufgaben nach Faelligkeit, Prioritaet und Titel,
- blendet erledigte und archivierte Aufgaben aus,
- zeigt Aufgaben ohne Faelligkeitsdatum verstaendlich an,
- ist nur eine Vorschau.

## Read-only-Grenzen

- Keine Aufgabe wird erstellt.
- Keine Aufgabe wird geaendert.
- Keine Aufgabe wird erledigt.
- Keine Aufgabe wird archiviert.
- Keine Aufgabe wird geloescht.
- Keine Tagesliste wird gespeichert.
- Keine externen Dienste werden genutzt.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unveraendert:
  - `"ja"` loescht nicht,
  - `"JA"` loescht,
  - `" JA "` bleibt durch `strip()` erlaubt.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Local Day Planning Final Acceptance Gate**.

Ziel:

- Modell, Renderer, CLI-Anbindung und Nutzer-Doku gemeinsam final abnehmen.
- Keine neue Produktlogik bauen.
