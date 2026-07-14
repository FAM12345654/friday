import { Audio } from "expo-av";
import Constants from "expo-constants";
import * as Device from "expo-device";
import * as FileSystem from "expo-file-system/legacy";
import * as Notifications from "expo-notifications";
import * as TaskManager from "expo-task-manager";
import { Platform } from "react-native";

import {
  getMorningBriefingAudioUrl,
  getMorningBriefingStatus,
  getMorningWakeTime,
  registerMorningBriefingPushToken,
} from "../api/client";
import {
  BRIEFING_FILE_PREFIX,
  BRIEFING_FILE_SUFFIX,
  isBriefingFileName,
  normalizeMorningAutomation,
  promoteDownloadedBriefing,
  shouldAutoPlayMorningBriefing,
  shouldRefreshMorningAlarm,
} from "./morningBriefingPolicy";
import { getMorningRoutineState, updateMorningRoutineState } from "./morningBriefingStore";

export const MORNING_PUSH_TASK = "friday-morning-briefing-push";
const DOWNLOAD_TEMP = "friday_briefing_download.tmp";
const DOWNLOAD_BACKUP = "friday_briefing_previous.tmp";
const MAX_FILE_AGE_MS = 24 * 60 * 60 * 1000;

let activeSound = null;

const dateOnly = (value = new Date()) => {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

const tomorrowDate = () => {
  const value = new Date();
  value.setDate(value.getDate() + 1);
  return dateOnly(value);
};

const briefingDirectory = () => FileSystem.documentDirectory;
const briefingUri = (date) => `${briefingDirectory()}${BRIEFING_FILE_PREFIX}${date}${BRIEFING_FILE_SUFFIX}`;

async function fileExists(uri) {
  if (!uri) return false;
  return Boolean((await FileSystem.getInfoAsync(uri)).exists);
}

export async function cleanupExpiredMorningBriefings(now = Date.now()) {
  const directory = briefingDirectory();
  if (!directory) return getMorningRoutineState();
  const names = await FileSystem.readDirectoryAsync(directory).catch(() => []);
  let state = await getMorningRoutineState();
  for (const name of names.filter(isBriefingFileName)) {
    const uri = `${directory}${name}`;
    const info = await FileSystem.getInfoAsync(uri);
    const modifiedAt = Number(info.modificationTime || 0) * 1000;
    if (modifiedAt && now - modifiedAt > MAX_FILE_AGE_MS) {
      await FileSystem.deleteAsync(uri, { idempotent: true });
      if (state?.local_uri === uri) {
        state = await updateMorningRoutineState({
          briefing_date: null,
          local_uri: null,
          downloaded_at: null,
        });
      }
    }
  }
  return state;
}

export async function downloadLatestMorningBriefing(statusOverride = null) {
  const directory = briefingDirectory();
  if (!directory) throw new Error("Lokaler Briefing-Speicher ist nicht verfügbar.");
  const status = statusOverride || (await getMorningBriefingStatus());
  const state = await getMorningRoutineState();
  if (!status?.success || !status?.date) {
    return updateMorningRoutineState({ last_error: status?.error || "Kein Briefing verfügbar." });
  }
  if (state?.briefing_date === status.date && (await fileExists(state.local_uri))) {
    return updateMorningRoutineState({ last_check_at: new Date().toISOString(), last_error: null });
  }

  const tempUri = `${directory}${DOWNLOAD_TEMP}`;
  const backupUri = `${directory}${DOWNLOAD_BACKUP}`;
  const targetUri = briefingUri(status.date);
  try {
    await FileSystem.deleteAsync(tempUri, { idempotent: true });
    const result = await FileSystem.downloadAsync(await getMorningBriefingAudioUrl(), tempUri);
    if (result.status < 200 || result.status >= 300) {
      throw new Error(`Audio-Download fehlgeschlagen: HTTP ${result.status}`);
    }
    const info = await FileSystem.getInfoAsync(tempUri);
    if (!info.exists || Number(info.size || 0) <= 0) {
      throw new Error("Heruntergeladene Briefing-Datei ist leer.");
    }

    await promoteDownloadedBriefing({
      fileSystem: FileSystem,
      directory,
      tempUri,
      targetUri,
      backupUri,
    });
    return updateMorningRoutineState({
      briefing_date: status.date,
      local_uri: targetUri,
      downloaded_at: new Date().toISOString(),
      last_check_at: new Date().toISOString(),
      last_error: null,
    });
  } catch (error) {
    await FileSystem.deleteAsync(tempUri, { idempotent: true }).catch(() => null);
    return updateMorningRoutineState({
      last_check_at: new Date().toISOString(),
      last_error: String(error?.message || error),
    });
  }
}

async function ensureNotificationPermission() {
  if (Platform.OS === "web") return false;
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("friday-morning", {
      name: "Friday Morning Routine",
      importance: Notifications.AndroidImportance.HIGH,
      sound: "default",
      vibrationPattern: [0, 250, 250, 250],
    });
  }
  let permission = await Notifications.getPermissionsAsync();
  if (permission.status !== "granted") {
    permission = await Notifications.requestPermissionsAsync();
  }
  return permission.status === "granted";
}

export async function registerMorningPush() {
  if (Platform.OS === "web" || !Device.isDevice) {
    return { registered: false, message: "Push benötigt ein echtes Gerät." };
  }
  if (!(await ensureNotificationPermission())) {
    return { registered: false, message: "Benachrichtigungs-Berechtigung fehlt." };
  }
  const projectId = Constants.expoConfig?.extra?.eas?.projectId || Constants.easConfig?.projectId;
  if (!projectId) {
    return { registered: false, message: "Expo-Projekt-ID fehlt." };
  }
  const token = (await Notifications.getExpoPushTokenAsync({ projectId })).data;
  await registerMorningBriefingPushToken(token);
  if (!(await TaskManager.isTaskRegisteredAsync(MORNING_PUSH_TASK))) {
    await Notifications.registerTaskAsync(MORNING_PUSH_TASK);
  }
  return { registered: true, message: "Morning-Briefing-Push ist registriert." };
}

async function cancelStoredAlarm(state) {
  if (state?.alarm_notification_id) {
    await Notifications.cancelScheduledNotificationAsync(state.alarm_notification_id).catch(() => null);
  }
}

export async function refreshMorningAlarm(force = false) {
  let state = await getMorningRoutineState();
  const today = dateOnly();
  const targetDate = tomorrowDate();
  const automation = normalizeMorningAutomation({
    status: state?.automation_status,
    skipDate: state?.skip_date,
    today,
  });
  if (automation.status !== state?.automation_status || automation.skipDate !== state?.skip_date) {
    state = await updateMorningRoutineState({
      automation_status: automation.status,
      skip_date: automation.skipDate,
    });
  }
  if (state?.automation_status === "paused") {
    await cancelStoredAlarm(state);
    return updateMorningRoutineState({ alarm_notification_id: null, alarm_reason: "Automatik pausiert" });
  }
  if (state?.automation_status === "skip_once" && state.skip_date === targetDate) {
    await cancelStoredAlarm(state);
    return updateMorningRoutineState({
      alarm_notification_id: null,
      alarm_date: targetDate,
      alarm_reason: "Morgen wird einmalig übersprungen",
    });
  }
  if (!shouldRefreshMorningAlarm({
    force,
    lastCheckAt: state?.last_check_at,
    alarmDate: state?.alarm_date,
    targetDate,
  })) {
    return state;
  }

  let wakeTime = { alarm_time: "07:00:00", reason: "Backend nicht erreichbar - lokaler Fallback um 07:00" };
  try {
    wakeTime = await getMorningWakeTime(targetDate);
  } catch (error) {
    wakeTime.reason = `Backend nicht erreichbar - lokaler Fallback um 07:00 (${String(error?.message || error)})`;
  }
  if (!(await ensureNotificationPermission())) {
    return updateMorningRoutineState({ last_error: "Benachrichtigungs-Berechtigung fehlt." });
  }
  const alarmDate = new Date(`${targetDate}T${String(wakeTime.alarm_time || "07:00").slice(0, 5)}:00`);
  await cancelStoredAlarm(state);
  const notificationId = await Notifications.scheduleNotificationAsync({
    content: {
      title: "Friday",
      body: `Guten Morgen. ${wakeTime.reason}`,
      sound: "default",
      data: { type: "morning_alarm", date: targetDate },
    },
    trigger: {
      type: Notifications.SchedulableTriggerInputTypes?.DATE || "date",
      date: alarmDate,
      channelId: Platform.OS === "android" ? "friday-morning" : undefined,
    },
  });
  return updateMorningRoutineState({
    alarm_notification_id: notificationId,
    alarm_date: targetDate,
    alarm_time: String(wakeTime.alarm_time || "07:00").slice(0, 5),
    alarm_reason: wakeTime.reason,
    last_check_at: new Date().toISOString(),
    last_error: null,
  });
}

export async function setMorningAutomationStatus(status) {
  if (!["active", "skip_once", "paused"].includes(status)) {
    throw new Error("Ungültiger Morning-Routine-Status.");
  }
  const state = await getMorningRoutineState();
  await cancelStoredAlarm(state);
  await updateMorningRoutineState({
    automation_status: status,
    skip_date: status === "skip_once" ? tomorrowDate() : null,
    alarm_notification_id: null,
  });
  return refreshMorningAlarm(true);
}

export async function playMorningBriefing({ force = false, onFinished = null } = {}) {
  const state = await getMorningRoutineState();
  const today = dateOnly();
  const hour = new Date().getHours();
  if (!force && !shouldAutoPlayMorningBriefing({
    hour,
    playedDate: state?.played_date,
    today,
    localUri: state?.local_uri,
  })) {
    return { played: false, state };
  }
  if (!(await fileExists(state?.local_uri))) {
    return { played: false, state: await updateMorningRoutineState({ last_error: "Keine lokale Briefing-Datei vorhanden." }) };
  }
  await stopMorningBriefing();
  await Audio.setAudioModeAsync({ playsInSilentModeIOS: true, shouldDuckAndroid: true });
  const { sound } = await Audio.Sound.createAsync({ uri: state.local_uri }, { shouldPlay: true });
  activeSound = sound;
  await updateMorningRoutineState({ played_date: today, last_error: null });
  sound.setOnPlaybackStatusUpdate((status) => {
    if (status.isLoaded && status.didJustFinish) {
      stopMorningBriefing().finally(() => onFinished?.());
    }
  });
  return { played: true, state: await getMorningRoutineState() };
}

export async function stopMorningBriefing() {
  if (!activeSound) return;
  const sound = activeSound;
  activeSound = null;
  await sound.stopAsync().catch(() => null);
  await sound.unloadAsync().catch(() => null);
}

export async function initializeMorningBriefing() {
  await cleanupExpiredMorningBriefings();
  const push = await registerMorningPush().catch((error) => ({
    registered: false,
    message: String(error?.message || error),
  }));
  let state = await downloadLatestMorningBriefing().catch(() => getMorningRoutineState());
  state = await refreshMorningAlarm().catch(() => state);
  const hour = new Date().getHours();
  return {
    state,
    push,
    shouldAutoPlay: shouldAutoPlayMorningBriefing({
      hour,
      playedDate: state?.played_date,
      today: dateOnly(),
      localUri: state?.local_uri,
    }),
  };
}

export function subscribeMorningBriefingEvents(onUpdate, onAlarm) {
  if (Platform.OS === "web") return () => {};
  const received = Notifications.addNotificationReceivedListener(async (notification) => {
    const data = notification?.request?.content?.data || {};
    if (data.type === "morning_briefing_ready") {
      onUpdate?.(await downloadLatestMorningBriefing());
    }
  });
  const response = Notifications.addNotificationResponseReceivedListener(async (event) => {
    const data = event?.notification?.request?.content?.data || {};
    if (data.type === "morning_alarm") {
      onAlarm?.();
    }
  });
  return () => {
    received.remove();
    response.remove();
  };
}

if (Platform.OS !== "web" && !TaskManager.isTaskDefined(MORNING_PUSH_TASK)) {
  TaskManager.defineTask(MORNING_PUSH_TASK, async ({ data, error }) => {
    if (error) return;
    const notificationData = data?.notification?.request?.content?.data || data?.data || data || {};
    if (notificationData.type === "morning_briefing_ready") {
      await downloadLatestMorningBriefing();
    }
  });
}
