# Friday Mobile Redesign System

## Leitidee
Friday wirkt wie ein ruhiger privater Assistent: warm, kompetent, lokal und persoenlich. Das neue Markenzeichen ist kein Buchstabe, sondern ein Emblem aus Ruhepunkt, Kompassnadel, Blatt und Hausform.

## Logo
- **Marke:** geschuetztes Moos-Emblem mit hellem Ruhepunkt.
- **Bedeutung:** Kompass = Orientierung, Blatt = warm/lebendig, Hausform = lokal/privat, Punkt = Fokus.
- **Dateien:** `friday-mobile/assets/friday-logo-mark.svg`, `friday-mobile/assets/friday-wordmark.svg`, `icon.png`, `adaptive-icon.png`, `splash-icon.png`.

## Palette
| Rolle | Light | Dark-Idee |
|---|---|---|
| Hintergrund | `#f7f1e3` | `#101711` |
| Surface | `#fffaf0` | `#182218` |
| Karte | `#fff7e8` | `#202c1f` |
| Akzent | `#536a48` | `#b6c99f` |
| Akzent stark | `#31402d` | `#d9e4c8` |
| Text | `#263022` | `#f2eadb` |
| Soft Text | `#738069` | `#b8c4ad` |
| Warnung | `#b88d3f` | `#d9b96b` |
| Gefahr | `#b86a55` | `#d98973` |

## Typografie
- Display/Heading: 20-33 px, sehr kraeftig, enge Laufweite.
- Body: 14 px, 20-21 px Zeilenhoehe.
- Labels/Chips: 10-12 px, uppercase oder 800/900 Gewicht.

## Komponenten
- Karten: 24 px Radius, warme Flaeche, sehr weicher Schatten, dezenter Moos-Rand.
- Buttons: mindestens 44 px Touch-Ziel, 16 px Radius, klare Primaerfarbe.
- Chips: Punkt + Label, Status sofort sichtbar.
- Inputs: 46 px Mindesthoehe, runde Surface-Felder, dezenter Rand.
- Header: Markenzeichen, Tagesgruss, lokaler Status als Pille.
- Tabs: horizontale schnelle Bereichsauswahl; aktive Tabs tiefes Moos.

## Screen-Konzept
- Dashboard: Fokuskarte plus vier Kennzahlen, Status oben.
- Aufgaben: Quick Add, Prioritaetschips, Weiterleiten prominent als sichere Draft-Aktion.
- Kalender: Quellenchips fuer Google/PH/Familienhelden, Zeitfensterfilter als kompakte Controls.
- Nachrichten: Relevanzchips (`an dich`, `Team`, `Kunde: Philip`, `unsicher`), Detailkarte fuer Volltext.
- Kontakte: Initialen-Avatare, Relation/Betreuer-Chips, Assistenten-Notizen als ruhige Textbox.
- Lernen: Fragekarten mit freundlichem Ton, gelernte Regeln als deaktivierbare Liste.
- Setup/Konten: klare Verbindungszustaende (`verbunden`, `neu verbinden`, `read-only`).
- Datenschutz: lokale Safety-Matrix und transparente Flags.

## Accessibility
- Touch-Ziele mindestens 44 px.
- Keine rein farbliche Statuskommunikation: Chips nutzen Label + Punkt.
- Kontraststarke Primaertexte auf Creme/Moos.
- Ruhige Abstaende fuer Einhand-Nutzung.
