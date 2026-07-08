# CLI UX Review 12C

## Geprüfte Bereiche
- Task Edit
- Task Search/Filter
- Task Archive/Done/Statuswechsel
- Task Loop Rücksprünge
- Delete Regression

## Abgesicherte Bereiche
- Edit-Flow ist stabil für:
  - ungültige Aufgaben-ID,
  - unbekannte Aufgaben-ID,
  - vollständige Leer-Eingaben bei Update-Feldern,
  - gültige Bearbeitung und ungültige Priorität.
- Such-/Filter-Flow ist stabil für:
  - Treffer-Suche per Text,
  - leere Suche mit offenen Filtern,
  - Suche ohne Treffer.
- Archive-/Done-Flow ist stabil für:
  - ungültige/fehlende ID,
  - gültige Aktion,
  - wiederholte Statusänderung auf den gleichen Wert.
- Rücksprung-Logik ist stabil für:
  - ungültige Hauptmenü-Eingaben in der Run-Loop,
  - ungültige Eingaben im Aufgaben-Untermenü und Rücksprung mit „8“.
- Delete-Regression ist stabil:
  - `ja` bricht ab,
  - `JA` löscht,
  - ` JA ` löscht durch `strip()` ebenfalls,
  - ` JA ` Verhalten ist explizit im Testbestand dokumentiert.

## Offene UX-Ränder

| Bereich | Ist-Zustand | Risiko | Empfehlung |
|---|---|---|---|
| Task-Loop-Navigation | Rücksprung im Aufgaben-Menü erfolgt derzeit nur über „8“; es gibt keinen weiteren globalen Abbruch-Taste-Shortcut. | Nutzer ist auf einen festen Rücksprung-Pfad angewiesen. | Optional: später einen Kurzbegriff wie `0`/`z` als Rücksprung ergänzen. |
| CLI-Fehlermeldungen | Ungültige Eingaben liefern konsistente, aber teils unterschiedliche Wortlaute je nach Bereich. | Eingaben sind korrekt abgefangen, die Konsistenz ist aber für neue Nutzer uneinheitlich. | Textbausteine vereinheitlichen (z. B. „Ungültige Eingabe.“). |

## Safety-Bewertung
- Keine externen Aktionen aktiviert.
- Lokale Tests mit temporärer SQLite-Datei (`tmp_path`) für die bearbeiteten Task-Flüsse.
- Sicherheitsflags bleiben auf lokaler Test-/Demo-Konfiguration:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Keine Datenbankschema-Änderung durchgeführt.

## Empfehlung für Build Step 12D
- Nächster sinnvoller Schritt: die Meldungs- und Menünachrichten übergreifend vereinheitlichen (ohne Logikänderung), danach gezielte E2E-Tests für diese Konsistenz ergänzen.
