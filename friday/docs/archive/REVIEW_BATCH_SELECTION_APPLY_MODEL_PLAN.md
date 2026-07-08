# Review Batch Selection Apply Model Plan

## Ziel

Dieses Dokument plant ein spaeteres lokales Review-Batch-Apply-Modell.

Der Schritt bleibt bewusst planend:

- keine Produktlogik-Aenderung,
- keine Apply-Implementierung,
- keine CLI-Anbindung,
- keine Batch-Aktion,
- keine Statusaenderung an Vorschlaegen,
- keine Datenbankoperation,
- keine externen Aktionen.

## Ausgangslage

Der Review-Batch-Stack hat aktuell:

- Batch-Auswahlparser,
- read-only Preview-Renderer,
- read-only CLI-Preview im Review-Bereich,
- Apply-Policy,
- side-effect-free Apply Guard,
- Guard Readiness Gate.

Ein spaeteres Apply-Modell darf nur nach erfolgreichem Guard-Ergebnis lokale Aktionen vorbereiten oder ausfuehren.

## Grundsatz

Ein spaeteres Apply-Modell darf nie ohne Guard laufen.

Pflicht:

```text
Guard allowed == True
```

Ohne erlaubendes Guard-Ergebnis muss jede Apply-Funktion blockieren.

## Geplante Apply-Aktionen

| Action Type | Spaeterer Effekt | Risiko | Bedingung |
|---|---|---|---|
| `approve_messages` | Nachrichten-Vorschlaege lokal auf approved setzen | niedrig bis mittel | kein Versand, Guard erforderlich |
| `reject_suggestions` | Vorschlaege lokal auf rejected setzen | niedrig | Guard erforderlich |
| `create_tasks` | Aufgaben-Vorschlaege lokal in Aufgaben umwandeln | mittel | Guard erforderlich, keine Duplikate |

## Verbotene Apply-Aktionen

Ein spaeteres Apply-Modell darf nicht:

- echte Nachrichten senden,
- echte Kalendertermine erstellen,
- externe APIs aufrufen,
- Provider verwenden,
- Obsidian schreiben,
- Backups/Restore/Import/Export ausloesen,
- Standing Approvals erstellen,
- Sicherheitsflags veraendern.

## Geplantes Ergebnis-Modell

Ein spaeteres Apply-Ergebnis koennte enthalten:

```text
applied: bool
action_type: str
affected_ids: tuple[int, ...]
created_task_ids: tuple[int, ...]
blocked_reasons: tuple[str, ...]
message: str
preview_only: bool
persisted: bool
external_action_used: bool
```

## Apply-Regeln fuer Nachrichten-Vorschlaege

`approve_messages`:

- nur Nachrichten-Vorschlaege,
- nur pending,
- kein Versand,
- Status darf nur lokal auf `approved` wechseln,
- Text bleibt lokaler Entwurf.

`reject_suggestions`:

- darf Nachrichten-Vorschlaege lokal ablehnen,
- Status darf nur lokal auf `rejected` wechseln,
- kein externer Effekt.

## Apply-Regeln fuer Aufgaben-Vorschlaege

`create_tasks`:

- nur Aufgaben-Vorschlaege,
- nur pending,
- erstellt lokale Aufgaben,
- setzt Aufgaben-Vorschlag auf `converted`,
- setzt `created_task_id`,
- darf bereits konvertierte Vorschlaege nicht duplizieren.

`reject_suggestions`:

- darf Aufgaben-Vorschlaege lokal ablehnen,
- Status darf nur lokal auf `rejected` wechseln.

## Transaktionsregel

Spaetere Apply-Implementierung muss nach Moeglichkeit atomar arbeiten:

- entweder alle gewaehlten lokalen Aenderungen erfolgreich,
- oder keine teilweise Batch-Aenderung.

Falls technische Atomizitaet nicht fuer alle Agent-/Repository-Kombinationen moeglich ist, muss dies vor Implementierung erneut geplant werden.

## UX-Regeln

Vor einem spaeteren Apply muss Friday klar anzeigen:

```text
Diese Batch-Aktion betrifft X Vorschlaege.
Es werden keine echten Nachrichten gesendet.
Es werden keine echten Kalendertermine erstellt.
```

Bei lokaler Task-Erstellung:

```text
Diese Batch-Aktion erstellt lokale Aufgaben.
```

Bei Abbruch:

```text
Batch-Aktion wurde abgebrochen.
```

## Vorgeschlagene spaetere Datei

```text
friday/app/review_batch_apply_model.py
```

## Vorgeschlagene spaetere Tests

```text
friday/tests/test_review_batch_apply_model.py
```

Testziele:

- ohne erlaubenden Guard wird nichts angewendet,
- `approve_messages` setzt nur lokale Nachrichten-Vorschlaege auf approved,
- `reject_suggestions` setzt Vorschlaege lokal auf rejected,
- `create_tasks` erstellt nur lokale Aufgaben,
- keine doppelten Tasks bei bereits converted Vorschlaegen,
- teilweise invalid Auswahl fuehrt nicht zu halbem Apply,
- keine externen Aktionen,
- Safe Flags stimmen.

## Nicht-Ziele

Dieser Plan baut noch nicht:

- keine Apply-Datei,
- keine Tests,
- keine CLI-Anbindung,
- keine Statusaenderung,
- keine Task-Erstellung,
- keine Datenbankschema-Aenderung,
- keine externen Integrationen.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
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

Naechster Build Step: **Review Batch Selection Apply Model**.

Ziel:

- isoliertes lokales Apply-Modell bauen,
- Guard-Ergebnis zwingend voraussetzen,
- fokussierte Tests mit tmp_path SQLite ergaenzen,
- keine CLI-Anbindung,
- keine externen Aktionen.
