# Friday Mobile & Desktop Guide

## Ziel

Dieses Dokument beschreibt den lokalen Start von Friday auf Handy und Desktop nach dem Creme/Moos-Redesign.

Friday bleibt lokal-first:

- keine echten E-Mails,
- kein echtes WhatsApp,
- keine echte SMS,
- keine echten Kalenderaktionen,
- keine Cloud-AI,
- keine externen Provider-Aktionen.

## Handy-Installation

Aktueller Android-Preview-Build im Creme/Moos-Design (inklusive Cleartext-Freigabe fuer lokales HTTP):

`https://expo.dev/artifacts/eas/3cfGZ3nlTERdjOa7nHdsqlvatKwbk6veBVSWLd5KP3c.apk`

Wichtig: Nur dieser Build (und neuere) kann die lokale API ueber `http://` erreichen.
Aeltere Builds blockieren unverschluesseltes HTTP durch die Android-Netzwerkrichtlinie
und zeigen dauerhaft `Offline`.

Installation:

1. APK-Link auf dem Android-Handy oeffnen.
2. APK herunterladen.
3. Falls Android fragt: Installation aus unbekannten Quellen fuer den Browser erlauben.
4. APK installieren.
5. Friday starten.

Hinweis: Der Build ist eine interne Preview-APK, keine Play-Store-Version.

## Verbindung zur lokalen Friday API

Die Handy-App erwartet die lokale API standardmaessig unter:

`http://192.168.178.42:8000`

Voraussetzungen:

- PC und Handy sind im selben WLAN.
- Die Friday API laeuft auf dem PC.
- Port `8000` ist in der Windows-Firewall erlaubt.

API starten:

```powershell
.\start_friday_api.bat
```

Firewall-Regel, falls das Handy die API nicht erreicht:

```powershell
New-NetFirewallRule -DisplayName "Friday API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

Diese Firewall-Regel ist nur dokumentiert und wird von Friday nicht automatisch ausgefuehrt.

## Updates

Kleine JavaScript- oder Design-Updates koennen ueber den Preview-Kanal verteilt werden:

```powershell
.\publish_friday_mobile_update_preview.bat
```

Native Aenderungen brauchen einen neuen Android-Build, zum Beispiel:

- neues Icon,
- neue native Berechtigungen,
- neue native Pakete,
- Expo-/Runtime-Aenderungen.

Neuen Android-Preview-Build starten:

```powershell
.\build_friday_mobile_android_preview.bat
```

Release-Verifikation:

```powershell
.\verify_friday_mobile_release.bat
```

## Design-System

Friday Mobile und Desktop nutzen das gleiche helle Erscheinungsbild:

- Cremeweiss: `#f6f1e4`
- Moosgruen: `#5c7150`
- weiche Radien
- ruhige Schatten
- helle Oberflaechen
- Status-Pills, Tab-Pills, Statistik-Karten und Chips

Icon-Beschreibung:

- geometrisches cremefarbenes `F`,
- schraege Schnitte,
- Moos-Verlauf im Hintergrund,
- klarer, reduzierter App-Icon-Stil.

## Desktop

Desktop lokal starten:

```powershell
.\start_friday_desktop.bat
```

Alternative, wenn die API bereits separat laeuft:

```powershell
.\start_friday_desktop_skip_api.bat
```

Der Desktop nutzt:

- Fenstertitel `Friday`,
- helles Creme/Moos-Design,
- Fenster-Icon aus `friday-desktop/assets/icon.png`,
- automatisch ausgeblendete Menueleiste.

Fuer verpackte Desktop-Builds gilt:

- Die gepackte App erwartet eine laufende Friday API.
- Starte vorher `start_friday_api.bat`.
- Danach kann die Desktop-App geoeffnet werden.

## Safety

- Friday Mobile und Desktop zeigen lokale Daten aus der Friday API.
- Die API bleibt lokal auf dem Windows-PC.
- Es werden keine echten Nachrichten gesendet.
- Es werden keine echten Kalendertermine erstellt.
- Externe Integrationen bleiben deaktiviert.
- Safety-Flags bleiben unveraendert.
