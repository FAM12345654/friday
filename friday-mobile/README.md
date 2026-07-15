# Friday Mobile (React Native + Expo)

## Setup

```bash
cd friday-mobile
npm install
copy .env.example .env
```

Setze `EXPO_PUBLIC_FRIDAY_API_URL` in `.env` auf die geschützte Geräte-URL:

- Android, iOS, Emulator und physisches Gerät: `https://pc.tail4c6152.ts.net`
- Unverschlüsseltes LAN-HTTP ist absichtlich deaktiviert.

## Start

Mit dem zentralen Startskript:

```bash
cd ..
start_friday_stack.bat
```

Für WLAN, Tailscale oder Tunnel muss auf dem API-Rechner zusätzlich ein
zufälliger `FRIDAY_API_TOKEN` mit mindestens 32 Zeichen gesetzt sein. Den
gleichen Token in der App unter **Mehr > Datenschutz** speichern. Er bleibt im
Geräte-Keystore und gehört nicht in `EXPO_PUBLIC_*`, `app.json` oder EAS-Updates.
Friday sendet diesen Token niemals über unverschlüsseltes WLAN-HTTP.

oder nur Mobile:

```bash
npm run start
```

Scanne anschließend den QR-Code mit Expo Go oder starte einen Emulator.

## Handy-Download (installierbare App)

Für einen echten Handy-Download nutzt Friday Mobile EAS Build:

```bash
cd ..
verify_friday_mobile_release.bat
configure_friday_mobile_eas.bat
build_friday_mobile_android_preview.bat
```

`build_friday_mobile_android_preview.bat` erzeugt einen EAS-Link für eine direkt installierbare Android-APK.

## Automatische Updates

Nach der einmaligen EAS-Konfiguration und einem installierten Preview-Build kannst du kleine Änderungen ohne neuen APK-Download ausrollen:

```bash
cd ..
publish_friday_mobile_update_preview.bat
```

Der installierte Preview-Build prüft beim App-Start auf Updates. Das Update wird im Hintergrund geladen und nach einem Neustart der App aktiv.

Native Änderungen (z. B. neue native Expo/React-Native-Pakete, neue Berechtigungen oder SDK-Wechsel) brauchen weiterhin einen neuen Build.

## 6 Screens (Feature-Ziele)

- Dashboard
- Tasks
- Nachrichten / Vorschläge
- Kalender
- Kontakte
- Datenschutz
