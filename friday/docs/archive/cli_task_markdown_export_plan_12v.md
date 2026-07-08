# CLI Task Markdown Export Plan 12V

## Ziel

Planung für einen sicheren, lokalen Markdown-Export lokaler Aufgaben.

## Warum zunächst Planung

Ein Export ist ein Dateisystem-Schreibvorgang.

In diesem Schritt bleibt 12V bewusst bei Planung und Safety-Definition:

- Welche Exportdaten sinnvoll sind,
- welcher Pfad zuerst unterstützt wird,
- welche Sicherheitsregeln gelten,
- welche Tests später ergänzt werden.

Es wird **kein produktiver Export implementiert**.

## Bewertete Varianten

| Variante | Nutzen | Risiko | Testbarkeit | Empfehlung |
|---|---|---|---|---|
| A. Agent-/Service-Methode ohne CLI-Menü | Sauberer Anfang, reine Logik klar testbar | Niedrig | Hoch | Empfohlen als nächster Schritt vor CLI-Bedienung |
| B. Aufgabenmenüpunkt „Export" | Direkt nutzbar für Nutzer | Mittel | Mittel | Später, nach stabiler Service-Methode |
| C. Fester lokaler Exportpfad | Nutzerfreundlich, wenig Eingabefehler | Mittel | Gut | Geeignet als Schritt 2 |
| D. Nutzerdefinierter Pfad | Hohe Flexibilität | Hoch (Schreibsicherheit) | Mittel | Nicht als Erstimplementierung |
| E. Obsidian-/Cloud-Pfad | Später nützlich | Hoch (externe Zielordner/Abhängigkeiten) | Mittel | Nicht für 12V/12W, erst mit separater Policy |

## Empfohlene Minimal-Policy

- Nur lokaler Export.
- Kein Schreibzugriff auf beliebige Nutzerpfade im ersten Schritt.
- Kein Obsidian-/Cloud-Schreiben.
- Kein automatisches Überschreiben ohne explizite Freigabe/Policy.
- Keine externen Aktionen.
- Export nur aus lokalem Task-Zustand.
- `Delete-Policy` bleibt unverändert.

## Vorgeschlagenes Markdown-Format

Beispiel-Layout:

```text
# Friday Aufgabenexport

## Offene Aufgaben
- [ ] Titel
  - ID: 12
  - Kategorie: arbeit
  - Fällig: 2026-07-05
  - Priorität: normal
  - Notizen: ...

## Erledigte Aufgaben

## Archivierte Aufgaben
```

## Testplan für spätere Implementierung

- Export über tmp_path-Dateisystem schreiben.
- Export enthält offene Aufgaben.
- Export enthält erledigte Aufgaben.
- Export enthält archivierte Aufgaben.
- Leere Taskliste bleibt stabil.
- Kein externer Pfad in der ersten Variante.
- Kein Obsidian-/Cloud-Schreiben.
- Keine Datenbankschema-Änderung.

## Sicherheits- und Architekturbewertung

- In 12V bleibt Produktlogik unverändert.
- Keine Dateischreiboperation implementiert.
- Keine externen Aktionen.
- Keine neuen Provider/Netzwerk-/Cloud-Aufrufe.
- Safety-Flags bleiben unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unverändert:
  - `"ja"` löscht nicht,
  - `"JA"` löscht,
  - `" JA "` bleibt durch `strip()` zulässig.

## Empfehlung für Build Step 12W

Als sicherer nächster Schritt: erst eine reine Markdown-Formatierungsfunktion oder Export-Service implementieren (ohne CLI-Menüpunkt), getestet mit `tmp_path`.
