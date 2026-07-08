# Obsidian Brain Preview Plan 13F

## Ziel

Planung für eine spätere lokale Obsidian-Brain-Anbindung als reine Vorschaufunktion ohne Schreiboperation.

## Warum Obsidian Brain Preview

Friday soll Wissen lokal konsolidieren können, ohne sofort Dateien zu schreiben:

- Personenkontext
- Projektwissen
- Aufgabenstatus
- Entscheidungen
- offene Fragen
- tägliche oder sitzungsbezogene Zusammenfassungen
- Unsicherheiten/Widersprüche

## Nicht-Ziele in 13F

- Keine Implementierung.
- Kein Obsidian-Write.
- Keine Vault-Erkennung.
- Keine Dateioperation im Vault.
- Keine automatische Memory-Ablage.
- Keine sensiblen Notizen ohne explizite Freigabe.
- Keine externen APIs.
- Keine OpenAI-/Cloud-Abhängigkeit.

## Vorgeschlagene Vault-Struktur (Preview)

- Obsidian/
  - Friday/
    - 00_Inbox/
    - 01_People/
    - 02_Projects/
    - 03_Tasks/
    - 04_Decisions/
    - 05_Daily/
    - 06_Reviews/
    - 07_Uncertainty/
    - 08_Archive/

## Geplante Note-Typen

| Note-Typ | Zweck |
|---|---|
| Person Note | lokaler Kontext zu bekannten Personen |
| Project Note | Projektwissen und Status |
| Task Summary | Aufgabenstand / abgeschlossene Aufgaben |
| Decision Note | dokumentierte Entscheidung |
| Daily Brief | lokale Tageszusammenfassung |
| Review Note | Review-/Suggestion-Ergebnisse |
| Uncertainty Note | offene Fragen, Widersprüche, Unsicherheiten |
| Source Note | Verweis auf lokale Herkunft / Quelle |

## Vorschlagsprinzip (Preview-first)

- Friday erzeugt zunächst nur Vorschau-Daten.
- Kein Dateischreiben in diesem Schritt.
- Nutzer sieht mindestens:
  - Zielordner-Vorschlag,
  - Dateinamen-Vorschlag,
  - Frontmatter-Vorschau,
  - Body-Vorschau,
  - Safety-Hinweise.
- Write/Export bleibt für einen späteren Schritt mit expliziter Freigabe reserviert.

## Frontmatter-Entwurf

| Feld | Zweck |
|---|---|
| type | Note-Typ |
| title | Titel der Notiz |
| created_at | Erstellung (lokal) |
| updated_at | letzte Änderung (lokal) |
| source_context | Entstehungsherkunft (z. B. nachricht, aufgabe) |
| confidence | Vertrauensgrad der Information |
| sensitivity | Sensitivitätsklasse |
| review_required | Prüfung durch Nutzer erforderlich |
| related_contacts | referenzierte Kontakt-IDs |
| related_projects | referenzierte Projekt-IDs |
| tags | lokale Tags |

## Safety- und Privacy-Klassen

| Klasse | Bedeutung |
|---|---|
| low | allgemeine Aufgaben-/Projektinfo |
| medium | Personen- oder Beziehungs-Kontext |
| high | sensible oder potenziell private Notizen |
| blocked | nicht automatisch speicherbar |

## Vorgeschlagene Teststrategie für spätere Implementierung

- Preview enthält Zielpfad-Vorschlag.
- Preview enthält Frontmatter-Vorschau.
- Preview enthält Body-Vorschau.
- In 13F wird keine Datei geschrieben.
- Sensible Inhalte werden als `high` oder `blocked` markiert.
- Write ohne explizite Freigabe wird blockiert.
- Vault-Mock via `tmp_path` erst in späterem Schritt.

## Empfohlene spätere Implementierungsreihenfolge

1. Preview-Datenstruktur ohne Dateisystem erstellen.
2. Tests für Preview-Payload definieren.
3. Vault-Pfad-Policy planen.
4. Write-Dry-Run planen.
5. Lokaler Write mit expliziter Freigabe als separater Step.

## Empfohlene Safety-Flags

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Empfehlung für Build Step 13G

**Local Model Readiness Planning**

- lokale Modellstrategie planen,
- keine Modellaufrufe in 13G,
- keine externen Provider,
- lokale Mock-/Fallback-Strategie vorbereiten.
