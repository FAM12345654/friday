// Lightweight DE/EN i18n for Friday mobile.
//
// German stays the default and the fallback for untranslated keys, so the
// app can be translated incrementally. The chosen locale is persisted in the
// local cache store.
import { getCache, setCache } from "./data/localStore";

const LOCALE_CACHE_KEY = "__locale";
export const SUPPORTED_LOCALES = ["de", "en"];

const dictionaries = {
  de: {
    "nav.Home": "Home",
    "nav.Kalender": "Kalender",
    "nav.Tasks": "Aufgaben",
    "nav.Nachrichten": "Posteingang",
    "nav.Mehr": "Mehr",
    "more.Kontakte.label": "Kontakte",
    "more.Kontakte.description": "Personen, Kunden und Notizen",
    "more.Lernen.label": "Lernen",
    "more.Lernen.description": "Offene Fragen und gelernte Regeln",
    "more.Setup.label": "Einrichten",
    "more.Setup.description": "Konten, lokale KI und Verbindungen",
    "more.Datenschutz.label": "Datenschutz",
    "more.Datenschutz.description": "Safety-Status und lokale Grenzen",
    "more.Spam.label": "Spam / Blockiert",
    "more.Spam.description": "Lokal blockierte Absender",
    "common.language": "Sprache",
    "common.busy": "Aktion läuft…",
    "common.footer": "lokal & privat",
    "voice.hold": "Halten zum Sprechen",
    "voice.listening": "Ich höre zu…",
    "voice.thinking": "Friday denkt nach…",
    "voice.speaking": "Friday spricht…",
    "voice.noPermission": "Mikrofon-Berechtigung fehlt.",
    "voice.noAudioModule": "Audio-Modul nicht verfügbar (neuer Build nötig).",
    "voice.noRecording": "Keine Aufnahme vorhanden.",
    "alarm.title": "Morgen-Wecker",
    "alarm.hint": "Weckt dich mit deinem gesprochenen Tages-Briefing.",
    "alarm.on": "An",
    "alarm.off": "Aus",
    "alarm.test": "Briefing jetzt abspielen",
    "alarm.testing": "Briefing wird geladen…",
    "alarm.scheduled": "Wecker gestellt für",
    "alarm.disabled": "Wecker ist aus.",
    "alarm.timeInvalid": "Zeit bitte als HH:MM angeben, z. B. 07:00.",
    "alarm.failed": "Wecker konnte nicht gestellt werden.",
    "alarm.noModule": "Wecker-Modul nicht verfügbar (neuer Build nötig).",
    "alarm.noPermission": "Benachrichtigungs-Berechtigung fehlt.",
    "alarm.notificationTitle": "Friday Wecker",
    "alarm.notificationBody": "Tippe für dein Morgen-Briefing.",
    "alarm.textOnly": "Nur Text (TTS-Server aus)",
  },
  en: {
    "nav.Home": "Home",
    "nav.Kalender": "Calendar",
    "nav.Tasks": "Tasks",
    "nav.Nachrichten": "Inbox",
    "nav.Mehr": "More",
    "more.Kontakte.label": "Contacts",
    "more.Kontakte.description": "People, customers and notes",
    "more.Lernen.label": "Learning",
    "more.Lernen.description": "Open questions and learned rules",
    "more.Setup.label": "Setup",
    "more.Setup.description": "Accounts, local AI and connections",
    "more.Datenschutz.label": "Privacy",
    "more.Datenschutz.description": "Safety status and local boundaries",
    "more.Spam.label": "Spam / Blocked",
    "more.Spam.description": "Locally blocked senders",
    "common.language": "Language",
    "common.busy": "Working…",
    "common.footer": "local & private",
    "voice.hold": "Hold to talk",
    "voice.listening": "Listening…",
    "voice.thinking": "Friday is thinking…",
    "voice.speaking": "Friday is speaking…",
    "voice.noPermission": "Microphone permission missing.",
    "voice.noAudioModule": "Audio module unavailable (new build required).",
    "voice.noRecording": "No recording captured.",
    "alarm.title": "Morning alarm",
    "alarm.hint": "Wakes you with your spoken daily briefing.",
    "alarm.on": "On",
    "alarm.off": "Off",
    "alarm.test": "Play briefing now",
    "alarm.testing": "Loading briefing…",
    "alarm.scheduled": "Alarm set for",
    "alarm.disabled": "Alarm is off.",
    "alarm.timeInvalid": "Please enter the time as HH:MM, e.g. 07:00.",
    "alarm.failed": "Could not set the alarm.",
    "alarm.noModule": "Alarm module unavailable (new build required).",
    "alarm.noPermission": "Notification permission missing.",
    "alarm.notificationTitle": "Friday alarm",
    "alarm.notificationBody": "Tap for your morning briefing.",
    "alarm.textOnly": "Text only (TTS server off)",
  },
};

let currentLocale = "de";

export function getAppLocale() {
  return currentLocale;
}

export async function initLocale() {
  try {
    const cached = await getCache(LOCALE_CACHE_KEY);
    if (cached?.value && SUPPORTED_LOCALES.includes(cached.value)) {
      currentLocale = cached.value;
    }
  } catch (error) {
    // keep default
  }
  return currentLocale;
}

export async function setAppLocale(locale) {
  if (!SUPPORTED_LOCALES.includes(locale)) {
    return currentLocale;
  }
  currentLocale = locale;
  try {
    await setCache(LOCALE_CACHE_KEY, locale);
  } catch (error) {
    // persistence is best-effort
  }
  return currentLocale;
}

export function t(key) {
  const table = dictionaries[currentLocale] || dictionaries.de;
  return table[key] ?? dictionaries.de[key] ?? key;
}
