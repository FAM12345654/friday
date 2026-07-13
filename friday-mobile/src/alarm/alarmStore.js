// Persisted alarm settings (local cache store, survives app restarts).
import { getCache, setCache } from "../data/localStore";

const ALARM_SETTINGS_KEY = "__alarm_settings";

export const DEFAULT_ALARM_SETTINGS = { enabled: false, time: "07:00" };

export async function getAlarmSettings() {
  try {
    const cached = await getCache(ALARM_SETTINGS_KEY);
    if (cached?.value && typeof cached.value === "object") {
      return { ...DEFAULT_ALARM_SETTINGS, ...cached.value };
    }
  } catch (error) {
    // fall through to defaults
  }
  return { ...DEFAULT_ALARM_SETTINGS };
}

export async function saveAlarmSettings(settings) {
  const next = { ...DEFAULT_ALARM_SETTINGS, ...settings };
  await setCache(ALARM_SETTINGS_KEY, next);
  return next;
}
