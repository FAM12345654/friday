# Backup / Restore CLI Integration Plan

## Ziel

Plan fuer eine spaetere lokale CLI-Integration von Backup Preview, Backup Write und Restore Dry-Run.

Dieser Schritt baut noch keinen Menuepunkt und keine Produktlogik. Er definiert nur, wie der Backup-/Restore-Bereich spaeter sicher in Friday sichtbar werden soll.

## Ausgangslage

Bereits umgesetzt:

- Backup Preview Model
- Backup Write Guard / Model
- Backup Write Implementation
- Backup Write Readiness Gate
- Restore Dry-Run Plan
- Restore Dry-Run Model
- Restore Dry-Run Readiness Gate

Noch nicht umgesetzt:

- Backup-/Restore-Menue in der CLI
- Backup Preview im Menue
- Backup Write im Menue
- Restore Dry-Run im Menue
- echter Restore

## Vorgeschlagener CLI-Bereich

Spaeterer Hauptmenuepunkt:

```text
Backup / Restore
```

Vorgeschlagenes Untermenue:

```text
Backup / Restore
1. Backup-Vorschau anzeigen
2. Backup lokal erstellen
3. Restore-Dry-Run pruefen
4. Zurueck zum Hauptmenue
```

## Menue-Verhalten

| Option | Verhalten | Safety |
|---|---|---|
| `1` Backup-Vorschau anzeigen | nutzt Backup Preview, schreibt nichts | erlaubt |
| `2` Backup lokal erstellen | nutzt Backup Preview + Backup Write Guard + Scanner Smoke + Token | gated |
| `3` Restore-Dry-Run pruefen | prueft Backup-Struktur, schreibt nichts zurueck | erlaubt als Dry-Run |
| `4` Zurueck | kehrt ins Hauptmenue zurueck | erlaubt |

## Backup-Vorschau

Die Backup-Vorschau darf:

- geplanten Backup-Zielordner anzeigen.
- enthaltene Sektionen anzeigen.
- ausgeschlossene Sektionen anzeigen.
- fehlende Sektionen anzeigen.
- erklaeren, dass noch nichts geschrieben wurde.

Die Backup-Vorschau darf nicht:

- Backup-Ordner erstellen.
- Dateien kopieren.
- ZIP-Dateien erzeugen.
- externe Speicherorte verwenden.
- Secrets oder Obsidian Vault aufnehmen.

## Backup lokal erstellen

Backup Write darf spaeter nur ausgefuehrt werden, wenn:

1. Backup Preview vorhanden ist.
2. Backup Write Guard erlaubt.
3. Scanner Smoke Script `PASS` ist.
4. Zielpfad unter `local_data/backups/` liegt.
5. Nutzer exakt `BACKUP ERSTELLEN` eingibt.

Nicht erlaubt:

- `JA`
- `ja`
- `ok`
- `yes`
- leere Eingabe
- automatische Backups beim Start
- Backups ausserhalb `local_data/backups/`
- Obsidian-Vault-Backup
- Secrets oder `.env`

## Restore-Dry-Run

Restore-Dry-Run darf spaeter:

- Backup-Ordner unter `local_data/backups/` pruefen.
- `manifest.json` lesen.
- fehlende Sektionen melden.
- riskante Inhalte blockieren.
- Warnungen anzeigen.

Restore-Dry-Run darf nicht:

- Dateien zurueckschreiben.
- aktive SQLite-Datenbank ersetzen.
- Exporte zurueckkopieren.
- Obsidian Vault schreiben.
- ZIP-Dateien entpacken.
- echte Restore-Aktionen starten.

## Echter Restore

Ein echter Restore bleibt nicht freigegeben.

Vor einem echten Restore braucht Friday spaeter mindestens:

- Restore Write Plan.
- Restore Write Guard.
- harte Token-Policy.
- Backup-Konsistenzpruefung.
- Konfliktstrategie fuer bestehende Daten.
- Restore-Dry-Run Readiness Gate.
- eigene Tests.
- eigenes Safety-Gate.

Moeglicher spaeterer harter Token:

```text
RESTORE AUSFUEHREN
```

Dieser Token ist in diesem Schritt nicht freigegeben.

## Vorgeschlagene Tests fuer spaetere Umsetzung

Wenn die CLI-Integration gebaut wird, sollten Tests abdecken:

- Hauptmenue oeffnet Backup-/Restore-Menue.
- Backup-/Restore-Menue zeigt vier Optionen.
- Option `1` zeigt Backup Preview und schreibt nichts.
- Option `2` blockiert ohne `BACKUP ERSTELLEN`.
- Option `2` erstellt lokales Backup nur mit `BACKUP ERSTELLEN`.
- Option `3` fuehrt Restore-Dry-Run aus und schreibt nichts.
- ungueltige Eingabe zeigt Standardmeldung.
- Rueckkehr zum Hauptmenue bleibt stabil.
- Exit nach Backup-/Restore-Menue bleibt stabil.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine CLI-Integration gebaut.
- Keine Tests geaendert.
- Kein Backup geschrieben.
- Kein Restore ausgefuehrt.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine Netzwerkaktionen.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Backup / Restore CLI Read-Only Preview.
