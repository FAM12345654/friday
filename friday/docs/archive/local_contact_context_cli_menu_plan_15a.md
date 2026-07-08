# Contact CLI Menu Plan 15A

## Ziel

Definiert eine erste, reine **Kontakt-Kontext-Navigation** im lokalen CLI, ohne Produktänderungen.

Der Fokus ist die Planungsstruktur für das Menü und klare Sicherheitsgrenzen für spätere Schritte.

## Gewünschte Menüstruktur im Kontakt-Kontext

- Kontakt-Kontext
  1. Kontakte anzeigen
  2. Kontakte suchen
  3. Kontakt bearbeiten
  4. Kontakt vergessen
  5. Zurück

## UX-Ziele

- Kontaktmenü ist über das Hauptmenü eindeutig erreichbar.
- Für nicht vorhandene Daten gibt es stabile Rückmeldungen.
- Jeder Menüpfad hat klaren Rücksprung ohne Seiteneffekte.
- Keine Aktion löscht/speichert ohne harte Freigabe.

## Sicherheitsgrenzen (verbindlich)

- kein Kontaktimport,
- keine externen Dienste im Scope dieses Schritts,
- keine realen Nachrichten- oder Kalenderaktionen,
- keine unkontrollierte Schreiboperation,
- kein automatisches Löschen/Übernehmen von Änderungen.

## Auszublendende Implementierung

In 15A werden **nur diese Punkte umgesetzt**:

- Menüplan dokumentiert.
- Sicherheitsgrenzen für spätere Schrittfreigaben festgelegt.
- Doku-Indexaktualisierung.

Die folgenden Punkte bleiben bewusst offen:

- konkrete CLI-Pfade in `menu.py`,
- Interaktion mit `TaskAgent`/`MessageAgent`,
- Persistenz-/Repository-Nutzung im Menüfluss,
- neue Tests mit echter Menügesteuerung.

## Nächster Schritt

- **15B — Contact CLI Read-Only Menu**
- dort:
  - Menüoptionen in CLI verfügbar machen,
  - Kontakte anzeigen/suchen ohne Schreibfluss,
  - `Keine lokalen Kontakt-Kontexte vorhanden.` bei leerer Liste,
  - stabile Rückkehrtests.
