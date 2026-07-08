# Local Obsidian Write Dry Run 18D

## Ziel

Build Step 18D ergänzt einen Dry-Run fuer Obsidian-Notizen.

Der Dry-Run zeigt, wohin Friday schreiben wuerde, schreibt aber selbst keine Datei.

## Verhalten

| Situation | Ergebnis |
|---|---|
| Write deaktiviert | `would_write=False`, Grund: `Obsidian Write ist deaktiviert.` |
| Zieldatei existiert | `would_write=False`, Grund: `Zieldatei existiert bereits.` |
| Write aktiviert und Datei fehlt | `would_write=True`, Grund: `Würde lokal schreiben.` |

## Safety-Bewertung

- Dry-Run schreibt keine Datei.
- Dry-Run nutzt keine externen Dienste.
- Dry-Run nutzt keinen Provider.
- Pfad bleibt im erlaubten Obsidian-Unterordner.
- Bestehende Dateien blockieren den Write-Pfad.

## Tests

- `test_obsidian_dry_run_does_not_write_when_disabled`
- `test_obsidian_target_path_stays_inside_allowed_subdir`

## Empfehlung für nächsten Schritt

18E: Lokalen Write nur mit hartem Approval-Token erlauben.
