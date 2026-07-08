# Privacy Data Cleanup Policy Readiness Gate

## Ziel

Dieses Gate prueft den Privacy Data Cleanup Policy Plan.

Der gepruefte Stand bleibt bewusst nicht-ausfuehrend:

- Policy vorhanden,
- keine Implementierung,
- keine CLI-Anbindung,
- keine Loeschfunktion,
- keine Exportfunktion,
- keine Importfunktion,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/docs/PRIVACY_DATA_CLEANUP_POLICY_PLAN.md` | Cleanup-Policy vorhanden |
| `friday/docs/SAFETY_MATRIX.md` | Policy als geplante Safety-Grenze vermerkt |
| `friday/docs/cli_documentation_index_12l.md` | Policy im Doku-Index eingetragen |

## Readiness-Ergebnis

- Es gibt keine globale Aktion wie "alles loeschen".
- Cleanup bleibt auf spaetere gezielte lokale Aktionen begrenzt.
- Jede echte Bereinigung braucht ein eigenes Implementierungs-Gate.
- Jede echte Bereinigung braucht ein eigenes Readiness-Gate.
- Harte Tokens sind nur geplant und noch nicht freigegeben.
- `JA` und `ja` sind fuer neue Privacy-Cleanup-Aktionen nicht erlaubt.
- Die bestehende Task-Delete-Policy bleibt unveraendert.

## Weiterhin blockierte Bereiche

| Bereich | Status |
|---|---|
| Aktive SQLite-Datenbank loeschen oder ersetzen | blockiert |
| `.env`, Secrets oder API-Keys anzeigen/exportieren/loeschen | blockiert |
| Obsidian Vault scannen oder bereinigen | blockiert |
| Provider oder Netzwerkzugriff | blockiert |
| In-Place-Restore | blockiert |
| Pending Review-Vorschlaege automatisch loeschen | blockiert |
| Alle Kontakte auf einmal loeschen | blockiert |
| Massenloeschung von Aufgaben ueber Privacy Dashboard | blockiert |

## Nicht freigegeben

- Keine Privacy-Cleanup-CLI.
- Kein Cleanup-Repository.
- Kein Dateisystem-Cleanup.
- Kein SQLite-Cleanup.
- Kein Exportordner-Cleanup.
- Kein Backupordner-Cleanup.
- Kein Restore-Kopien-Cleanup.
- Kein Review-Cleanup.
- Kein Kontakt-Cleanup ueber Privacy Management.
- Kein Obsidian-Cleanup.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine neuen Loeschpfade.
- Keine neuen Exportpfade.
- Keine neuen Importpfade.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Teststatus

Empfohlene Pruefkommandos:

```powershell
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Schritt:

`Privacy Cleanup Preview Model Plan`

Ziel: Nur planen, wie eine spaetere Cleanup-Vorschau aussehen soll. Noch keine Loeschfunktion, kein Dateizugriff und keine CLI-Aktion implementieren.
