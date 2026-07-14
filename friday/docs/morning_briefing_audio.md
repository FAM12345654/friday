# Morning Briefing Audio

Friday erzeugt das Morning Briefing nachts lokal auf dem Home-PC. Der englische Text wird aus lokalen Aufgaben, dem zusammengeführten Kalender und Open-Meteo-Daten aufgebaut. Kokoro rendert die MP3 mit `lang_code="a"` und der Stimme `af_heart`.

## Ablauf

1. Der Backend-Scheduler startet täglich um 03:00 Uhr in `Europe/Berlin`.
2. Friday berechnet die Weckzeit und erstellt das englische Briefing.
3. Erst nach erfolgreichem Rendering ersetzt die neue MP3 die alte Datei. Auf dem Server liegt maximal eine `briefing_*.mp3`.
4. Ein Expo-Push informiert das registrierte Handy.
5. Die App lädt die MP3 sofort in ihren lokalen Dokumentordner. Erst nach erfolgreichem Download wird die vorherige MP3 entfernt.
6. Zwischen 05:00 und 10:00 Uhr wird das Briefing höchstens einmal täglich abgespielt. Das Antippen der Weckbenachrichtigung startet es ebenfalls.

## Konfiguration

- `FRIDAY_EXPO_PUSH_TOKEN`: optionaler statischer Expo-Push-Token. Normalerweise registriert die App ihren Token selbst.
- `FRIDAY_MORNING_INTERNAL_TOKEN`: schützt den internen manuellen Push-Endpunkt.
- `FRIDAY_OPEN_METEO_LATITUDE` und `FRIDAY_OPEN_METEO_LONGITUDE`: Standort für den Wettertext; Standard ist Berlin.
- `MORNING_BRIEFING_VOICE = "af_heart"`
- `MORNING_BRIEFING_LANG_CODE = "a"`

## Lokale Safety-Regeln

- Alte Serverdateien werden erst nach erfolgreicher Audioerzeugung gelöscht.
- Alte Handydateien werden erst nach erfolgreichem Download ersetzt.
- Fehlende Push-Zustellung wird beim nächsten App-Start durch Status-Polling aufgefangen.
- Lokale Briefing-Dateien älter als 24 Stunden werden gelöscht.
- `Morgen überspringen` gilt einmalig; `Automatik pausieren` bleibt aktiv, bis der Nutzer sie wieder einschaltet.
- Die Morning Routine sendet keine E-Mails oder Nachrichten und schreibt keine Kalendertermine.

## Installation und Build

Backend-Abhängigkeiten werden mit `python -m pip install -r requirements.txt` installiert. Kokoro lädt beim ersten Rendering das lokale Modell (ungefähr 313 MiB). Auf dem aktuellen Home-PC läuft PyTorch im CPU-Modus.

Die Mobile-App benötigt wegen `expo-notifications`, `expo-task-manager`, `expo-file-system` und `expo-av` einen neuen nativen Android-Build. Ein reines OTA-Update kann diese nativen Module nicht in eine ältere APK einbauen.

## Prüfkommandos

```powershell
python -m pytest friday/tests/test_morning_routine.py friday/tests/test_briefing_generator.py friday/tests/test_briefing_push.py friday/tests/test_friday_api_morning_briefing.py
python scripts/friday_safety_smoke.py
cd friday-mobile
npm run test:morning
npx expo export --platform android
```
