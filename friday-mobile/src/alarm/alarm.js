// Morning alarm for Friday: a daily Notifee trigger notification that rings
// like an alarm clock (USAGE_ALARM channel, full-screen intent on Android)
// and plays the spoken morning briefing when it fires or is tapped.
//
// Notifee is a native module — it loads dynamically so OTA-updated builds
// without it degrade with a clear message instead of crashing. On iOS the
// alarm is a time-sensitive notification (third-party apps cannot override
// silent mode there); on Android it uses AlarmManager with allowWhileIdle.
import { getVoiceMorningBriefing } from "../api/client";
import { getAppLocale, t } from "../i18n";
import { playBase64Wav } from "../voice/audio";

export const ALARM_NOTIFICATION_ID = "friday-morning-alarm";
const ALARM_CHANNEL_ID = "friday-alarm";

async function loadNotifee() {
  try {
    return await import("@notifee/react-native");
  } catch (error) {
    return null;
  }
}

export function parseAlarmTime(value) {
  const match = /^([01]?\d|2[0-3]):([0-5]\d)$/.exec(String(value || "").trim());
  if (!match) {
    return null;
  }
  return { hour: Number(match[1]), minute: Number(match[2]) };
}

export function nextOccurrence(hour, minute, now = new Date()) {
  const next = new Date(now);
  next.setHours(hour, minute, 0, 0);
  if (next.getTime() <= now.getTime()) {
    next.setDate(next.getDate() + 1);
  }
  return next;
}

export async function scheduleDailyAlarm(hour, minute) {
  const module = await loadNotifee();
  if (!module) {
    return { ok: false, reason: t("alarm.noModule") };
  }
  const notifee = module.default;
  const {
    AndroidCategory,
    AndroidImportance,
    AndroidVisibility,
    RepeatFrequency,
    TriggerType,
  } = module;

  const permission = await notifee.requestPermission();
  if (permission?.authorizationStatus != null && permission.authorizationStatus < 1) {
    return { ok: false, reason: t("alarm.noPermission") };
  }

  const channelId = await notifee.createChannel({
    id: ALARM_CHANNEL_ID,
    name: "Friday Wecker",
    importance: AndroidImportance.HIGH,
    visibility: AndroidVisibility.PUBLIC,
    sound: "default",
    vibration: true,
  });

  const next = nextOccurrence(hour, minute);
  await notifee.createTriggerNotification(
    {
      id: ALARM_NOTIFICATION_ID,
      title: t("alarm.notificationTitle"),
      body: t("alarm.notificationBody"),
      android: {
        channelId,
        category: AndroidCategory.ALARM,
        importance: AndroidImportance.HIGH,
        sound: "default",
        loopSound: true,
        fullScreenAction: { id: "default" },
        pressAction: { id: "alarm", launchActivity: "default" },
      },
      ios: {
        sound: "default",
        interruptionLevel: "timeSensitive",
      },
    },
    {
      type: TriggerType.TIMESTAMP,
      timestamp: next.getTime(),
      repeatFrequency: RepeatFrequency.DAILY,
      alarmManager: { allowWhileIdle: true },
    },
  );
  return { ok: true, nextAt: next.toISOString() };
}

export async function cancelDailyAlarm() {
  const module = await loadNotifee();
  if (!module) {
    return false;
  }
  await module.default.cancelTriggerNotification(ALARM_NOTIFICATION_ID);
  return true;
}

// Fetches today's briefing in the app language and speaks it.
// Returns the briefing payload so callers can show the text too.
export async function playMorningBriefing() {
  const data = await getVoiceMorningBriefing(getAppLocale(), true);
  if (data?.audio_base64) {
    await playBase64Wav(data.audio_base64, "friday-briefing.wav");
  }
  return data;
}

// Wire up: app opened from the alarm notification (cold start), alarm tapped
// while the app runs, or alarm delivered while the app is in the foreground.
export async function initAlarmHandlers(onAlarm) {
  const module = await loadNotifee();
  if (!module) {
    return () => {};
  }
  const notifee = module.default;
  const { EventType } = module;

  const initial = await notifee.getInitialNotification().catch(() => null);
  if (initial?.notification?.id === ALARM_NOTIFICATION_ID) {
    onAlarm();
  }

  return notifee.onForegroundEvent(({ type, detail }) => {
    if (detail?.notification?.id !== ALARM_NOTIFICATION_ID) {
      return;
    }
    if (type === EventType.PRESS || type === EventType.DELIVERED) {
      onAlarm();
    }
  });
}
