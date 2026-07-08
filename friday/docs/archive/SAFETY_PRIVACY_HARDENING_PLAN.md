# Friday Safety / Privacy Hardening Plan

## Ziel

Plan fuer die naechste Safety- und Privacy-Haertung nach dem Post-399 Consolidation Gate.

## Ausgangslage

Friday besitzt jetzt lokale Datenfluesse fuer:

- Contact Context
- Contact Repository
- Review Contact Integration
- Task Contact Snapshot
- Obsidian Brain Preview / Write Gate
- Local Model Foundation

Full Regression: `399 passed`.

## Zentrale Risiken

| Risiko | Bereich | Status |
|---|---|---|
| sensible Kontaktinfos in Freitext | Contact Context | Guard fehlt |
| doppelte Kontakte | Contact Context | Dedupe/Merge fehlt |
| ungewollter Obsidian-Write | Obsidian | gated, weiter haerten |
| sensible Daten in Obsidian | Obsidian | Sensitivity Check fehlt |
| externe Imports/Provider | Safety Layer | Scanner fehlt |
| lokale Modellantworten ungeprueft | Local Model | Validator vorhanden, produktive Nutzung fehlt |
| unklare Datenansicht fuer Nutzer | Privacy | Dashboard fehlt |
| fehlendes Backup | Storage | Backup/Restore fehlt |

## Geplante Hardening-Bausteine

### 1. Sensitive Contact Context Guard

Ziel:

- Freitextfelder pruefen.
- sensible Kategorien blockieren.
- harmlose Arbeitskontexte erlauben.

Zu blockierende Kategorien:

- Politik
- Religion
- Ethnie
- Gesundheit
- sexuelle Orientierung
- Gewerkschaftszugehoerigkeit
- strafrechtliche Details
- private Finanzdetails
- intime/private Profile

### 2. Forbidden Import Scanner

Ziel:

- versehentliche Cloud-/Provider-Imports erkennen.

Zu pruefen:

- `openai`
- `requests`
- `httpx`
- `twilio`
- WhatsApp-/SMS-Provider
- Google-/Microsoft-Provider in nicht freigegebenen Modulen

### 3. No Network Scanner

Ziel:

- Netzwerkzugriffe in lokalen Modulen verhindern.

### 4. No Input/Print Scanner

Ziel:

- isolierte Modell-/Parser-/Renderer-/Preview-Module bleiben side-effect-frei.

### 5. Safety Flag Regression Check

Ziel:

- zentrale Safety-Flags bleiben unveraendert.

### 6. Approval Token Matrix Check

Ziel:

- harte Tokens zentral pruefen:
  - `SPEICHERN`
  - `KONTAKT LÖSCHEN`
  - `OBSIDIAN SCHREIBEN`

### 7. Obsidian Write Hardening

Ziel:

- Dedupe
- Contradiction Check
- Sensitivity Check
- Rollback Plan
- Write Audit

### 8. Privacy Dashboard Plan

Ziel:

Nutzer kann spaeter sehen:

- welche Kontakte gespeichert sind,
- welche Task-Snapshots existieren,
- welche Obsidian-Writes moeglich sind,
- welche Provider deaktiviert sind,
- welche Daten geloescht werden koennen.

## Nicht-Ziele in diesem Plan

- Keine Implementierung.
- Keine Produktlogik.
- Keine DB-Migration.
- Keine externen Aktionen.
- Keine neuen Provider.
- Keine echten Modellaufrufe.
- Kein automatischer Obsidian-Write.

## Empfohlene Build-Reihenfolge

1. Sensitive Contact Context Guard
2. Forbidden Import / No Network Scanner
3. No Input/Print Scanner
4. Safety Flag Regression Scanner
5. Approval Token Matrix Check
6. Obsidian Write Hardening
7. Privacy Dashboard Plan
8. Backup/Restore Plan

## Validierung

- `python -m pytest friday/tests`
- `python -m compileall friday`
- `git diff --check`

## Entscheidung

Safety/Privacy Hardening ist der sinnvollste naechste Arbeitsbereich, bevor neue riskantere Produktintegrationen gebaut werden.
