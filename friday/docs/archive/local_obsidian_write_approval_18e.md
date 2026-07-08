# Local Obsidian Write Approval 18E

## Ziel

Build Step 18E ergaenzt einen streng gegateten lokalen Obsidian-Write.

Ein Write ist nur moeglich, wenn:
- `write_enabled=True` explizit uebergeben wird,
- der Zielpfad im erlaubten Unterordner liegt,
- die Zieldatei noch nicht existiert,
- die Bestaetigung exakt `OBSIDIAN SCHREIBEN` lautet.

## Approval-Token

```text
OBSIDIAN SCHREIBEN
```

Andere Eingaben wie `JA`, `ja` oder leere Eingaben schreiben nicht.

## Bewusst unveraendert

- Keine CLI-Anbindung.
- Kein automatischer Write.
- Keine Obsidian-Integration mit Sync.
- Keine externen Aktionen.
- Keine Datenbankschema-Aenderung.
- Keine Aenderung an Task-Delete-Policy.

## Tests

- Falscher Token schreibt nicht.
- Harter Token schreibt lokal in `tmp_path`.
- Bestehende Datei wird nicht ueberschrieben.
- Preview-Markdown bleibt der geschriebene Inhalt.

## Safety-Bewertung

- Obsidian bleibt standardmaessig deaktiviert.
- Echter Write ist nur lokal und testisoliert abgesichert.
- Keine echten Nachrichten oder Kalenderaktionen.
- Keine Provider- oder Netzwerkaufrufe.

## Empfehlung für Build Step 19A

Als naechsten Schritt kann das Local Provider Interface geplant werden. Es soll weiterhin ohne echte Provider-Nutzung starten.
