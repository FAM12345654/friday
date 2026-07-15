# Morning Briefing Audio (Vorproduktion)

Friday kann das gesprochene Morning-Briefing vorab erzeugen, damit der
Morgen-Wecker es sofort abspielt, statt auf die Live-Synthese zu warten. Der
Text entsteht über `friday/app/voice_briefing.py` (`build_briefing_text`) aus
den lokalen Aufgaben, dem zusammengeführten Kalender und – optional – dem
Wetter. Die Audioausgabe läuft über die lokalen TTS-Server aus
`friday/app/voice_synthesis.py` (Deutsch: Orpheus, Englisch: Kokoro, jeweils
OpenAI-kompatibel auf localhost). Es gibt keinen zweiten TTS-Client und keinen
zweiten Textbaustein.

## Ablauf

1. `scripts/friday_pregenerate_briefing.py` wird geplant ausgeführt (z. B.
   nachts per Cron). Beispiel: `0 3 * * * cd /pfad/zu/friday && python scripts/friday_pregenerate_briefing.py`.
2. Das Skript baut den Briefing-Text, ruft optional das Wetter ab
   (nur wenn `ENABLE_WEATHER_BRIEFING = True`) und synthetisiert das Audio.
3. Erst nach erfolgreicher Synthese ersetzt die neue Datei die alte
   (`briefing_<datum>.wav` unter `local_data/briefings/`). Eine kleine
   `briefing_status.json` hält Datum, Zeit, Sprache und Engine fest.
4. Alte Dateien werden automatisch beschnitten (Standard: die letzten 7
   bleiben, `BRIEFING_PREGEN_KEEP_LAST`).
5. Ist `ENABLE_PUSH_NOTIFICATIONS = True` und ein Gerät registriert, sendet
   das Skript einen „Briefing bereit"-Push (`notify_briefing_ready`).
6. Der Wecker (oder ein Test-Tap) ruft
   `GET /api/voice/morning-briefing?prefer_pregenerated=true` auf. Existiert
   die vorproduzierte Datei für heute, liefert die API deren Audio (Base64)
   sofort zurück; andernfalls synthetisiert sie live weiter.

## Konfiguration (`friday/config.py`)

- `BRIEFING_PREGEN_LANGUAGE` – Sprache der Vorproduktion (Standard `"de"`).
- `BRIEFING_PREGEN_KEEP_LAST` – Anzahl behaltener Audiodateien (Standard 7).
- `BRIEFING_PREGEN_DIR` – Ablageort (`local_data/briefings`).
- `ENABLE_WEATHER_BRIEFING` – Opt-in für den Wettersatz (Standard `False`).
- `OPEN_METEO_LATITUDE` / `OPEN_METEO_LONGITUDE` – Standort (per
  `FRIDAY_WEATHER_LATITUDE` / `FRIDAY_WEATHER_LONGITUDE`, Standard Berlin).
- `ENABLE_PUSH_NOTIFICATIONS` – Opt-in für den „Briefing bereit"-Push.

## Lokale Safety-Regeln

- Alte Serverdateien werden erst nach erfolgreicher Audioerzeugung ersetzt.
- Das Wetter ist ein externer HTTP-Aufruf und bleibt hinter
  `ENABLE_WEATHER_BRIEFING`; bei deaktiviertem Flag oder Netzfehler fällt der
  Wettersatz still weg.
- TTS läuft ausschließlich lokal (localhost-Guard in `voice_synthesis.py`).
- Push bleibt hinter `ENABLE_PUSH_NOTIFICATIONS` (externer Expo-Dienst).
- Die Vorproduktion sendet keine E-Mails oder Nachrichten und schreibt keine
  Kalendertermine.

## Prüfkommandos

```bash
python -m pytest friday/tests/test_briefing_pregeneration.py \
  friday/tests/test_open_meteo_weather.py \
  friday/tests/test_voice_briefing.py \
  friday-api/tests/test_voice_endpoints.py
python scripts/friday_pregenerate_briefing.py
```
