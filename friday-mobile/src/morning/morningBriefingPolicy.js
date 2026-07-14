export const BRIEFING_FILE_PREFIX = "friday_briefing_";
export const BRIEFING_FILE_SUFFIX = ".mp3";
export const ALARM_REFRESH_INTERVAL_MS = 12 * 60 * 60 * 1000;

export function isBriefingFileName(name) {
  return name.startsWith(BRIEFING_FILE_PREFIX) && name.endsWith(BRIEFING_FILE_SUFFIX);
}

export function shouldRefreshMorningAlarm({
  force = false,
  lastCheckAt,
  alarmDate,
  targetDate,
  now = Date.now(),
}) {
  if (force || alarmDate !== targetDate) return true;
  const lastCheck = Date.parse(lastCheckAt || "");
  return !Number.isFinite(lastCheck) || now - lastCheck >= ALARM_REFRESH_INTERVAL_MS;
}

export function shouldAutoPlayMorningBriefing({ hour, playedDate, today, localUri }) {
  return hour >= 5 && hour < 10 && playedDate !== today && Boolean(localUri);
}

export function normalizeMorningAutomation({ status, skipDate, today }) {
  if (status === "skip_once" && skipDate && skipDate <= today) {
    return { status: "active", skipDate: null };
  }
  return { status, skipDate };
}

function fileNameFromUri(uri) {
  return String(uri).split(/[\\/]/).pop();
}

export async function promoteDownloadedBriefing({
  fileSystem,
  directory,
  tempUri,
  targetUri,
  backupUri,
}) {
  await fileSystem.deleteAsync(backupUri, { idempotent: true });
  const targetInfo = await fileSystem.getInfoAsync(targetUri);
  const targetWasBackedUp = Boolean(targetInfo.exists);
  if (targetWasBackedUp) {
    await fileSystem.moveAsync({ from: targetUri, to: backupUri });
  }

  try {
    await fileSystem.moveAsync({ from: tempUri, to: targetUri });
  } catch (error) {
    if (targetWasBackedUp) {
      await fileSystem.deleteAsync(targetUri, { idempotent: true });
      await fileSystem.moveAsync({ from: backupUri, to: targetUri });
    }
    throw error;
  }

  const targetName = fileNameFromUri(targetUri);
  const names = await fileSystem.readDirectoryAsync(directory).catch(() => []);
  for (const name of names) {
    if (isBriefingFileName(name) && name !== targetName) {
      await fileSystem.deleteAsync(`${directory}${name}`, { idempotent: true });
    }
  }
  await fileSystem.deleteAsync(backupUri, { idempotent: true });
  return targetUri;
}
