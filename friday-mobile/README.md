# Friday Mobile (React Native + Expo)

## Setup

```bash
cd friday-mobile
npm install
copy .env.example .env
```

Setze `EXPO_PUBLIC_FRIDAY_API_URL` in `.env` auf die erreichbare API-URL:

- Emulator: `http://10.0.2.2:8000`
- iOS Sim: `http://127.0.0.1:8000`
- Physisches Gerät: `http://<deine-PC-IP>:8000`

## Start

Mit dem zentralen Startskript:

```bash
cd ..
start_friday_stack.bat
```

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
