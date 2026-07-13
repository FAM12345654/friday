// Expo push registration for Friday reminders.
//
// Best-effort: if the user denies permission, the device is an emulator, or
// expo-notifications is not installed in the current build, the app keeps
// working without push.
import { Platform } from "react-native";

import { registerPushToken } from "./api/client";

export async function registerForPushNotifications() {
  let Notifications;
  try {
    // Dynamic import so development builds without the native module don't crash.
    Notifications = await import("expo-notifications");
  } catch (error) {
    return { ok: false, reason: "expo-notifications nicht verfügbar" };
  }

  try {
    const settings = await Notifications.getPermissionsAsync();
    let status = settings.status;
    if (status !== "granted") {
      const request = await Notifications.requestPermissionsAsync();
      status = request.status;
    }
    if (status !== "granted") {
      return { ok: false, reason: "Berechtigung abgelehnt" };
    }

    if (Platform.OS === "android") {
      await Notifications.setNotificationChannelAsync("friday-reminders", {
        name: "Friday Erinnerungen",
        importance: Notifications.AndroidImportance.DEFAULT,
      });
    }

    const tokenResponse = await Notifications.getExpoPushTokenAsync();
    const token = tokenResponse?.data;
    if (!token) {
      return { ok: false, reason: "Kein Token erhalten" };
    }

    await registerPushToken(token, Platform.OS);
    return { ok: true, token };
  } catch (error) {
    return { ok: false, reason: String(error?.message || error) };
  }
}
