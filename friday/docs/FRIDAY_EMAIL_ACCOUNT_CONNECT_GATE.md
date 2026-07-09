# Friday E-Mail Account Connect Gate

## Ziel

Dieses Gate beschreibt die vorbereitete E-Mail-Konto-Anbindung fuer Friday.
Der Stand baut Konto-Store, Verbindungstests, read-only Inbox-Preview und Send-Guards, aktiviert aber keinen echten Versand.

## Umgesetzt

| Bereich | Status | Hinweis |
|---|---|---|
| Lokaler Konto-Store | umgesetzt | genau ein Konto unter `local_data/accounts/email_account.json` |
| Passwortschutz | umgesetzt | Windows DPAPI, sonst Warn-Fallback ohne stille Sicherheit |
| Konto speichern | gated | nur mit Token `KONTO SPEICHERN` |
| Konto loeschen | gated | nur mit Token `KONTO LOESCHEN` |
| SMTP-Test | umgesetzt | Login-Test, kein Versand |
| IMAP-Test | umgesetzt | Login-Test, keine Aenderung am Postfach |
| Inbox-Preview | umgesetzt | read-only, begrenzte lokale Anzeige, keine Persistenz von E-Mail-Inhalten |
| API-Endpunkte | umgesetzt | Status, Connect, Test, Delete, Activation-Gate, Inbox, guarded task-forward send |
| CLI-Kontenmenue | umgesetzt | Status, Verbindung, Test, Loeschen, Aktivierungs-Gate |
| Mobile Kontenbereich | umgesetzt | Status, Verbindungstest und Konto-Verbindung in der Datenschutz-Ansicht |
| E-Mail Send-Guard | vorbereitet | blockiert solange `ENABLE_REAL_EMAIL=False` |
| Sendelog | vorbereitet | SQLite-Tabelle `email_send_log` fuer spaetere echte Sendungen |

## Nicht aktiviert

- `ENABLE_REAL_EMAIL` bleibt `False`.
- Es wird in diesem Stand keine echte E-Mail durch Friday gesendet.
- Es wird kein OAuth-Flow gebaut.
- Es wird kein WhatsApp-Provider gebaut.
- Es wird keine private oder inoffizielle WhatsApp-Automatisierung verwendet.
- Es werden keine Zugangsdaten in Tests, Doku, Logs oder Git gespeichert.

## Guard-Regeln fuer spaeteren echten E-Mail-Versand

Ein spaeterer echter Versand darf nur erlaubt werden, wenn alle Bedingungen erfuellt sind:

1. `ENABLE_REAL_EMAIL=True`.
2. Ein lokales E-Mail-Konto ist verbunden.
3. SMTP- und IMAP-Test waren erfolgreich.
4. Der Empfaenger ist als lokaler Kontakt mit E-Mail-Adresse gespeichert.
5. Die Tagesgrenze von 20 E-Mails ist nicht erreicht.
6. Der Nutzer gibt exakt den Token `EMAIL SENDEN` ein.
7. Der Versand wird lokal in `email_send_log` protokolliert.

## WhatsApp-Grenze

WhatsApp bleibt bewusst ein Deep-Link-/App-Oeffnungsflow.
Friday darf einen Text vorbereiten und WhatsApp oeffnen, aber Friday automatisiert keinen WhatsApp-Versand und nutzt keine inoffiziellen WhatsApp-Schnittstellen.

## Rollback

Falls ein spaeteres Gate echten E-Mail-Versand aktiviert, bleibt der sichere Rollback:

```python
ENABLE_REAL_EMAIL = False
```

Zusaetzlich kann das lokale Konto mit `KONTO LOESCHEN` entfernt werden.

## Safety-Bewertung

- Keine echten E-Mails in diesem Stand.
- Keine echten WhatsApp-Nachrichten.
- Keine SMS.
- Keine Kalenderaktionen.
- Keine Cloud-Provider.
- Keine neuen Abhaengigkeiten.
- SMTP/IMAP sind scanner-allowlisted nur in den isolierten E-Mail-Modulen.
- Tests nutzen Mocks und keine echten Konten.

## Validierung

Empfohlene Checks nach Aenderungen:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts\friday_safety_smoke.py
git diff --check
```

## Naechster sinnvoller Schritt

Ein spaeterer Schritt kann das echte Aktivierungs-Gate separat testen und freigeben.
Bis dahin bleibt Friday bei E-Mail read-only/gated und sendet nichts real.
