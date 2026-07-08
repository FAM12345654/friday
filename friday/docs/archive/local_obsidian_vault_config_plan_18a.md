# Obsidian Vault Config Plan 18A

## Ziel

18A plant die spätere lokale Obsidian-Anbindung.

Dieser Schritt schreibt keine Dateien und ergänzt keine Obsidian-Produktlogik.

## Geplante Konfiguration

```python
OBSIDIAN_VAULT_PATH = ""
OBSIDIAN_WRITE_ENABLED = False
OBSIDIAN_ALLOWED_SUBDIR = "Friday/"
```

## Sicherheitsregeln

- Kein Write ohne eigenes späteres Gate.
- Kein beliebiger Dateipfad.
- Nur erlaubtes Unterverzeichnis im Vault.
- Preview vor jedem Write.
- Approval vor jedem Write.
- Keine sensiblen Kontaktinformationen ohne Freigabe.

## Nicht-Ziele

- kein Obsidian-Write,
- kein Dateiexport in ein Vault,
- keine Vault-Erkennung,
- keine externe Integration,
- keine Datenbankschema-Änderung.

## Empfehlung für Build Step 18B

Nächster sinnvoller Schritt: `18B — Obsidian Note Preview Renderer`.

Dabei sollen Markdown-Notizen nur als String-Preview erzeugt werden.
