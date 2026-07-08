# Local Contact Context Persistence Plan 14Q

## Ziel

Planung, wie Kontakt-Kontext später lokal gespeichert werden darf – ohne in dieser Phase Produktlogik oder externen Side-Effekt.

14Q ist ein reines Planungs-Dokument ohne neue Funktionalität.

## Gültiger Scope (14Q)

- Keine produktive Kontaktfunktion in der CLI.
- Keine automatische Persistenz ohne Nutzer-Intent.
- Keine externen API-/Netzwerkaufrufe.
- Keine DB-Änderung in Nutzungsroutinen.
- Keine neue Modell-/Provider-Nutzung.

## Geplante Persistenzfelder

| Feld | Typ | Zweck |
|---|---|---|
| `contact_id` | TEXT | Eindeutiger lokaler Identifier |
| `display_name` | TEXT | Nutzer-lesbarer Name |
| `normalized_name` | TEXT | Vergleichbarer Schlüssel (Lowercase, normalisiert) |
| `contact_type` | TEXT | Kontaktklasse |
| `nickname` | TEXT | Optionale Zusatzbeschreibung |
| `relationship_context` | TEXT | Kontext der Beziehung |
| `source_context` | TEXT | Ursprung (z. B. `nachrichten_review`) |
| `created_at` | TEXT | Erstellung |
| `updated_at` | TEXT | Letzte Änderung |
| `user_approved_persistence` | INTEGER (0/1) | Persistenz nur bei expliziter Zustimmung |
| `sensitivity_checked` | INTEGER (0/1) | Sensitivität-Status vor Speicherung |

## Geplante Sorgfalt (Verbotene/gesperrte Felder)

- Religiöse, politische oder gesundheitliche Merkmale nicht automatisch speichern.
- Keine Intimdaten oder sensible Finanzdaten ohne expliziten Freigabepfad.
- Kein automatischer „Backfill“ aus externen Quellen.

## Consent und Sicherheitsregel

- Keine Speicherung ohne explizite Nutzerfreigabe (`user_approved_persistence = 1`).
- Speicherfluss bleibt lokal und transparent.

## Nächster technischer Schritt

- 14R — Contact Repository / DB Preview
  - Lokale Vorschau-Repository-Komponente (noch ohne Produktionsintegration).
  - Ziel: Datensatz-Lebenszyklus testen (create/get/list/update/delete).

## Nicht-Ziele in 14Q

- Kein vollständiger Kontakt-Edit-Flow im Produkt.
- Kein CLI-Menü für Kontaktverwaltung.
- Keine Delete-/Approval-Hardening-UI-Funktionen.
- Kein Obsidian- oder Datei-Export.

## Safety

- Keine externen Aktionen.
- Keine Kontaktimporte.
- Keine Echtzeit-/Provider-Flows.
- Safety-Flags bleiben unverändert.
