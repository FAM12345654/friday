# Local Obsidian Note Preview Renderer 18B

## Ziel

Build Step 18B ergänzt lokale Markdown-Preview-Helfer für spätere Obsidian-Notizen.

Der Schritt erzeugt nur Vorschau-Inhalte. Es wird nichts automatisch in ein Vault geschrieben.

## Umgesetzte Bereiche

| Bereich | Verhalten |
|---|---|
| Kontakt-Notiz | Markdown-Preview für lokalen Kontakt-Kontext |
| Aufgaben-Notiz | Markdown-Preview für lokale Aufgaben |
| Projekt-Notiz | Markdown-Preview für einfache Projektinformationen |
| Dateiname | konservativer Markdown-Dateiname über `safe_obsidian_filename()` |
| Frontmatter | einfache lokale Metadaten mit `external_lookup_used: false` |

## Safety-Regeln

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Kein Obsidian-Write in der Preview-Funktion.
- Kontakt-Beziehungskontext wird nur aufgenommen, wenn Persistenz freigegeben und Sensitivitätsprüfung markiert ist.
- Vorschauen bleiben `preview_only=True` und `persisted=False`.

## Tests

- `friday/tests/test_obsidian_note_preview.py`

## Empfehlung für nächsten Schritt

18C: Obsidian Safety Gate fuer erlaubte Zielpfade, Dedupe und Approval-Regeln dokumentieren und absichern.
