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

Die Handy-App prueft beim Start mehrere API-Adressen parallel und nimmt automatisch
die erste erreichbare (Failover-Reihenfolge):

1. `http://192.168.178.42:8000` — Heim-WLAN (LAN, schnellster Weg)
2. `http://100.122.129.101:8000` — Tailscale-VPN (unterwegs)

Die aktive Adresse steht in der App unten im Footer.

Voraussetzungen zuhause:

- PC und Handy sind im selben WLAN.
- Die Friday API laeuft auf dem PC.
- Port `8000` ist in der Windows-Firewall erlaubt.

## Unterwegs (Tailscale)

Unterwegs laeuft die Verbindung ueber das private Tailscale-VPN — die API wird dabei
NICHT oeffentlich ins Internet gestellt.

Voraussetzungen unterwegs:

- Der PC ist eingeschaltet und Tailscale ist verbunden (Tray-Icon aktiv;
  pruefen mit `tailscale status`).
- Die Friday API laeuft auf dem PC (`start_friday_api.bat`).
- Auf dem Handy ist die Tailscale-App installiert, mit demselben Konto angemeldet
  und das VPN ist eingeschaltet.

Hinweise:

- Die Tailscale-Adresse `100.122.129.101` ist dem PC fest zugeordnet und bleibt stabil.
- Zuhause funktioniert die App auch ohne Tailscale (LAN-Fallback).
- Faellt eine Adresse aus, wechselt die App automatisch zur naechsten erreichbaren.

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

Friday Mobile prueft beim App-Start aktiv auf neue Preview-Updates.
Wenn ein Update verfuegbar ist, wird es geladen und die App startet automatisch neu.
Details stehen in `FRIDAY_MOBILE_AUTO_UPDATE_GATE.md`.

Im Aufgabenbereich gibt es zusaetzlich ein lokales Feld `Weiterleiten an Kollege`.
Es speichert nur eine Notiz an der Aufgabe und sendet keine Nachricht.
Details stehen in `FRIDAY_MOBILE_TASK_FORWARD_FIELD.md`.

Zusaetzlich kann eine Aufgabe ueber `Weiterleiten` als lokaler Entwurf fuer einen gespeicherten Kontakt vorbereitet werden.
Dabei kann E-Mail oder WhatsApp als Zielkanal ausgewaehlt werden.
Auch dieser Flow sendet nichts echt; Details stehen in `FRIDAY_MOBILE_TASK_DELEGATION_DRAFT_FLOW.md`.
Der Weg zu spaeterem echtem Versand ist in `FRIDAY_MESSAGING_PROVIDER_GATE.md` dokumentiert.

## Aufgaben weiterleiten mit KI-Draft

Der Weiterleiten-Flow erstellt jetzt einen lokalen KI-Entwurf mit dem lokalen Ollama-Modell `qwen3:8b`, wenn Ollama auf dem Windows-PC erreichbar ist.
Falls Ollama nicht erreichbar ist, bleibt Friday im lokalen Fallback und sendet trotzdem nichts.

Ablauf in der Handy-App:

1. Aufgabe oeffnen.
2. `Weiterleiten` waehlen.
3. Gespeicherten Kontakt auswaehlen.
4. Kanal auswaehlen: E-Mail oder WhatsApp.
5. KI-Draft pruefen.
6. Harten Token eingeben:
   - `EMAIL SENDEN` fuer E-Mail-Deep-Link,
   - `WHATSAPP SENDEN` fuer WhatsApp-Deep-Link.
7. Friday oeffnet nur die externe App mit vorbereitetem Text.
8. Der Nutzer entscheidet in E-Mail oder WhatsApp selbst, ob wirklich gesendet wird.

Wichtig:

- Friday sendet keine echte Nachricht.
- Friday nutzt keine Cloud-KI.
- Der KI-Draft laeuft lokal ueber `http://localhost:11434`.
- Die externen Safety-Flags fuer E-Mail und WhatsApp bleiben `False`.

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
