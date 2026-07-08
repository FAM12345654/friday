# Privacy Dashboard CLI Read-Only Plan

## Ziel

Dieses Dokument plant die spaetere read-only CLI-Anbindung des Privacy Dashboards.

Der Schritt ist nur Planung:

- keine Menueaenderung,
- keine Interface-Aenderung,
- keine Datenbankabfrage,
- keine Schreibaktion,
- keine externen Aktionen.

## Geplanter Menuepunkt

Das Privacy Dashboard soll spaeter als eigener Hauptmenuepunkt sichtbar werden.

Vorschlag:

```text
Hauptmenue
...
12. Privacy Dashboard
```

Falls die Nummerierung bis dahin anders ist, soll der Menuepunkt an das bestehende Hauptmenue angepasst werden.

## Geplanter CLI-Flow

```text
Privacy Dashboard

Friday arbeitet lokal.
Externe Aktionen sind deaktiviert.
Schreibaktionen brauchen harte Tokens.

1. Lokale Datenbereiche anzeigen
2. Safety-Flags anzeigen
3. Externe Aktionen anzeigen
4. Gated Actions anzeigen
5. Safety Scanner anzeigen
6. Zurueck zum Hauptmenue
```

Alle Optionen sind read-only.

## Geplante Anzeigen

| Option | Anzeige | Schreibaktion |
|---|---|---|
| Lokale Datenbereiche | Aufgaben, Kontakte, Review, Backups, Restore-Kopien | keine |
| Safety-Flags | erwartete lokale Flags | keine |
| Externe Aktionen | E-Mail, WhatsApp, SMS, Kalender, Wetter, Musik deaktiviert | keine |
| Gated Actions | harte Tokens als Statushinweis | keine |
| Safety Scanner | Scanner-Namen und lokaler Safety-Smoke-Hinweis | keine |
| Zurueck | Rueckkehr zum Hauptmenue | keine |

## Datenquelle

Die CLI soll zunaechst nur das bestehende read-only Modell verwenden:

- `build_privacy_dashboard_summary(...)`

Die erste CLI-Version soll keine Repository-Zaehler direkt laden.

Optionale Zaehler koennen spaeter in einem eigenen Gate angebunden werden, wenn klar ist:

- welche Repositories gelesen werden,
- welche Details verborgen bleiben,
- wie sensible Daten nicht versehentlich ausgegeben werden.

## UX-Regeln

- Kurze deutsche Texte.
- Keine sensiblen Details anzeigen.
- Keine vollstaendigen Kontakt-Freitexte anzeigen.
- Keine vollstaendigen Nachrichten oder Review-Texte anzeigen.
- Kein Write-Hinweis darf wie eine Aufforderung zur Aktion wirken.
- Harte Tokens duerfen als Sicherheitsstatus sichtbar sein.
- Ungueltige Auswahl nutzt die Standardmeldung:
  `Ungueltige Auswahl. Bitte erneut versuchen.`

## Nicht-Ziele

- Kein Loeschen.
- Kein Export.
- Kein Bearbeiten.
- Kein Speichern.
- Kein Backup Write aus dem Privacy Dashboard.
- Kein Restore Write aus dem Privacy Dashboard.
- Kein Obsidian Write.
- Keine Datenbankmigration.
- Keine externen Provider.
- Keine Netzwerkaktion.

## Testplanung

Spaetere Tests sollten pruefen:

- Hauptmenue oeffnet Privacy Dashboard.
- Privacy Dashboard zeigt lokalen Status.
- Safety-Flags werden angezeigt.
- Externe Aktionen werden als deaktiviert angezeigt.
- Gated Actions werden nur als Status dargestellt.
- Ungueltige Auswahl bleibt stabil.
- Rueckkehr zum Hauptmenue funktioniert.
- Exit nach Privacy Dashboard funktioniert.
- Keine Schreibaktion wird ausgefuehrt.

## Safety-Bewertung

- Dieser Schritt ist Doku-only.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine externen Aktionen.
- Keine Datenbankschema-Aenderung.
- Keine CLI-Anbindung in diesem Schritt.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Privacy Dashboard CLI Read-Only Implementation.
