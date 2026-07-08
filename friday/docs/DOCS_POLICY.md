# Friday Docs Policy

## Ziel

Diese Policy haelt die aktive Friday-Dokumentation klein und wartbar.

## Aktive Dokumente

Aktiv im Ordner `friday/docs/` bleiben nur zentrale Dokumente:

- Nutzer- und Setup-Doku,
- Architektur- und Datenmodell-Doku,
- Safety- und Test-Matrix,
- Build History,
- aktuelle MVP-/Produktabschluss-Dokumente.

## Archiv

Historische Plan-, Gate-, Readiness- und Acceptance-Dokumente liegen unter `friday/docs/archive/`.

Das Archiv ist Nur-Lese-Historie:

- nicht loeschen,
- nicht als Quelle fuer neue Produktlogik verwenden,
- nur bei Bedarf zur Nachverfolgung alter Entscheidungen lesen.

## Kuenftige Build Steps

Neue Steps sollen bevorzugt bestehende zentrale Dokumente aktualisieren:

- `README_USER.md`,
- `BUILD_HISTORY.md`,
- `TEST_MATRIX.md`,
- `SAFETY_MATRIX.md`,
- `DATA_MODELS.md`,
- `FRIDAY_ARCHITECTURE.md`,
- `FRIDAY_LOCAL_MVP_POST_RELEASE_ROADMAP.md`.

Neue Gate-Dateien sollen nur entstehen, wenn sie dauerhaft als aktuelles Abschlussdokument gebraucht werden.

## Safety

Die Doku-Konsolidierung aendert keine Produktlogik, keine Datenbank und keine externen Aktionen.
