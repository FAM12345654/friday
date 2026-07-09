# Friday Mobile & Desktop Guide

## Ziel

Dieses Dokument beschreibt den lokalen Start von Friday auf Handy und Desktop nach dem Creme/Moos-Redesign.

Friday bleibt lokal-first:

- keine echten E-Mails,
- kein echtes WhatsApp,
- keine echte SMS,
- echte Kalenderaktionen nur als bewusst aktivierte Ausnahme mit hartem Token pro Termin,
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

## Setup-Screen und Termin-Erkennung

Die Mobile-App enthaelt einen Setup-Tab. Dort sieht man lokal:

- ob Friday lokal laeuft,
- ob die lokale KI aktiv ist,
- welche Safety-Flags gesetzt sind,
- ob E-Mail/WhatsApp nur vorbereitet oder verbunden sind,
- dass echte Kalender-Schreibaktionen bewusst aktiviert sind (Google, pro Termin mit `TERMIN SPEICHERN`).

In der Nachrichtenansicht gibt es zusaetzlich `Termin erkennen`.
Friday erstellt daraus nur einen lokalen Review-Vorschlag.
Datum und Uhrzeit werden deterministisch in Python aufgeloest; das Modell darf relative Angaben nicht allein entscheiden.
Ein echter Google-Termin entsteht erst nach deiner Bestaetigung mit `TERMIN SPEICHERN`.

## Kalender-Konten und Account-Policies

Im Setup-Tab gibt es einen Bereich fuer Kalender-Konten und Account-Policies.
Eine Policy beschreibt pro Konto:

- Provider, z. B. `google_calendar`,
- Rolle, z. B. `main` oder `source`,
- Zugriff, z. B. `read` oder `read_write`,
- harte Filter, z. B. Titel enthaelt `PH`,
- Notizen fuer lokalen KI-Kontext.

Policies werden nur mit dem Token `POLICY SPEICHERN` gespeichert.
`ENABLE_REAL_CALENDAR` ist als bewusste Ausnahme aktiviert (nur Kalender; E-Mail/WhatsApp/SMS/Wetter/Musik bleiben erzwungen aus).
Ein echter Google-Termin-Write braucht pro Termin exakt `TERMIN SPEICHERN` plus Haupt-Policy und Verbindung.
Loeschen braucht exakt `TERMIN LOESCHEN`. Outlook-ICS-Quellen bleiben rein lesbar.

Google OAuth laeuft am PC. Client-Secrets und OAuth-Tokens gehoeren nicht in Git, nicht in Screenshots und nicht in Chat-Nachrichten.
Details stehen in `FRIDAY_CALENDAR_ACCOUNTS_GATE.md`.

Im Aufgabenbereich gibt es zusaetzlich ein lokales Feld `Weiterleiten an Kollege`.
Es speichert nur eine Notiz an der Aufgabe und sendet keine Nachricht.
Details stehen in `FRIDAY_MOBILE_TASK_FORWARD_FIELD.md`.

Zusaetzlich kann eine Aufgabe ueber `Weiterleiten` als lokaler Entwurf fuer einen gespeicherten Kontakt vorbereitet werden.
Dabei kann E-Mail oder WhatsApp als Zielkanal ausgewaehlt werden.
Auch dieser Flow sendet nichts echt; Details stehen in `FRIDAY_MOBILE_TASK_DELEGATION_DRAFT_FLOW.md`.
Der Weg zu spaeterem echtem Versand ist in `FRIDAY_MESSAGING_PROVIDER_GATE.md` dokumentiert.

## Kontakte, Kunden-Betreuer und To-do-Regel

Im Kontakte-Tab koennen haeufige Kontakte lokal gespeichert werden.
Die Kontaktart bleibt eine lokale Relation, z. B. `arbeit`, `freund`, `familie`, `kunde` oder `sonstiges`.

Wenn ein Kontakt als `Kunde` gespeichert wird, kann zusaetzlich ein Betreuer gewaehlt werden:

- Flo
- Philip
- Alex

Diese Betreuer-Information steuert lokale Aufgaben-Vorschlaege:

- Task-artige Nachrichten werden nur als To-do vorgeschlagen, wenn der Text ganzwoertig `Philip`, `Phips`, `PH` oder `Zeitler` enthaelt.
- Oder wenn der bekannte Absender ein Kunde mit Betreuer `Philip` ist.
- Andere Kunden oder private Kontakte erzeugen nicht automatisch ein To-do fuer Philip.

In der Nachrichtenansicht kann ein unbekannter Absender direkt lokal als Kontakt gespeichert werden.
Bei `Kunde` wird dort ebenfalls der Betreuer ausgewaehlt.
Friday sendet dabei nichts und nutzt keine Cloud-KI; die Regel ist deterministisch in Python.
Details stehen in `FRIDAY_CONTACT_BETREUER_TODO_RULE_GATE.md`.

## WhatsApp mitlesen (Read-Bridge)

Friday enthaelt eine lokale WhatsApp-Web-Read-Bridge als getrenntes Node-Projekt unter `friday-whatsapp-bridge/`.
Diese Bridge liest nur eingehende Einzelchat-Nachrichten und spiegelt sie lokal an die Friday API.
Friday sendet ueber diese Bridge nie automatisch.

Risiko-Hinweis:

- WhatsApp-Web-Bridges koennen gegen WhatsApp-Regeln verstossen.
- Es besteht ein moegliches Kontosperrungs-Risiko.
- Empfohlen ist eine Zweitnummer oder ein bewusst begrenzter Testbetrieb.
- Gruppen werden standardmaessig ignoriert.
- Senden bleibt nur der bestehende WhatsApp-Link, bei dem du am Handy selbst auf Senden tippst.

Aktivierung:

1. In Friday das Konten-Menue oeffnen.
2. `WhatsApp Read-Bridge Aktivierung prüfen` waehlen.
3. Risiko-Hinweis lesen.
4. Exakt `WHATSAPP BRIDGE AKTIVIEREN` eingeben.
5. Safety Smoke muss `PASS` sein.
6. Danach API starten und die Bridge separat starten:

```powershell
.\start_friday_api.bat
.\start_whatsapp_bridge.bat
```

Erster Start:

- Falls `node_modules` fehlt, einmal im Bridge-Ordner ausfuehren:

```powershell
cd friday-whatsapp-bridge
npm install
```

- Beim ersten Bridge-Start erscheint ein QR-Code im Terminal.
- QR-Code mit WhatsApp auf dem Handy scannen.
- Danach spiegelt Friday neue eingehende Einzelchat-Nachrichten lokal.

Lokale Dateien:

- Session, Token und Bridge-Konfiguration liegen unter `local_data/whatsapp/`.
- Dieser Ordner ist gitignored.
- Telefonnummern werden in der Friday-DB nur gehasht/maskiert gespeichert.

Stoppen:

```powershell
.\stop_whatsapp_bridge.bat
```

Oder im laufenden Bridge-Terminal `STRG+C` druecken.

Rollback:

1. `ENABLE_WHATSAPP_BRIDGE_READ = False` in `friday/config.py` setzen.
2. Bridge stoppen.
3. Optional `local_data/whatsapp/` loeschen, wenn QR-Session und lokale Bridge-Daten entfernt werden sollen.

## E-Mail-Konto verbinden (Gate)

Friday kann ein einzelnes E-Mail-Konto lokal vorbereiten und testen. Das Konto bleibt auf dem Windows-PC in `local_data/accounts/email_account.json`.
Das App-Passwort wird unter Windows mit DPAPI geschuetzt. Falls DPAPI nicht verfuegbar ist, zeigt Friday einen Warnstatus und nutzt nur eine unsichere lokale Fallback-Codierung.

Wichtig:

- `ENABLE_REAL_EMAIL` bleibt standardmaessig `False`.
- Ein verbundenes Konto aktiviert noch keinen echten Versand.
- Echte E-Mail waere erst in einem spaeteren Gate erlaubt.
- Empfaenger muessen als lokale Kontakte gespeichert sein.
- Die spaetere Tagesgrenze ist auf 20 E-Mails vorbereitet.
- Jeder spaetere echte Versand braucht den harten Token `EMAIL SENDEN`.
- WhatsApp bleibt weiterhin nur Deep-Link/App-Oeffnung. Friday automatisiert WhatsApp nicht.

Gmail-App-Passwort vorbereiten:

1. Im Google-Konto die Zwei-Faktor-Authentifizierung aktivieren.
2. Ein App-Passwort fuer Mail erstellen.
3. Dieses App-Passwort in Friday als E-Mail-Passwort eintragen.
4. Token `KONTO SPEICHERN` verwenden, wenn Friday das Konto lokal speichern soll.
5. Danach die Verbindung testen.

Empfohlener sicherer Weg:

- Konto zuerst am PC im lokalen Netzwerk einrichten.
- Danach in der Handy-App nur den Status pruefen.
- Keine echten Zugangsdaten in Screenshots, Logs, Chat oder Git kopieren.

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
- Es werden keine echten Kalendertermine ohne harten Token pro Termin erstellt.
- Externe Integrationen bleiben deaktiviert.
- Safety-Flags bleiben unveraendert.

## Outlook-ICS, Termin-Flow und Delete

- Outlook-ICS kann als read-only Kalenderquelle ueber eine Account-Policy gespeichert werden.
- Die ICS-URL wird lokal verschluesselt abgelegt und nicht in API-Antworten angezeigt.
- Kalenderquellen werden in der Kalenderansicht zusammengefuehrt; PH-Filter laufen deterministisch in Python.
- Fuer Outlook-ICS-Policies kann ein lokales PH-Zeitfenster gesetzt werden.
  Aktuell wird `team-hampejs`/PH als Tagesblock `08:00` bis `18:00` angezeigt,
  ohne diese Regel auf andere Kalenderquellen anzuwenden.
- Termin-aus-Nachricht ist ein Review-Flow: bearbeiten, pruefen, dann erst mit `TERMIN SPEICHERN` in Google schreiben.
- Google-Termine koennen nur mit `TERMIN LOESCHEN` geloescht werden.
- E-Mail, WhatsApp, SMS, Wetter und Musik bleiben deaktiviert.

Details: `FRIDAY_CALENDAR_SOURCES_AND_FLOW_GATE.md`.

## Kalenderansicht und Filter

Die Kalenderansicht der Mobile-App nutzt die zusammengefuehrte Liste `merged_items`.
Damit erscheinen lokale Termine, Google-Hauptkalender und read-only Quellen wie Outlook-ICS in einer gemeinsamen Ansicht.

In der App koennen fuer die Ansicht gesetzt werden:

- Heute,
- 7 Tage,
- 30 Tage,
- eigener Zeitraum,
- Tageszeitfenster, z. B. `08:00` bis `18:00`.

Der PH-Filter fuer Outlook-ICS arbeitet tokenbasiert:

- `PH`, `PH+D` und `PH-Dienst` werden erkannt,
- `Philip`, `GRAPH` und `graphisch` werden nicht faelschlich getroffen.

Details: `FRIDAY_CALENDAR_VIEW_FILTER_FIXES_GATE.md`.

## Agent-Notizen fuer lokale KI-Entwuerfe

Friday kann lokale Agent-Notizen speichern fuer:

- E-Mail-Konto,
- WhatsApp-Read-Bridge,
- einzelne Kontakte/Personen,
- Account-Policies.

Diese Notizen bleiben lokal und werden nur fuer lokale KI-Entwuerfe verwendet.
Sie werden nicht an E-Mail, WhatsApp, Kalender, Cloud-KI oder externe Provider gesendet.

In der Mobile-App sind die Notizen sichtbar in:

- `Kontakte` fuer Personen-Notizen,
- `Datenschutz`/Konten fuer E-Mail- und WhatsApp-Agent-Notizen,
- `Setup` fuer Account-Policy-Notizen und PH-Zeitfenster.

Details: `FRIDAY_PH_TIME_WINDOW_AGENT_NOTES_GATE.md`.

## Familienhelden-Postfach read-only via Microsoft Graph

Friday kann das Familienhelden-Microsoft-365-Postfach nur lesend verbinden. Das ist getrennt vom normalen E-Mail-Senden: `ENABLE_REAL_EMAIL` bleibt aus.

### Azure App Registrierung

1. In Azure / Entra ID eine App Registration erstellen.
2. Anwendungstyp: Public Client / Mobile & Desktop.
3. Redirect URI: `http://localhost`.
4. Microsoft Graph Delegated Permissions setzen:
   - `Mail.Read`
   - `offline_access`
   - `User.Read`
5. Kein `Mail.Send` vergeben.
6. Client-ID in der Friday App in `Setup` oder `Datenschutz > Konten` eintragen.

### Verbinden in Friday

1. In der App `OAuth-Link öffnen` antippen.
2. Microsoft Login abschliessen.
3. Die `localhost` Rueckgabe-URL in Friday einfuegen.
4. Token `KONTO SPEICHERN` eingeben.
5. Danach `MAIL LESEN AKTIVIEREN` ausfuehren und Friday API neu starten.
6. Danach kann `Familienhelden-Mails synchronisieren` genutzt werden.

Grenzen:

- Friday liest nur Betreff, Absender, Empfangszeit und Vorschau.
- Friday sendet keine E-Mail.
- Aufgaben und Termine entstehen nur als lokale Review-Vorschlaege.
- Sync ist deaktiviert, solange `ENABLE_MS_MAIL_READ = False` ist.

Details: `FRIDAY_MS_MAIL_READ_GATE.md`.
