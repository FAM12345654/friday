# Privacy Cleanup Writer Model

## Ziel

Dieses Dokument beschreibt das isolierte Privacy Cleanup Writer Model.

Der Writer ist noch nicht mit der CLI verbunden und darf nur explizit aus Code oder Tests aufgerufen werden. Er nutzt verpflichtend das Privacy Cleanup Write Guard Model.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/privacy_cleanup_writer.py` | Guarded Writer-Prototyp fuer eng begrenzten lokalen Datei-Cleanup |
| `friday/tests/test_privacy_cleanup_writer.py` | Tests fuer Guard-Pflicht, Dry-Run und tmp_path-Datei-Cleanup |

## Umgesetztes Verhalten

- Writer blockiert ohne Guard.
- Writer blockiert, wenn der Guard blockiert.
- Writer blockiert bei Cleanup-Area-Mismatch.
- Writer blockiert bei Target-Path-Mismatch.
- Writer blockiert das neueste Backup.
- Writer blockiert DB-/Kontakt-Cleanup-Bereiche weiterhin.
- Dry-Run loescht nichts.
- Datei-Cleanup funktioniert nur fuer erlaubte lokale Datei-Scopes.
- Tests nutzen ausschliesslich `tmp_path`.

## Unterstuetzte Bereiche im Writer-Modell

| Bereich | Status |
|---|---|
| `exports` | lokaler Datei-Cleanup im erlaubten Scope moeglich |
| `backups` | lokaler Datei-Cleanup moeglich, neuestes Backup bleibt geschuetzt |
| `restore_work` | lokaler Datei-Cleanup im erlaubten Scope moeglich |
| `review_history` | weiterhin blockiert |
| `contact_context` | weiterhin blockiert |

## Safety-Eigenschaften

- Keine CLI-Anbindung.
- Keine automatische Ausfuehrung.
- Keine externen Aktionen.
- Keine SQLite-Loeschung.
- Keine Datenbankschema-Aenderung.
- Keine Kontakt-Loeschung.
- Guard-Ergebnis ist Pflicht.
- `dry_run=True` loescht nichts.
- Tests schreiben und loeschen nur in `tmp_path`.

## Nicht freigegeben

- Kein produktiver Cleanup aus der CLI.
- Kein Review-History-Cleanup.
- Kein Kontakt-Kontext-Cleanup.
- Kein Obsidian-Cleanup.
- Kein Cleanup ausserhalb erlaubter lokaler Scopes.
- Keine externen Provider- oder Netzwerkaktionen.

## Teststatus

- Fokus-Tests: `python -m pytest friday/tests/test_privacy_cleanup_writer.py`
- Full Regression: `python -m pytest friday/tests`
- Compilecheck: `python -m compileall friday`
- Safety Smoke: `python scripts/friday_safety_smoke.py`
- Diff-/Whitespace-Check: `git diff --check`

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup Writer Readiness Gate**.

Ziel:

- Writer-Modell final pruefen,
- Fokus-Tests, Full Regression, Compilecheck, Safety Smoke und Diff-Check dokumentieren,
- keine CLI-Anbindung,
- keine produktive Cleanup-Ausfuehrung.
