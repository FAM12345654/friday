# Forget Person Finalization Gate

## Ziel

Forget Person ist der lokale, releasefaehige Flow zum gezielten Vergessen eines Kontakt-Kontexts in Friday.

## Freigegebener Scope

- Kontakt-Kontext-Menue: `4. Kontakt vergessen`
- Lokale SQLite-Tabelle: `contact_contexts`
- Auswahl per `contact_id` oder normalisiertem Anzeigenamen
- Read-only Preview vor jedem Write
- Write nur nach lokalem Backup, Safety Smoke PASS und hartem Token

## Nicht freigegeben

- Obsidian-Write
- Obsidian-Vault-Aenderungen
- Cloud-Provider
- Netzwerkaktionen
- echte E-Mails
- echtes WhatsApp
- echte SMS
- echte Kalenderaktionen
- echte Wetter-/Musikaktionen
- echte AI-Modellaufrufe
- Datenbankschema-Aenderungen
- Loeschungen in Aufgaben, Nachrichten, Kalenderdaten oder Review-History

## Token

Der exakte Forget-Person-Token lautet:

```text
PERSON VERGESSEN
```

Nicht ausreichend:

- leerer Token
- `ja`
- `JA`
- `ok`
- `löschen`
- `SPEICHERN`
- `KONTAKT LÖSCHEN`
- ` PERSON VERGESSEN `

`KONTAKT LÖSCHEN` bleibt nur der bestehende Token fuer den separaten DB-Cleanup-Kontaktpfad.

## Technischer Ablauf

1. `build_forget_person_preview(...)`
2. lokaler Backup-Nachweis unter `local_data/backups/`
3. `run_safety_smoke()`
4. `check_forget_person_write_allowed(...)`
5. `apply_forget_person_write(...)`

## Safety Contract

- Preview nutzt SQLite `mode=ro`.
- Guard ist side-effect-free.
- Writer nutzt eine lokale SQLite-Transaktion.
- Writer loescht nur guard-gebundene `contact_id`-Targets.
- Candidate-Count-Mismatch fuehrt zu Rollback.
- Sensitive Freitexte werden nicht als Write-Ergebnis zurueckgegeben.
- `schema_changed=False`
- `external_action_used=False`
- `obsidian_write_performed=False`

## Tests

Fokus-Tests:

```text
python -m pytest friday/tests/test_forget_person_preview.py friday/tests/test_forget_person_write_guard.py friday/tests/test_forget_person_writer.py friday/tests/test_interface_main_menu_e2e.py friday/tests/test_privacy_dashboard.py friday/tests/test_approval_token_scanner.py friday/tests/test_scanner_smoke_script.py
```

Pflichtvalidierung:

```text
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Gate Status

Freigegeben fuer lokalen Release-Kandidaten, solange Safety-Flags unveraendert bleiben und die Pflichtvalidierung PASS bleibt.
