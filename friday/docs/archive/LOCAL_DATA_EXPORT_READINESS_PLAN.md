# Local Data Export Readiness Plan

## Ziel

Dieses Dokument plant einen spaeteren lokalen Datenexport fuer Friday.

Der Schritt ist nur Planung:

- kein Export-Code,
- kein ZIP,
- kein neuer Schreibpfad,
- keine CLI-Aenderung,
- keine Datenbankabfrage,
- keine externen Aktionen.

## Geplanter Exportumfang

| Bereich | Geplanter Export | Hinweise |
|---|---|---|
| Aufgaben | Markdown oder JSON | nur lokale Aufgabenfelder |
| Kontakt-Kontexte | JSON/Markdown-Zusammenfassung | nur mit Consent, keine sensiblen Freitexte |
| Review-Vorschlaege | JSON/Markdown-Zusammenfassung | Status und IDs, keine vollstaendigen privaten Nachrichten |
| Backup-/Restore-Status | Markdown-Zusammenfassung | nur Pfade/Status, keine Inhalte |
| Privacy Dashboard Summary | Markdown-Zusammenfassung | read-only Statusuebersicht |
| Safety Matrix | Markdown-Kopie | vorhandene Doku, keine Secrets |

## Nicht zu exportieren

- `.env`
- API Keys
- Tokens
- Cache-Dateien
- Obsidian Vault
- vollstaendige private Nachrichten
- sensible Kontakt-Freitexte
- private Gesundheitsdaten
- private Finanzdetails
- politische/religioese/ethnische/personenbezogene sensible Kategorien
- aktive Datenbank als Rohkopie ohne eigenes Backup-Gate

## Geplanter Zielpfad

Ein spaeterer Export soll nur lokal erfolgen:

```text
local_data/exports/
```

Ein moeglicher spaeterer Zielordner:

```text
local_data/exports/friday_data_export_YYYYMMDD_HHMMSS/
```

## Geplanter harter Token

Falls spaeter ein echter Export-Write gebaut wird, soll ein eigener harter Token verwendet werden:

```text
DATEN EXPORTIEREN
```

Nicht erlaubt als Export-Freigabe:

- `ja`
- `JA`
- `ok`
- `speichern`
- `BACKUP ERSTELLEN`
- `RESTORE AUSFUEHREN`

## Safety-Regeln fuer spaetere Implementierung

1. Export bleibt lokal.
2. Export schreibt nur unter `local_data/exports/`.
3. Export braucht einen eigenen Guard.
4. Export braucht einen eigenen harten Token.
5. Export darf keine Secrets enthalten.
6. Export darf keine sensiblen Kontakt-Freitexte enthalten.
7. Export darf keine externen Provider aufrufen.
8. Export darf keine Netzwerkaktion ausfuehren.
9. Export darf keine Daten loeschen.
10. Export darf keine aktiven Projektdateien ueberschreiben.

## Geplante Modell-/Guard-Schritte

Empfohlene spaetere Reihenfolge:

1. Local Data Export Plan Gate
2. Local Data Export Preview Model
3. Local Data Export Guard
4. Local Data Export Writer
5. Local Data Export CLI Approval
6. Local Data Export Readiness Gate
7. User Guide Integration

## Testplanung

Spaetere Tests sollten pruefen:

- Preview ist side-effect-free.
- Guard blockiert falsche Tokens.
- Guard blockiert Pfade ausserhalb `local_data/exports/`.
- Guard blockiert Secrets und `.env`.
- Writer schreibt nur erlaubte Dateien.
- Writer ueberschreibt nicht ungefragt.
- CLI bricht bei Enter ab.
- CLI akzeptiert nur `DATEN EXPORTIEREN`.
- Full Regression bleibt gruen.
- Safety Smoke bleibt PASS.

## Safety-Bewertung

- Dieser Schritt ist Doku-only.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine Schreibaktion.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Local Data Export Preview Model.
