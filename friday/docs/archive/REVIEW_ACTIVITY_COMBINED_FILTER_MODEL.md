# Review Activity Combined Filter Model

## Ziel

Dieses Dokument beschreibt das isolierte read-only Modell fuer den lokalen Review Activity Combined Filter in Friday.

Der technische Step setzt den Plan aus `REVIEW_ACTIVITY_COMBINED_FILTER_PLAN.md` minimal um:

- Status Filter,
- Type Filter,
- optionale Suche.

## Implementierung

Neu ist:

`friday/app/review_activity_combined_filter.py`

Das Modell stellt bereit:

- `ReviewActivityCombinedFilterResult`
- `build_review_activity_combined_filter(...)`

Die Funktion nimmt lokale `ReviewActivityDetailItem`-Daten entgegen und kombiniert vorhandene Review-Activity-Modelle:

1. Status Filter,
2. Type Filter,
3. optionale Search.

Leere Suchbegriffe werden als "keine Suche" behandelt. Nicht-leere, aber zu kurze Suchbegriffe bleiben ungueltig und liefern eine sichere Fehlermeldung.

## Read-only Verhalten

Das Modell:

- schreibt keine Dateien,
- schreibt nicht in SQLite,
- liest keine Datenbank direkt,
- fuehrt keine externen Aktionen aus,
- nutzt keine Netzwerkaktion,
- nutzt keinen Cloud-Provider,
- nutzt keinen echten AI-Modellaufruf.

Die Ergebnisflags bleiben:

- `preview_only = True`
- `persisted = False`
- `external_action_used = False`

## Testabdeckung

Neu ist:

`friday/tests/test_review_activity_combined_filter.py`

Abgedeckt sind:

- Status plus Typ,
- offener Status plus Typ,
- Status plus Suche,
- Typ plus Suche,
- Status plus Typ plus Suche,
- stabile Reihenfolge,
- leere Suche als kein Suchfilter,
- ungueltiger Status,
- ungueltiger Typ,
- zu kurzer nicht-leerer Suchbegriff,
- Search-Limit,
- read-only Safety-Flags.

## Safety-Grenzen

Die folgenden Safety-Flags bleiben unveraendert:

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Nicht Teil dieses Steps

Nicht umgesetzt wurden:

- CLI-Anbindung,
- neue Menuepunkte,
- DB-Schema-Aenderungen,
- gespeicherte Filter-Presets,
- automatische Review-Aktionen,
- Batch-Aktionen,
- externe Aktionen,
- echte AI-Modellaufrufe.

## Ergebnis

Der Review Activity Combined Filter ist als isoliertes read-only Modell umgesetzt und getestet.

Naechster sinnvoller Build-Step:

`REVIEW_ACTIVITY_COMBINED_FILTER_MODEL_READINESS_GATE.md`
