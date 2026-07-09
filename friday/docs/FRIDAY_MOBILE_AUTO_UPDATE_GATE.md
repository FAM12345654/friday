# Friday Mobile Auto Update Gate

## Ziel

Friday Mobile prueft beim App-Start aktiv auf ein neues Expo-Update.

Wenn ein neues Update im Preview-Kanal verfuegbar ist:

1. Friday laedt das Update.
2. Friday startet die App automatisch neu.
3. Danach laeuft die neue Version.

## Umsetzung

Die Logik liegt in:

`friday-mobile/App.js`

Verwendet wird:

`expo-updates`

Der Footer zeigt zusaetzlich einen kleinen Status:

- `Update: pruefe...`
- `Update: aktuell`
- `Update: wird installiert...`
- `Update: spaeter erneut`

## Wichtig fuer das erste Update

Die aktuell installierte App muss dieses Update-Gate selbst erst per OTA erhalten.

Darum kann beim ersten Mal weiterhin noetig sein:

1. App komplett schliessen.
2. App oeffnen.
3. 10 bis 20 Sekunden warten.
4. App erneut komplett schliessen.
5. App erneut oeffnen.

Ab dann ist das neue Auto-Update-Gate aktiv.

## Safety

- Keine externen Friday-Produktaktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Provider-/OAuth-Aenderung.
- Keine Python-/DB-Aenderung.
- Nur Expo-Update-Pruefung fuer die Mobile-App.
