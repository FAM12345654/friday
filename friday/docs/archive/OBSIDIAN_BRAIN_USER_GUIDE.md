# Obsidian Brain User Guide

## Ziel

Friday kann lokale Aufgaben, Kontakte und Projekte als Obsidian-Notiz-Preview anzeigen.
Die Funktion bleibt lokal und schreibt standardmaessig keine Dateien.

## Was angezeigt wird

| Bereich | Preview-Ziel |
|---|---|
| Aufgaben | `Aufgaben/<titel>.md` |
| Kontakte | `Kontakte/<name>.md` |
| Projekte | `Projekte/<titel>.md` |

Jede Preview enthaelt Markdown mit Frontmatter:

- `source: friday`
- `external_lookup_used: false`
- `type: contact`, `task` oder `project`

## Sichere Defaults

- `OBSIDIAN_VAULT_PATH = ""`
- `OBSIDIAN_WRITE_ENABLED = False`
- `OBSIDIAN_ALLOWED_SUBDIR = "Friday"`
- Preview-Funktionen setzen `preview_only=True`.
- Preview-Funktionen setzen `persisted=False`.
- Preview-Funktionen setzen `external_lookup_used=False`.

## Wann ein Write moeglich waere

Ein Obsidian Write ist nur lokal und nur mit allen Gates moeglich:

1. Ein Vault-Pfad wird explizit gesetzt.
2. `OBSIDIAN_WRITE_ENABLED` wird explizit auf `True` gesetzt.
3. Der Zielpfad bleibt im erlaubten Unterordner.
4. Die Zieldatei existiert noch nicht.
5. Der Sensitive Guard erlaubt den gerenderten Markdown-Inhalt.
6. Die Bestaetigung lautet exakt `OBSIDIAN SCHREIBEN`.

## Blockierte Aktionen

- Automatisches Erkennen eines Vaults.
- Automatisches Schreiben in Obsidian.
- Schreiben ohne harten Token.
- Schreiben sensibler Freitexte.
- Ueberschreiben bestehender Notizen.
- Cloud-Sync oder Provider-Aufrufe.

## Nutzerhinweis

Wenn Friday eine Obsidian-Preview zeigt, ist das nur eine Vorschau.
Ohne explizite lokale Konfiguration und den harten Token wird keine Obsidian-Datei geschrieben.
