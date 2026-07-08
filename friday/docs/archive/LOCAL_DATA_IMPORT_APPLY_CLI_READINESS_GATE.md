# Local Data Import Apply CLI Readiness Gate

## Ziel

Dieses Gate prueft den getrennten CLI-Schreibpfad fuer lokalen Import-Apply nach der Implementierung.

Der Fokus liegt auf Readiness, Safety und klarer Abgrenzung:

- `7. Import-Apply-Vorschau anzeigen` bleibt read-only.
- `8. Import nach Freigabe anwenden` ist der einzige Apply-Schreibpfad.
- Der Schreibpfad bleibt lokal und wird nur nach Guard, Backup-Schutz, Safety Smoke und hartem Token freigegeben.

## Gepruefte Bereiche

| Bereich | Ergebnis |
|---|---|
| Menuefuehrung | Backup-/Restore-Menue trennt Vorschau und Apply-Schreibpfad. |
| Read-only Vorschau | Punkt `7` fragt keinen Token ab und schreibt nichts. |
| Backup-Schutz | Punkt `8` blockiert ohne lokalen Backup-Eintrag vor Tokenabfrage. |
| Safety Smoke | Punkt `8` prueft Safety Smoke vor der Tokenfreigabe. |
| Approval Token | Nur exakt `IMPORT ANWENDEN` gibt den Writer frei. |
| Falsche Tokens | `JA`, `ja` oder andere Eingaben schreiben nichts. |
| Writer | Schreibt nur erlaubte lokale Scopes in die lokale SQLite-DB. |
| Rollback / Blockierung | Writer-Blockiergruende bleiben sichtbar und externe Aktionen bleiben aus. |

## Abgesicherte Tests

- `friday/tests/test_menu.py`
- `friday/tests/test_interface_main_menu_e2e.py`
- `friday/tests/test_local_data_import_apply_write_guard.py`
- `friday/tests/test_local_data_import_apply_writer.py`

Relevante Testabdeckung:

- Menuepunkt `8. Import nach Freigabe anwenden` vorhanden.
- Rueckkehr ins Hauptmenue ueber `9`.
- Apply-Schreibpfad blockiert ohne Backup-Schutz vor Tokenabfrage.
- Apply-Schreibpfad blockiert falschen Token.
- Apply-Schreibpfad wendet mit exakt `IMPORT ANWENDEN` einen gueltigen lokalen Export auf tmp_path SQLite an.
- Bestehende read-only Apply-Vorschau bleibt unveraendert.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Cloud-Integration.
- Keine Datenbankschema-Aenderung.
- Kein Restore in aktive Projektdateien.
- Lokaler Import-Apply schreibt nur erlaubte Zusammenfassungsbereiche:
  - `tasks`
  - `contact_contexts`
  - `review_suggestions`
- Safety-Flags bleiben unveraendert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unveraendert:
  - `"ja"` loescht nicht,
  - `"JA"` loescht,
  - `" JA "` bleibt per `strip()` zugelassen.

## Readiness Ergebnis

Der lokale Import-Apply-CLI-Schreibpfad ist als kontrollierter lokaler Pfad bereit.

Freigegeben:

- lokaler Apply aus einem gueltigen Exportordner,
- nur nach Backup-Schutz,
- nur nach Safety-Smoke PASS,
- nur mit exakt `IMPORT ANWENDEN`,
- nur in lokale SQLite-Daten.

Nicht freigegeben:

- externer Import,
- Restore in aktive Projektdateien,
- Provider-/Cloud-Aufrufe,
- automatische Apply-Ausfuehrung ohne Token,
- Schema-Migration im Apply-Pfad,
- Import sensibler oder privater Rohdaten.

## Empfehlung fuer naechsten Build Step

Local Data Import Apply User Guide Integration: README/User-Doku final synchronisieren, damit Nutzer die Trennung zwischen read-only Vorschau und echtem guarded Apply eindeutig verstehen.
