# Privacy Cleanup User Guide Integration

## Ziel

Dieses Dokument beschreibt die Nutzer-Doku-Ergaenzung fuer die read-only Privacy Cleanup Preview.

Friday zeigt im Privacy Dashboard eine Cleanup-Vorschau an, fuehrt aber keine echte Bereinigung aus.

## Nutzerpfad

Die read-only Cleanup Preview ist ueber diesen lokalen CLI-Pfad erreichbar:

```text
Hauptmenue -> 12. Privacy Dashboard -> 7. Privacy Cleanup Preview anzeigen
```

Rueckkehr:

```text
8. Zurueck zum Hauptmenue
```

## In README_USER.md ergaenzte Hinweise

- Die Cleanup Preview ist nur eine Vorschau.
- Es wird nichts geloescht.
- Es wird nichts exportiert.
- Es wird nichts importiert.
- Es wird nichts wiederhergestellt.
- Es wird kein Token abgefragt.
- Externe Aktionen bleiben deaktiviert.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Cleanup-Ausfuehrung aktiviert.
- Keine Datei- oder Datenbankloeschung.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
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
  - `" JA "` bleibt durch `strip()` erlaubt.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup Final Acceptance Gate**.

Ziel:

- Privacy Cleanup Policy, Preview Model, CLI Preview, Runtime Summary und User Guide final zusammenfassen,
- keine Produktlogik aendern,
- keine Tests erweitern,
- Full Regression, Compilecheck, Safety Smoke und Diff-Check ausfuehren.
