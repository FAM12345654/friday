# Local Contact Context Preview Model 14A

## Ziel

Erster technischer Schritt für lokalen Kontaktkontext als reine Preview-Struktur ohne Persistenz.

## Umfang

- Reine In-Memory-/Preview-Datenstruktur.
- Keine DB-Migration.
- Keine neue Tabelle.
- Keine Kontaktimporte.
- Keine externen APIs.
- Keine WhatsApp-/E-Mail-/SMS-Integration.
- Keine Obsidian-Schreiboperation.
- Keine direkte CLI- oder Flow-Integration in diesem Schritt.

## Implementierte Funktionen

- `ContactContextPreview`
- `normalize_contact_name`
- `normalize_contact_type`
- `build_contact_context_preview`

## Unterstützte Kontaktarten

- `kunde`
- `kollege`
- `mitarbeiter`
- `familie`
- `freund`
- `dienstleister`
- `sonstiges`
- `unbekannt`

## Verhalten

- Name wird stabil normalisiert:
  - trimmen
  - auf `lower`
  - mehrfachen Leerraum auf einzelne Leerzeichen
- Kontaktart wird validiert:
  - bekannte Typen werden übernommen,
  - `None`/leer → `unbekannt`,
  - unbekannte Werte → `sonstiges`.
- Vorschauobjekt setzt feste lokale Flags:
  - `preview_only = True`
  - `persisted = False`
  - `external_lookup_used = False`

## Safety-/Privacy-Bewertung

- Es werden bewusst keine sensiblen Datenfelder automatisch erfasst.
- Kein externer Kontakt-Lookup.
- Keine Datenbankspeicherung.
- Kein Datei-/DB-Schreibpfad.
- Keine externen Dienste.
- Keine Datenbankschema-Änderung.

## Tests

- `friday/tests/test_contact_context_preview.py`
- Geprüfte Punkte:
  - Preview-Objekt wird lokal erstellt.
  - Name- und Typ-Normalisierung.
  - Unbekannte/fehlende Typen stabil gemappt.
  - lokale Kontextfelder bleiben gesetzt.
  - keine Persistenz oder externe Datenabhängigkeit.
- `python -m pytest friday/tests`: vorhanden und grün nach Integration.

## Nächster Schritt

- Build Step **14B — Contact Context Prompt Planning**
- Zweck: gezielt planen, wann und wie Friday später per minimale Rückfrage Kontaktkontext speichern darf.
- Keine Persistenz und kein Messaging-/Task-/Review-Flow in 14B.
