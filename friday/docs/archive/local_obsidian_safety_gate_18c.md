# Local Obsidian Safety Gate 18C

## Ziel

Build Step 18C dokumentiert und testet die lokalen Sicherheitsgrenzen fuer spaetere Obsidian-Ausgaben.

## Abgesicherte Regeln

| Regel | Umsetzung |
|---|---|
| Vault-Pfad | Zielpfad wird aus einem expliziten Vault-Pfad gebaut |
| Erlaubter Unterordner | Standard ist `Friday` |
| Pfad-Schutz | Zielpfad muss innerhalb des erlaubten Unterordners liegen |
| Dedupe | bestehende Dateien werden nicht ueberschrieben |
| Preview first | Preview-Funktionen schreiben nie |
| Approval required | echter Write braucht ein hartes Token |

## Bewusst nicht umgesetzt

- Keine CLI-Anbindung.
- Keine automatische Vault-Erkennung.
- Kein echter Obsidian-Sync.
- Kein externer Provider.
- Kein Ueberschreiben vorhandener Notizen.

## Safety-Bewertung

- `OBSIDIAN_WRITE_ENABLED = False` bleibt der sichere Default.
- `OBSIDIAN_VAULT_PATH = ""` bedeutet: kein produktiver Vault ist aktiv.
- `OBSIDIAN_ALLOWED_SUBDIR = "Friday"` begrenzt spaetere lokale Writes.
- Es gibt keine Datenbankschema-Aenderung.

## Empfehlung für nächsten Schritt

18D: Write-Dry-Run als lokale Zielpfad-Vorschau ohne Schreiboperation dokumentieren.
