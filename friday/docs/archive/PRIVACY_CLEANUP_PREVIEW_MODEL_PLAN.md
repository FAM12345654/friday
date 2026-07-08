# Privacy Cleanup Preview Model Plan

## Ziel

Dieser Plan beschreibt ein spaeteres read-only Preview-Modell fuer Privacy Cleanup.

Das Modell soll nur anzeigen, was eine spaetere Bereinigung theoretisch betreffen wuerde.

Der Schritt bleibt Plan-only:

- keine Produktlogik,
- kein Modellcode,
- keine Tests,
- keine CLI-Aenderung,
- kein Dateizugriff,
- kein SQLite-Zugriff,
- keine Loeschfunktion,
- keine externen Aktionen.

## Geplantes Modell

Spaeteres Modul:

```text
friday/app/privacy_cleanup_preview.py
```

Spaetere Tests:

```text
friday/tests/test_privacy_cleanup_preview.py
```

## Geplante Datenstrukturen

```python
@dataclass(frozen=True)
class PrivacyCleanupPreviewItem:
    area_name: str
    cleanup_type: str
    target_path: str
    count_label: str
    allowed_root: str
    allowed: bool
    blocked_reasons: tuple[str, ...]
    requires_token: str


@dataclass(frozen=True)
class PrivacyCleanupPreview:
    items: tuple[PrivacyCleanupPreviewItem, ...]
    blocked_actions: tuple[str, ...]
    writes_performed: bool
    deletes_performed: bool
    external_lookup_used: bool
```

## Geplante Vorschau-Bereiche

| Bereich | Preview erlaubt? | Spaeterer Cleanup-Typ | Erlaubter Root |
|---|---|---|---|
| Exporte | Ja | alte Exportordner | `local_data/exports/` |
| Backups | Ja | alte Backupordner | `local_data/backups/` |
| Restore-Kopien | Ja | alte Restore-Kopien | `local_data/restores/` |
| Review-Vorschlaege | Ja, nur Status-Vorschau | alte abgelehnte/converted Vorschlaege | SQLite, aber kein Write im Preview |
| Kontakt-Kontexte | Nur Einzelkontakt-Vorschau | gezieltes Vergessen ueber bestehendes Gate | SQLite, aber kein Write im Preview |
| Aufgaben | Nein im Privacy Cleanup | nicht vorgesehen | bestehendes Task-Menue |
| aktive SQLite-DB | Nein | blockiert | nicht erlaubt |
| `.env` / Secrets | Nein | blockiert | nicht erlaubt |
| Obsidian Vault | Nein | blockiert | nicht erlaubt |

## Sicherheitsregeln fuer spaeteres Preview-Modell

Das Preview-Modell darf:

- erlaubte Bereiche beschreiben,
- geplante Counts als Eingabe akzeptieren,
- Zielpfade als Strings anzeigen,
- blockierte Gruende ausgeben,
- harte Tokens als erforderlich markieren.

Das Preview-Modell darf nicht:

- Ordner erstellen,
- Dateien lesen,
- Dateien loeschen,
- Dateien schreiben,
- SQLite oeffnen,
- Datenbankzeilen loeschen,
- externe Provider aufrufen,
- Netzwerkzugriff ausfuehren,
- freie Pfade akzeptieren,
- aktive SQLite-Dateien als Ziel erlauben.

## Geplante Blockiergruende

| Grund | Bedeutung |
|---|---|
| `outside_allowed_root` | Ziel liegt ausserhalb des erlaubten lokalen Roots |
| `active_database_blocked` | aktive SQLite-Datenbank ist betroffen |
| `secrets_blocked` | `.env`, Secrets oder API-Keys waeren betroffen |
| `obsidian_vault_blocked` | Obsidian Vault waere betroffen |
| `pending_review_blocked` | Pending Review-Vorschlaege sollen nicht geloescht werden |
| `global_delete_blocked` | globale Loeschaktion ist nicht erlaubt |
| `missing_future_gate` | ein separates Implementierungs-Gate fehlt |

## Geplanter Testumfang

Spaetere Tests sollten pruefen:

- Preview ist read-only.
- `writes_performed` bleibt `False`.
- `deletes_performed` bleibt `False`.
- `external_lookup_used` bleibt `False`.
- erlaubte Bereiche werden korrekt gelistet.
- blockierte Bereiche bleiben blockiert.
- aktive SQLite-Datenbank wird nie als Cleanup-Ziel erlaubt.
- `.env` und Secrets werden nie erlaubt.
- Obsidian Vault wird nie erlaubt.
- globale Loeschaktion wird blockiert.
- falsche oder freie Pfade werden blockiert.

## Nicht-Ziele

- Keine Implementierung in diesem Schritt.
- Keine echte Vorschau-Berechnung.
- Kein Dateisystem-Scan.
- Kein SQLite-Scan.
- Keine CLI-Anbindung.
- Kein Approval-Token-Check.
- Keine Loeschaktion.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine neuen Loeschpfade.
- Keine neuen Exportpfade.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Schritt:

`Privacy Cleanup Preview Model`

Ziel: Ein isoliertes read-only Modell bauen, das geplante Cleanup-Bereiche nur aus explizit uebergebenen Daten beschreibt. Noch kein Dateizugriff, kein SQLite-Zugriff, keine CLI-Anbindung und keine Loeschfunktion.
