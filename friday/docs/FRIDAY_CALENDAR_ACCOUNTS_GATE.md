# Friday Calendar Accounts Gate

## Ziel

Dieses Gate dokumentiert das neue Fundament fuer echte Kalenderkonten:

- generische Account-Policy-Engine,
- Google-Kalender-Provider hinter Interface,
- Kalender-Aktivierungs-Gate,
- Event-Write-Guard,
- Setup-Screen-Anbindung fuer Policies.

## Bewusste Architekturentscheidung

Kalenderkonten werden nicht pro Sonderfall hartkodiert. Jedes Konto bekommt eine Policy:

| Feld | Bedeutung |
|---|---|
| `provider` | z. B. `google_calendar`, spaeter `outlook_graph` |
| `label` | Nutzername fuer das Konto |
| `role` | `main` fuer Schreibziel oder `source` fuer nur Quelle |
| `access` | `read` oder `read_write` |
| `include_filters` | harte Allowlist, z. B. `{"title_contains":["PH"]}` |
| `exclude_filters` | harte Ausschlussliste |
| `notes` | Kontext fuer lokale KI |
| `enabled` | Policy aktiv/inaktiv |

Der PH-Outlook-Fall aus der Planung wird dadurch spaeter nur ein Policy-Eintrag:

```json
{
  "provider": "outlook_graph",
  "label": "Arbeit Outlook PH",
  "role": "source",
  "access": "read",
  "include_filters": {"title_contains": ["PH"]},
  "notes": "PH = Dienst = belegt. Alles andere aus diesem Konto ignorieren."
}
```

## Umgesetzte Module

| Modul | Zweck |
|---|---|
| `account_policy_store.py` | lokale Policy-Persistenz mit Token `POLICY SPEICHERN` |
| `account_policy_engine.py` | deterministische Filter und KI-Kontext |
| `calendar_provider_base.py` | gemeinsames Kalender-Provider-Interface |
| `calendar_provider_google.py` | dedizierter Google-Provider |
| `calendar_google_account_store.py` | verschluesselte lokale Google-Token-Ablage |
| `calendar_activation_gate.py` | Gate fuer `KALENDER AKTIVIEREN` |
| `calendar_event_write_guard.py` | Gate fuer `TERMIN SPEICHERN` |

## Google-Kalender-Status

Der Google-Provider ist technisch vorbereitet, aber ohne Nutzer-OAuth noch nicht verbunden.

Aktuell gilt:

- kein Google-Token im Git,
- kein Client-Secret im Git,
- echte Verbindung lokal moeglich, aber verschluesselt unter `local_data`,
- echte Kalender-Schreibaktionen nur nach hartem Event-Token,
- Provider-Tests nutzen Fakes/Mocks.

## Safety-Bewertung

- `ENABLE_REAL_CALENDAR = True` ist eine bewusste, dokumentierte Ausnahme.
- E-Mail, WhatsApp, SMS, Wetter und Musik bleiben weiterhin erzwungen aus.
- `KALENDER AKTIVIEREN` ist die einmalige Nutzerentscheidung fuer Kalender-Schreiben.
- `TERMIN SPEICHERN` ist fuer echte Event-Writes erforderlich.
- Ohne Haupt-Policy, Verbindungstest und exakten Event-Token blockiert der Write-Guard.
- Google-Imports sind nur in `calendar_provider_google.py` erlaubt.
- Keine Cloud-KI.
- Keine echten Nachrichten.
- Keine Datenbankspalten wurden geloescht oder geaendert; Tabellen wurden additiv ergaenzt.
- Rollback: `ENABLE_REAL_CALENDAR=False` setzen und Scanner-Baseline wieder auf Kalender `False` zurueckstellen.

## Neue Tabellen

| Tabelle | Zweck |
|---|---|
| `account_policies` | lokale Account-Regeln, Filter und Notizen |
| `calendar_entries` | lokale Referenz auf spaetere Provider-Event-IDs |
| `calendar_cache` | spaeterer Fallback-Cache fuer gelesene Events |

## Neue API-Bereiche

| Endpoint | Zweck |
|---|---|
| `GET /api/accounts/policies` | Policies und KI-Kontext anzeigen |
| `POST /api/accounts/policies` | Policy mit `POLICY SPEICHERN` anlegen |
| `PATCH /api/accounts/policies/{id}` | Policy mit `POLICY SPEICHERN` aendern |
| `DELETE /api/accounts/policies/{id}` | Policy mit `POLICY SPEICHERN` entfernen |
| `GET /api/accounts/calendar/status` | Kalenderkonto-/Policy-Status |
| `POST /api/accounts/calendar/google/oauth-url` | OAuth-URL fuer PC-Login vorbereiten |
| `POST /api/accounts/calendar/activation-gate` | Aktivierungsgate pruefen |
| `POST /api/calendar/events/write-guard` | Event-Write-Gate pruefen und bei erlaubtem Guard genau einen Google-Termin erstellen |

## Nicht umgesetzt / bewusst deferred

- Microsoft/Outlook Graph Provider,
- Outlook ICS Provider,
- automatischer Kalender-Sync,
- Batch-Write,
- Schreiben ohne Nutzer-Token,
- OAuth-Zugangsdaten im Repo.

## Validierung

Fokus-Tests:

```powershell
python -m pytest friday/tests/test_account_policy_engine.py friday/tests/test_account_policy_store.py friday/tests/test_calendar_provider_google.py friday/tests/test_calendar_activation_and_write_gates.py friday/tests/test_no_network_scanner.py friday/tests/test_forbidden_import_scanner.py friday/tests/test_friday_api_setup_calendar_contact.py
```

Voll-Checks:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Naechster sinnvoller Schritt

Kalender-Schreiben im Mobile-/Desktop-Review-Flow sichtbar anschliessen: Vorschlag pruefen, editieren, dann pro Termin mit `TERMIN SPEICHERN` schreiben.
