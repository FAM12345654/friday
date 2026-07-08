# Review Batch Selection CLI Preview Implementation

## Ziel

Dieses Dokument beschreibt die read-only CLI-Anbindung der Review-Batch-Auswahlpreview.

Der Step bindet Parser und Preview-Renderer in den lokalen Review-Bereich ein, ohne Batch-Aktionen auszufuehren.

## Geaenderte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/interface.py` | Review-Uebersicht um Batch-Preview-Option und read-only Preview-Methode erweitert |
| `friday/tests/test_interface_combined_review.py` | E2E-nahe Tests fuer Batch-Preview und invalid ID |
| `friday/docs/REVIEW_BATCH_SELECTION_CLI_PREVIEW_IMPLEMENTATION.md` | Dokumentation dieses Implementierungsschritts |

## Nutzerpfad

```text
Hauptmenue -> 6. Vorschlaege pruefen / freigeben -> 5. Batch-Auswahl als Vorschau anzeigen
```

Danach kann der Nutzer eine Auswahl eingeben:

```text
1,2,3
all
none
z
```

Friday zeigt nur eine Vorschau.

## Implementiertes Verhalten

- Review-Uebersicht zeigt `5. Batch-Auswahl als Vorschau anzeigen`.
- Die Batch-Preview nutzt nur gerade sichtbare pending Nachrichten- und Aufgaben-Vorschlaege.
- Intern werden virtuelle sichtbare IDs erzeugt, damit Nachrichten- und Aufgaben-Vorschlags-IDs nicht kollidieren.
- Parser und Preview-Renderer werden verwendet.
- Ungueltige IDs zeigen die Standardmeldung.
- Jede Preview enthaelt:

```text
Es wurde noch nichts freigegeben, abgelehnt oder gesendet.
```

## Read-only-Grenzen

- Kein Vorschlag wird freigegeben.
- Kein Vorschlag wird abgelehnt.
- Kein Aufgaben-Vorschlag wird konvertiert.
- Keine lokale Aufgabe wird erstellt.
- Keine Nachricht wird gesendet.
- Kein Kalendertermin wird erstellt.
- Kein DB-Status wird geaendert.
- Keine externe Aktion wird ausgeloest.

## Tests

Ergaenzte Tests pruefen:

- Batch-Preview zeigt ausgewaehlte sichtbare Nachrichten- und Aufgaben-Vorschlaege.
- Invalid ID bleibt read-only.
- Pending Vorschlaege bleiben offen.
- Es wird keine lokale Aufgabe erzeugt.
- Safety-Hinweis wird angezeigt.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine Batch-Apply-Funktion.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection CLI Preview Readiness Gate**.

Ziel:

- CLI-Preview-Anbindung final pruefen,
- Fokus-Tests und Full Regression bestaetigen,
- dokumentieren, dass weiterhin keine Batch-Aktion freigegeben ist.
