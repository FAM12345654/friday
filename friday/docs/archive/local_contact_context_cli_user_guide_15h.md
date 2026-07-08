# Contact CLI User Guide 15H

## Wofuer ist die Kontakt-Kontext-CLI da?

Die Kontakt-Kontext-CLI zeigt lokale Kontakt-Kontexte in Friday.

Sie hilft dir, gespeicherte lokale Kontakte zu sehen, zu suchen, als Draft zu bearbeiten oder gezielt zu vergessen.

## Menue oeffnen

1. Starte Friday.
2. Waehle im Hauptmenue `9. Kontakt-Kontext anzeigen`.

Das Kontakt-Kontext-Menue zeigt:

| Auswahl | Funktion |
|---|---|
| `1` | Kontakte anzeigen |
| `2` | Kontakt suchen |
| `3` | Kontakt bearbeiten (Vorschau) |
| `4` | Kontakt vergessen |
| `5` | Zurueck zum Hauptmenue |

## Kontakte anzeigen

`1. Kontakte anzeigen` zeigt lokal gespeicherte Kontakt-Kontexte.

Friday zeigt sichtbare lokale Felder wie:

- Kontakt-ID,
- Anzeigename,
- Kontaktart,
- Spitzname,
- Kontext.

Wenn keine Kontakte vorhanden sind, zeigt Friday:

`Keine lokalen Kontakt-Kontexte vorhanden.`

## Kontakt suchen

`2. Kontakt suchen` sucht nur lokal in sichtbaren Kontaktfeldern.

Wenn keine Treffer vorhanden sind, zeigt Friday:

`Keine passenden Kontakt-Kontexte gefunden.`

Leere Eingabe kehrt ohne Aenderung zum Kontakt-Kontext-Menue zurueck.

## Kontakt bearbeiten

`3. Kontakt bearbeiten (Vorschau)` erstellt zuerst nur einen lokalen Draft.

Friday speichert erst, wenn exakt dieses Token eingegeben wird:

`SPEICHERN`

Diese Eingaben speichern nicht:

- Enter,
- `ja`,
- `JA`,
- andere Texte.

## Kontakt vergessen

`4. Kontakt vergessen` nutzt den Forget-Person-Flow.

Friday zeigt zuerst eine lokale Preview aus SQLite:

- betroffene Zieltabelle,
- Kandidatenanzahl,
- passende Kontakt-ID und Anzeigename,
- Hinweis, dass kein Obsidian-Write und keine externe Aktion ausgefuehrt wird.

Vor dem Write prueft Friday:

- lokaler Backup-Nachweis unter `local_data/backups/`,
- Safety Smoke PASS,
- side-effect-free Guard,
- lokale SQLite-Transaktion mit Rollback.

Der exakte Token lautet:

`PERSON VERGESSEN`

Diese Eingaben loeschen nicht:

- Enter,
- `ja`,
- `JA`,
- `ok`,
- `KONTAKT LÖSCHEN`,
- andere Texte.

Der Flow schreibt keine Obsidian-Dateien und loescht nur passende Zeilen aus `contact_contexts`.

## Safety

Die Kontakt-Kontext-CLI bleibt lokal.

- Keine echten Nachrichten.
- Keine echten Kalenderaktionen.
- Keine echten E-Mails.
- Kein echtes WhatsApp.
- Keine echte SMS.
- Kein Kontaktimport.
- Keine Netzwerkaktionen.
- Keine Cloud-Provider.
- Keine Datenbankschema-Aenderung.

Unveraenderte Safety-Flags:

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Empfehlung fuer Build Step 15I

Naechster sinnvoller Schritt: `15I — Contact CLI Finalization Gate`.
