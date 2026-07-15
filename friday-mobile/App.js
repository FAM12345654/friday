import React, { useEffect, useRef, useState } from "react";
import { useFonts } from "expo-font";
import * as SplashScreen from "expo-splash-screen";
import * as Updates from "expo-updates";
import {
  ActivityIndicator,
  AppState,
  Linking,
  Modal,
  Platform,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  useColorScheme,
  View,
} from "react-native";
import Svg, { Circle, Line, Path, Polyline } from "react-native-svg";
import {
  cacheTypes,
  enqueueOfflineWrite,
  flushWriteQueue,
  formatSyncTime,
  getSyncStatus,
  readThroughCache,
  setSyncStatus as persistSyncStatus,
  writeLocalCacheEntry,
} from "./src/data/sync";
import { registerForPushNotifications } from "./src/notifications";
import { SUPPORTED_LOCALES, getAppLocale, initLocale, setAppLocale, t } from "./src/i18n";
import PushToTalk from "./src/voice/PushToTalk";
import AlarmSettings from "./src/alarm/AlarmSettings";
import { initAlarmHandlers, playMorningBriefing, restoreScheduledAlarm } from "./src/alarm/alarm";
import { subscribeLiveEvents } from "./src/data/liveEvents";
import { groupInboxItems } from "./src/inboxGrouping";

import {
  approveMessageSuggestion,
  approveTaskSuggestion,
  archiveTask,
  answerLearningQuestion,
  buildTaskForwardDraft,
  checkHealth,
  completeTask,
  activateMailOrganize,
  connectEmailAccount,
  connectImapMailAccount,
  connectMsMailAccount,
  createAccountPolicy,
  createCalendarEventFromMessage,
  createContact,
  createTask,
  deleteCalendarEvent,
  deleteImapMailAccount,
  deleteMsMailAccount,
  deleteTask,
  dismissLearningQuestion,
  getAccountPolicies,
  getCalendarAccountStatus,
  getEmailAccountStatus,
  getEmailInbox,
  getImapMailStatus,
  generateCalendarEventSuggestionForMessage,
  getWhatsAppMessages,
  getWhatsAppAgentNotes,
  getWhatsAppStatus,
  generateTaskSuggestionsForMessage,
  getApiUrl,
  getApiTokenStatus,
  getCalendar,
  getGoogleCalendarReadPreview,
  getCalendarViewPrefs,
  getContacts,
  getDashboard,
  getLearning,
  getMailOrganizeLog,
  getBlockedSenders,
  getMessageSuggestion,
  getMessageSuggestions,
  getMessages,
  getMsMailStatus,
  getPrivacy,
  getSetupStatus,
  getTasks,
  getUnifiedMailMessage,
  getUnifiedMailMessages,
  checkCalendarActivationGate,
  activateImapMailRead,
  activateMsMailRead,
  runMailOrganize,
  snoozeTask,
  syncImapMailMessages,
  syncMsMailMessages,
  syncWorkdaysToGoogle,
  markMessageSpam,
  sendTaskForwardEmail,
  saveApiToken,
  testEmailAccountConnection,
  unblockSender,
  rejectMessageSuggestion,
  rejectTaskSuggestion,
  updateContact,
  updateCalendarViewPrefs,
  updateEmailAgentNotes,
  updateLearnedRule,
  undoMailOrganize,
  updateWhatsAppAgentNotes,
} from "./src/api/client";

SplashScreen.preventAutoHideAsync().catch(() => {});

const bottomTabs = [
  { key: "Home", label: "Home", icon: "home" },
  { key: "Kalender", label: "Termine", icon: "calendar" },
  { key: "Tasks", label: "Aufgaben", icon: "check" },
  { key: "Nachrichten", label: "Posteingang", icon: "mail" },
  { key: "Mehr", label: "Mehr", icon: "more" },
];

const moreScreens = [
  { key: "Kontakte", label: "Kontakte", description: "Personen, Kunden und Notizen", icon: "contacts" },
  { key: "Lernen", label: "Lernen", description: "Offene Fragen und gelernte Regeln", icon: "learning" },
  { key: "Setup", label: "Einrichten", description: "Konten, lokale KI und Verbindungen", icon: "settings" },
  { key: "Datenschutz", label: "Datenschutz", description: "Safety-Status und lokale Grenzen", icon: "privacy" },
  { key: "Spam", label: "Spam / Blockiert", description: "Lokal blockierte Absender", icon: "alert" },
];

const lightColors = {
  bg: "#f6f1e4",
  bgWash: "#efe3ce",
  surface: "#fdfaf1",
  card: "#fbf7ec",
  cardStrong: "#fdfaf1",
  line: "#e7dfca",
  border: "#e7dfca",
  accent: "#5c7150",
  accentStrong: "#36442e",
  accentSoft: "#e9eddd",
  sage: "#7d9270",
  moss: "#5c7150",
  leaf: "#9aaa7f",
  deep: "#36442e",
  text: "#2e3627",
  textSoft: "#84907b",
  muted: "#9a927f",
  success: "#5f7f52",
  warn: "#b8924a",
  danger: "#bb6b58",
  clay: "#bb6b58",
  gold: "#b8924a",
  cream: "#f6f1e4",
  white: "#fdfaf1",
  buttonSolidText: "#f6f1e4",
  buttonLightText: "#36442e",
  buttonGhostBg: "#e9eddd",
  buttonGhostText: "#36442e",
  onAccent: "#f6f1e4",
};

const darkColors = {
  bg: "#1c241a",
  bgWash: "#182017",
  surface: "#232c1f",
  card: "#273322",
  cardStrong: "#2f3a29",
  line: "#3a4633",
  border: "#3a4633",
  accent: "#9aaa7f",
  accentStrong: "#d9e4c8",
  accentSoft: "#34412f",
  sage: "#b6c99f",
  moss: "#9aaa7f",
  leaf: "#b6c99f",
  deep: "#f1ede0",
  text: "#f1ede0",
  textSoft: "#b9c4ae",
  muted: "#9ca894",
  success: "#9dbd86",
  warn: "#d1ab62",
  danger: "#d98973",
  clay: "#d98973",
  gold: "#d1ab62",
  cream: "#f1ede0",
  white: "#273322",
  buttonSolidText: "#36442e",
  buttonLightText: "#36442e",
  buttonGhostBg: "#d9e4c8",
  buttonGhostText: "#36442e",
  onAccent: "#36442e",
};

let colors = lightColors;

const figtreeFonts = {
  Figtree_400Regular: require("@expo-google-fonts/figtree/400Regular/Figtree_400Regular.ttf"),
  Figtree_500Medium: require("@expo-google-fonts/figtree/500Medium/Figtree_500Medium.ttf"),
  Figtree_600SemiBold: require("@expo-google-fonts/figtree/600SemiBold/Figtree_600SemiBold.ttf"),
  Figtree_700Bold: require("@expo-google-fonts/figtree/700Bold/Figtree_700Bold.ttf"),
  Figtree_800ExtraBold: require("@expo-google-fonts/figtree/800ExtraBold/Figtree_800ExtraBold.ttf"),
};

const defaultTextStyle = { fontFamily: "Figtree_400Regular" };
Text.defaultProps = Text.defaultProps || {};
Text.defaultProps.style = [defaultTextStyle, Text.defaultProps.style].filter(Boolean);
TextInput.defaultProps = TextInput.defaultProps || {};
TextInput.defaultProps.style = [defaultTextStyle, TextInput.defaultProps.style].filter(Boolean);

const fontFamilyForWeight = (fontWeight) => {
  const weight = Number(String(fontWeight || "400").replace(/\D/g, "")) || 400;
  if (weight >= 800) return "Figtree_800ExtraBold";
  if (weight >= 700) return "Figtree_700Bold";
  if (weight >= 600) return "Figtree_600SemiBold";
  if (weight >= 500) return "Figtree_500Medium";
  return "Figtree_400Regular";
};

const withFigtreeFonts = (styleMap) =>
  Object.fromEntries(
    Object.entries(styleMap).map(([key, value]) => {
      if (!value || typeof value !== "object" || Array.isArray(value)) {
        return [key, value];
      }
      const isTextStyle =
        Object.prototype.hasOwnProperty.call(value, "fontSize") ||
        Object.prototype.hasOwnProperty.call(value, "fontWeight") ||
        key.toLowerCase().includes("text") ||
        key.toLowerCase().includes("label") ||
        key.toLowerCase().includes("title") ||
        key.toLowerCase().includes("heading") ||
        key.toLowerCase().includes("body") ||
        key.toLowerCase().includes("meta");
      if (!isTextStyle) {
        return [key, value];
      }
      const numericWeight = Number(String(value.fontWeight || "400").replace(/\D/g, "")) || 400;
      const normalizedWeight =
        numericWeight >= 800
          ? "800"
          : numericWeight >= 700
            ? "700"
            : numericWeight >= 600
              ? "600"
              : numericWeight >= 500
                ? "500"
                : "400";
      return [
        key,
        {
          ...value,
          fontWeight: normalizedWeight,
          fontFamily: fontFamilyForWeight(value.fontWeight),
        },
      ];
    }),
  );

const createSoftShadow = (theme) => ({
  shadowColor: theme.deep,
  shadowOffset: { width: 0, height: 3 },
  shadowOpacity: 0.06,
  shadowRadius: 16,
  elevation: 2,
});

const formatDate = (value) => {
  if (!value) {
    return "";
  }
  return String(value);
};

const padDatePart = (value) => String(value).padStart(2, "0");

const formatTimezoneOffset = (date) => {
  const offset = -date.getTimezoneOffset();
  const sign = offset >= 0 ? "+" : "-";
  const absolute = Math.abs(offset);
  const hours = padDatePart(Math.floor(absolute / 60));
  const minutes = padDatePart(absolute % 60);
  return `${sign}${hours}:${minutes}`;
};

const formatLocalDateTime = (date) => {
  const year = date.getFullYear();
  const month = padDatePart(date.getMonth() + 1);
  const day = padDatePart(date.getDate());
  const hours = padDatePart(date.getHours());
  const minutes = padDatePart(date.getMinutes());
  const seconds = padDatePart(date.getSeconds());
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}${formatTimezoneOffset(date)}`;
};

const buildGoogleCalendarRange = (days = 14) => {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
  const end = new Date(start);
  end.setDate(start.getDate() + days);
  return {
    rangeStart: formatLocalDateTime(start),
    rangeEnd: formatLocalDateTime(end),
  };
};

const formatDateOnly = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

const addDays = (date, days) => {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
};

// Wochenkalender-Helfer: Stunden aus "HH:MM" oder ISO-Zeiten robust ableiten.
const extractHourValue = (value) => {
  const match = String(value || "").match(/(\d{1,2}):(\d{2})/);
  if (!match) {
    return null;
  }
  return Number(match[1]) + Number(match[2]) / 60;
};

const eventDurationHours = (entry) => {
  const start = extractHourValue(entry?.start || entry?.start_time);
  const end = extractHourValue(entry?.end || entry?.end_time);
  if (start === null || end === null) {
    return 0;
  }
  const diff = end - start;
  return diff > 0 ? diff : 0;
};

const eventDateKey = (entry) => {
  const explicit = String(entry?.date || "").slice(0, 10);
  if (/^\d{4}-\d{2}-\d{2}$/.test(explicit)) {
    return explicit;
  }
  const fromStart = String(entry?.start || "").slice(0, 10);
  if (/^\d{4}-\d{2}-\d{2}$/.test(fromStart)) {
    return fromStart;
  }
  return "";
};

const eventTimeLabel = (entry) => {
  const match = String(entry?.start || entry?.start_time || "").match(/(\d{1,2}:\d{2})/);
  return match ? match[1] : "";
};

const formatHoursLabel = (hours) => {
  const rounded = Math.round(Number(hours || 0) * 10) / 10;
  return `${String(rounded).replace(".", ",")} h`;
};

// Rollierendes Wochenfenster: heute + 7 Tage einschließlich (Mi -> nächster Mi).
const buildWeekDays = (calendarPayload, googlePreview) => {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const events = [
    ...isArray(calendarPayload?.merged_items || calendarPayload?.items || calendarPayload?.calendar_items || []),
    ...isArray(googlePreview?.events),
  ];
  const seen = new Set();
  const byDay = {};
  events.forEach((entry) => {
    const key = eventDateKey(entry);
    if (!key) {
      return;
    }
    const dedupKey = `${key}|${String(entry?.title || "").trim().toLowerCase()}|${extractHourValue(entry?.start)}`;
    if (seen.has(dedupKey)) {
      return;
    }
    seen.add(dedupKey);
    if (!byDay[key]) {
      byDay[key] = [];
    }
    byDay[key].push(entry);
  });
  return Array.from({ length: 8 }, (_, index) => {
    const day = addDays(start, index);
    const key = formatDateOnly(day);
    const dayEvents = (byDay[key] || [])
      .slice()
      .sort((a, b) => (extractHourValue(a?.start) ?? 0) - (extractHourValue(b?.start) ?? 0));
    const hours = dayEvents.reduce((sum, entry) => sum + eventDurationHours(entry), 0);
    return { key, date: day, events: dayEvents, hours };
  });
};

const weekdayLabel = (date) =>
  date.toLocaleDateString("de-DE", { weekday: "short" }).replace(".", "");

const shortDateLabel = (date) =>
  `${padDatePart(date.getDate())}.${padDatePart(date.getMonth() + 1)}.`;

const defaultCalendarViewPrefs = {
  range_preset: "heute",
  custom_from: "",
  custom_to: "",
  day_start: "00:00",
  day_end: "23:59",
};

const resolveCalendarViewQuery = (prefs = defaultCalendarViewPrefs) => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
  const preset = prefs?.range_preset || "heute";
  const dayStart = prefs?.day_start || "00:00";
  const dayEnd = prefs?.day_end || "23:59";

  if (preset === "7tage") {
    return {
      range_start: formatDateOnly(today),
      range_end: formatDateOnly(addDays(today, 6)),
      day_start: dayStart,
      day_end: dayEnd,
    };
  }
  if (preset === "30tage") {
    return {
      range_start: formatDateOnly(today),
      range_end: formatDateOnly(addDays(today, 29)),
      day_start: dayStart,
      day_end: dayEnd,
    };
  }
  if (preset === "custom") {
    return {
      range_start: prefs?.custom_from || formatDateOnly(today),
      range_end: prefs?.custom_to || prefs?.custom_from || formatDateOnly(today),
      day_start: dayStart,
      day_end: dayEnd,
    };
  }
  return {
    range_start: formatDateOnly(today),
    range_end: formatDateOnly(today),
    day_start: dayStart,
    day_end: dayEnd,
  };
};

const calendarRangeLabel = (calendar) => {
  if (!calendar?.range_start && !calendar?.date) {
    return "-";
  }
  if (calendar?.range_start && calendar?.range_end && calendar.range_start !== calendar.range_end) {
    return `${calendar.range_start} bis ${calendar.range_end}`;
  }
  return calendar?.date || calendar?.range_start || "-";
};

const formatCalendarMoment = (value) => {
  if (!value) {
    return "?";
  }
  return String(value).replace("T", " ").slice(0, 16);
};

const isArray = (value) => (Array.isArray(value) ? value : []);

const toPriorityLabel = (value) => (value ? String(value).trim() || "normal" : "normal");

const priorityColor = (value) => {
  const label = toPriorityLabel(value).toLowerCase();
  if (label === "hoch" || label === "high") {
    return colors.danger;
  }
  if (label === "mittel" || label === "medium" || label === "normal") {
    return colors.warn;
  }
  return colors.success;
};

const normalizeApiError = (error) => {
  if (!error || !error.message) {
    return "Unbekannter Fehler";
  }
  return String(error.message);
};

const channelLabel = (channel) => (channel === "whatsapp" ? "WhatsApp" : "E-Mail");

const approvalTokenFor = (channel) =>
  channel === "whatsapp" ? "WHATSAPP SENDEN" : "EMAIL SENDEN";

const hasForwardTarget = (contact, channel) =>
  channel === "whatsapp"
    ? Boolean(contact?.whatsapp_target)
    : Boolean(contact?.email_address);

const spamMessageRef = (message) => {
  if (message?.source === "ms_mail") {
    return message.ms_mail_local_id || Math.max(0, Number(message.id || 0) - 3000000);
  }
  if (message?.source === "imap_mail") {
    return message.ms_mail_local_id || Math.max(0, Number(message.id || 0) - 3000000);
  }
  if (message?.source === "whatsapp") {
    return message.whatsapp_message_id || Math.max(0, Number(message.id || 0) - 900000000);
  }
  return message?.id;
};

const msMailRelevanceLabel = (reason) => {
  const labels = {
    personal_mailbox: "persoenliches Postfach",
    recipient: "an dich",
    name: "Philip erwaehnt",
    team: "Team",
    betreuer: "Kunde: Philip",
    noise: "Rauschen",
    unsicher: "unsicher",
    not_relevant: "nicht relevant",
    philip_trigger: "Philip erwaehnt",
    team_all_partners: "Team",
    customer_betreuer_philip: "Kunde: Philip",
    ai_unavailable_conservative_include: "unsicher",
    office_not_relevant: "nicht relevant",
  };
  if (reason && !labels[reason]) {
    return `lokal: ${reason}`;
  }
  return labels[reason] || "Relevanz lokal";
};

const msMailRecipientsText = (detail) => {
  const recipients = Array.isArray(detail?.recipients_list) ? detail.recipients_list : [];
  if (!recipients.length) {
    return "-";
  }
  return recipients.map((item) => item.label || item.address || item.name || "-").join(", ");
};

const contactTypeOptions = [
  { value: "arbeit", label: "Arbeit" },
  { value: "freund", label: "Freund" },
  { value: "familie", label: "Familie" },
  { value: "kunde", label: "Kunde" },
  { value: "sonstiges", label: "Sonstiges" },
];

const betreuerOptions = [
  { value: "flo", label: "Flo" },
  { value: "philip", label: "Philip" },
  { value: "alex", label: "Alex" },
];

const betreuerLabel = (value) =>
  betreuerOptions.find((item) => item.value === value)?.label || value || "-";

const normalizeLookup = (value) =>
  String(value || "").trim().toLowerCase().replace(/\s+/g, " ");

const normalizePhoneLookup = (value) => String(value || "").replace(/\D+/g, "");

const senderHasContact = (sender, contacts) => {
  const normalizedSender = normalizeLookup(sender);
  const senderPhone = normalizePhoneLookup(sender);
  if (!normalizedSender && senderPhone.length < 5) {
    return false;
  }
  return contacts.some((contact) => {
    const values = [
      normalizeLookup(contact.name),
      normalizeLookup(contact.email_address),
      normalizeLookup(contact.whatsapp_target),
    ];
    const phoneValues = [
      normalizePhoneLookup(contact.email_address),
      normalizePhoneLookup(contact.whatsapp_target),
    ];
    return values.includes(normalizedSender) || (senderPhone.length >= 5 && phoneValues.includes(senderPhone));
  });
};

const buildForwardDraft = (task, contact, channel) => {
  const contactName = contact?.name || "du";
  const target =
    channel === "whatsapp"
      ? contact?.whatsapp_target || "WhatsApp-Ziel noch nicht gespeichert"
      : contact?.email_address || "E-Mail-Adresse noch nicht gespeichert";
  const title = task?.title || "diese Aufgabe";
  const due = task?.due_date ? `\nFällig: ${task.due_date}` : "";
  const notes = task?.notes ? `\nHinweis: ${task.notes}` : "";
  return [
    `Hallo ${contactName},`,
    "",
    `kannst du bitte die Aufgabe "${title}" übernehmen?${due}${notes}`,
    "",
    "Danke dir!",
    "",
    `Kanal: ${channelLabel(channel)}`,
    `Ziel: ${target}`,
    "KI-Draft: lokaler Fallback.",
    "Noch nicht gesendet.",
  ].join("\n");
};

const greeting = () => {
  const hour = new Date().getHours();
  if (hour < 5) {
    return "Gute Nacht";
  }
  if (hour < 11) {
    return "Guten Morgen";
  }
  if (hour < 18) {
    return "Guten Tag";
  }
  return "Guten Abend";
};

const todayLabel = () =>
  new Date().toLocaleDateString("de-DE", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

function LineIcon({ name, size = 21, color = colors.muted }) {
  const common = {
    stroke: color,
    strokeWidth: 2,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    fill: "none",
  };
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" accessibilityRole="image">
      {name === "home" && (
        <>
          <Path d="M3 11.5 12 4l9 7.5" {...common} />
          <Path d="M5.5 10.5V20h13v-9.5" {...common} />
          <Path d="M9.5 20v-5h5v5" {...common} />
        </>
      )}
      {name === "calendar" && (
        <>
          <Path d="M5 5h14a2 2 0 0 1 2 2v12H3V7a2 2 0 0 1 2-2Z" {...common} />
          <Line x1="8" y1="3" x2="8" y2="7" {...common} />
          <Line x1="16" y1="3" x2="16" y2="7" {...common} />
          <Line x1="3" y1="10" x2="21" y2="10" {...common} />
        </>
      )}
      {name === "check" && <Polyline points="5 12.5 10 17.5 19 7" {...common} />}
      {name === "mail" && (
        <>
          <Path d="M4 6h16v12H4Z" {...common} />
          <Path d="m4 7 8 6 8-6" {...common} />
        </>
      )}
      {name === "more" && (
        <>
          <Circle cx="6" cy="12" r="1.4" fill={color} />
          <Circle cx="12" cy="12" r="1.4" fill={color} />
          <Circle cx="18" cy="12" r="1.4" fill={color} />
        </>
      )}
      {name === "contacts" && (
        <>
          <Circle cx="9" cy="8" r="3" {...common} />
          <Path d="M3.5 20a5.5 5.5 0 0 1 11 0" {...common} />
          <Path d="M17 9a2.5 2.5 0 0 1 0 5" {...common} />
          <Path d="M18.5 20a4 4 0 0 0-2.5-3.7" {...common} />
        </>
      )}
      {name === "learning" && (
        <>
          <Path d="M6 4h9.5A2.5 2.5 0 0 1 18 6.5V20H7a3 3 0 0 1-3-3V6a2 2 0 0 1 2-2Z" {...common} />
          <Path d="M8 8h6" {...common} />
          <Path d="M8 12h5" {...common} />
        </>
      )}
      {name === "settings" && (
        <>
          <Circle cx="12" cy="12" r="3" {...common} />
          <Path d="M19.4 15a8.2 8.2 0 0 0 .1-6l-2.1-.4-1-1.7.7-2A8.2 8.2 0 0 0 11 3l-1.3 1.6H7.8L6.5 3.1A8.2 8.2 0 0 0 3.4 8l1.3 1.6-.1 1.9L3.2 13a8.2 8.2 0 0 0 3 5.3l2-.7 1.7 1 .4 2.1a8.2 8.2 0 0 0 6-1l-.4-2.2 1-1.6Z" {...common} />
        </>
      )}
      {name === "privacy" && (
        <>
          <Path d="M12 3 19 6v5c0 4.5-2.8 7.7-7 10-4.2-2.3-7-5.5-7-10V6Z" {...common} />
          <Path d="m9 12 2 2 4-5" {...common} />
        </>
      )}
      {name === "alert" && (
        <>
          <Path d="M12 4 21 20H3Z" {...common} />
          <Line x1="12" y1="9" x2="12" y2="13" {...common} />
          <Circle cx="12" cy="17" r="1" fill={color} />
        </>
      )}
      {name === "lightbulb" && (
        <>
          <Path d="M9 18h6" {...common} />
          <Path d="M10 22h4" {...common} />
          <Path d="M8 14a6 6 0 1 1 8 0c-.8.7-1 1.5-1 2H9c0-.5-.2-1.3-1-2Z" {...common} />
        </>
      )}
      {name === "clock" && (
        <>
          <Circle cx="12" cy="12" r="8" {...common} />
          <Path d="M12 8v5l3 2" {...common} />
        </>
      )}
    </Svg>
  );
}

function ToggleSwitch({ enabled }) {
  return (
    <View style={[styles.toggleSwitch, enabled && styles.toggleSwitchOn]}>
      <View style={[styles.toggleKnob, enabled && styles.toggleKnobOn]} />
    </View>
  );
}

function PrivacyStatusPill({ active, inactiveLabel = "AUS" }) {
  const label = active ? "AKTIV" : inactiveLabel;
  return (
    <View style={[styles.privacyStatusPill, active && styles.privacyStatusPillWarn]}>
      <Text style={[styles.privacyStatusText, active && styles.privacyStatusTextWarn]}>{label}</Text>
    </View>
  );
}

function ListRow({ children, style }) {
  return <View style={[styles.listRow, style]}>{children}</View>;
}


// Konzept A "Kompasspunkt": Ring + Mittelpunkt + Orbit-Punkt (siehe assets/icon.png).
function LogoMark({ size = 48 }) {
  const scale = size / 48;
  const ring = 32 * scale;
  const ringBorder = Math.max(2, 3.4 * scale);
  const core = 9 * scale;
  const orbit = 8.5 * scale;
  const center = size / 2;
  const diag = (ring / 2) * 0.707; // 45°-Position oben rechts auf dem Ring
  return (
    <View style={[styles.logoMark, { width: size, height: size, borderRadius: 17 * scale }]}>
      <View
        style={{
          width: ring,
          height: ring,
          borderRadius: ring / 2,
          borderWidth: ringBorder,
          borderColor: colors.onAccent,
          backgroundColor: "transparent",
        }}
      />
      <View
        style={{
          position: "absolute",
          width: core,
          height: core,
          borderRadius: core / 2,
          backgroundColor: colors.onAccent,
          left: center - core / 2,
          top: center - core / 2,
        }}
      />
      <View
        style={{
          position: "absolute",
          width: orbit,
          height: orbit,
          borderRadius: orbit / 2,
          backgroundColor: colors.onAccent,
          left: center + diag - orbit / 2,
          top: center - diag - orbit / 2,
        }}
      />
    </View>
  );
}

function ActionButton({ label, onPress, disabled, variant = "primary", small }) {
  const variantStyle =
    variant === "danger"
      ? styles.buttonDanger
      : variant === "ghost"
        ? styles.buttonGhost
        : variant === "success"
          ? styles.buttonSuccess
          : variant === "light"
            ? styles.buttonLight
            : styles.buttonPrimary;
  const textStyle =
    variant === "ghost"
      ? styles.buttonGhostText
      : variant === "light"
        ? styles.buttonLightText
        : styles.buttonText;
  return (
    <TouchableOpacity
      style={[styles.button, variantStyle, small && styles.buttonSmall, disabled && styles.buttonDisabled]}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.7}
    >
      <Text style={[textStyle, small && styles.buttonTextSmall]}>{label}</Text>
    </TouchableOpacity>
  );
}

function Chip({ label, color }) {
  const chipColor = color || colors.accentStrong;
  return (
    <View style={[styles.chip, { backgroundColor: `${chipColor}1f` }]}>
      <Text style={[styles.chipText, { color: chipColor }]}>{String(label || "").toUpperCase()}</Text>
    </View>
  );
}

function Badge({ value }) {
  if (!value) {
    return null;
  }
  return (
    <View style={styles.badge}>
      <Text style={styles.badgeText}>{value}</Text>
    </View>
  );
}

function Card({ children, onPress, style }) {
  const content = <View style={[styles.card, style]}>{children}</View>;
  if (!onPress) {
    return content;
  }
  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.76}>
      {content}
    </TouchableOpacity>
  );
}

function ReadOnlyChip({ label }) {
  return <Chip label={label} color={colors.textSoft} />;
}

function RelevanceFilterBar({ includeAll, onToggle }) {
  return (
    <View style={styles.filterBar}>
      <TouchableOpacity
        style={[styles.filterOption, !includeAll && styles.filterOptionActive]}
        onPress={() => includeAll && onToggle()}
        activeOpacity={0.75}
      >
        <Text style={[styles.filterText, !includeAll && styles.filterTextActive]}>Nur relevante</Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.filterOption, includeAll && styles.filterOptionActive]}
        onPress={() => !includeAll && onToggle()}
        activeOpacity={0.75}
      >
        <Text style={[styles.filterText, includeAll && styles.filterTextActive]}>Alle anzeigen</Text>
      </TouchableOpacity>
    </View>
  );
}

function ConfirmTokenModal({ visible, title, explanation, expectedToken, onCancel, onConfirm }) {
  const [value, setValue] = useState("");
  const valid = value === expectedToken;
  useEffect(() => {
    if (visible) {
      setValue("");
    }
  }, [visible, expectedToken]);
  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onCancel}>
      <View style={styles.modalBackdrop}>
        <View style={styles.modalCard}>
          <Text style={styles.cardTitle}>{title}</Text>
          <Text style={styles.cardBody}>{explanation}</Text>
          <Text style={styles.forwardSafety}>Erwarteter Token: {expectedToken}</Text>
          <TextInput
            value={value}
            onChangeText={setValue}
            style={styles.input}
            placeholder={expectedToken}
            placeholderTextColor={colors.textSoft}
            autoCapitalize="characters"
          />
          <View style={styles.row}>
            <ActionButton small variant="ghost" label="Abbrechen" onPress={onCancel} />
            <ActionButton
              small
              label="Bestätigen"
              onPress={() => onConfirm(value)}
              disabled={!valid}
            />
          </View>
        </View>
      </View>
    </Modal>
  );
}

function SectionTitle({ children }) {
  return <Text style={styles.sectionTitle}>{children}</Text>;
}

function EmptyState({ icon, text }) {
  return (
    <View style={styles.empty}>
      <LineIcon name={icon} size={21} color={colors.textSoft} />
      <Text style={styles.emptyText}>{text}</Text>
    </View>
  );
}

function StatCard({ label, value, tint }) {
  return (
    <View style={[styles.statCard, { borderLeftColor: tint }]}>
      <Text style={[styles.statValue, { color: tint }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function Avatar({ name }) {
  const initial = (String(name || "?").trim().charAt(0) || "?").toUpperCase();
  return (
    <View style={styles.avatar}>
      <Text style={styles.avatarText}>{initial}</Text>
    </View>
  );
}

export default function App() {
  const [fontsLoaded, fontLoadError] = useFonts(figtreeFonts);
  const [active, setActive] = useState("Home");
  const [moreScreen, setMoreScreen] = useState("");
  const [locale, setLocaleState] = useState(getAppLocale());

  useEffect(() => {
    initLocale().then((loaded) => setLocaleState(loaded)).catch(() => null);
  }, []);

  const changeLocale = async (nextLocale) => {
    const applied = await setAppLocale(nextLocale);
    setLocaleState(applied);
  };
  const [tokenModal, setTokenModal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadProgress, setLoadProgress] = useState({ done: 0, total: 0 });
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [updateStatus, setUpdateStatus] = useState("Update: prüfe…");
  const [online, setOnline] = useState(null);
  const [syncStatus, setSyncStatus] = useState({
    online: false,
    lastSyncedAt: null,
    lastError: "",
    queueSize: 0,
  });
  const [dashboard, setDashboard] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [messages, setMessages] = useState([]);
  const [messageSuggestions, setMessageSuggestions] = useState([]);
  const [taskSuggestions, setTaskSuggestions] = useState([]);
  const [calendar, setCalendar] = useState(null);
  const [weekCalendar, setWeekCalendar] = useState(null);
  const [calendarViewPrefs, setCalendarViewPrefs] = useState(defaultCalendarViewPrefs);
  const [calendarPrefsResult, setCalendarPrefsResult] = useState("");
  const [googleCalendarPreview, setGoogleCalendarPreview] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [newContactName, setNewContactName] = useState("");
  const [newContactEmail, setNewContactEmail] = useState("");
  const [newContactWhatsapp, setNewContactWhatsapp] = useState("");
  const [newContactNotes, setNewContactNotes] = useState("");
  const [newContactType, setNewContactType] = useState("arbeit");
  const [newContactBetreuer, setNewContactBetreuer] = useState("philip");
  const [contactNotesDrafts, setContactNotesDrafts] = useState({});
  const [contactNotesResult, setContactNotesResult] = useState("");
  const [senderAssignmentDrafts, setSenderAssignmentDrafts] = useState({});
  const [senderAssignmentResult, setSenderAssignmentResult] = useState("");
  const [learning, setLearning] = useState(null);
  const [learningResult, setLearningResult] = useState("");
  const [privacy, setPrivacy] = useState(null);
  const [apiTokenDraft, setApiTokenDraft] = useState("");
  const [apiTokenConfigured, setApiTokenConfigured] = useState(false);
  const [apiTokenResult, setApiTokenResult] = useState("");
  const [setupStatus, setSetupStatus] = useState(null);
  const [accountPolicies, setAccountPolicies] = useState(null);
  const [calendarAccountStatus, setCalendarAccountStatus] = useState(null);
  const [policyLabel, setPolicyLabel] = useState("Google Hauptkalender");
  const [policyProvider, setPolicyProvider] = useState("google_calendar");
  const [policyRole, setPolicyRole] = useState("main");
  const [policyAccess, setPolicyAccess] = useState("read_write");
  const [policyTitleContains, setPolicyTitleContains] = useState("");
  const [policyNotes, setPolicyNotes] = useState("");
  const [policyTransformStart, setPolicyTransformStart] = useState("08:00");
  const [policyTransformEnd, setPolicyTransformEnd] = useState("18:00");
  const [policyIcsUrl, setPolicyIcsUrl] = useState("");
  const [policyToken, setPolicyToken] = useState("");
  const [policyResult, setPolicyResult] = useState("");
  const [calendarActivationToken, setCalendarActivationToken] = useState("");
  const [calendarActivationResult, setCalendarActivationResult] = useState("");
  const [emailAccountStatus, setEmailAccountStatus] = useState(null);
  const [emailInbox, setEmailInbox] = useState(null);
  const [msMailStatus, setMsMailStatus] = useState(null);
  const [msMailInbox, setMsMailInbox] = useState(null);
  const [msMailIncludeAll, setMsMailIncludeAll] = useState(false);
  const [selectedMsMailDetail, setSelectedMsMailDetail] = useState(null);
  const [imapMailStatus, setImapMailStatus] = useState(null);
  const [mailOrganizeLog, setMailOrganizeLog] = useState(null);
  const [mailOrganizeResult, setMailOrganizeResult] = useState("");
  const [mailOrganizeToken, setMailOrganizeToken] = useState("");
  const [whatsappStatus, setWhatsappStatus] = useState(null);
  const [whatsappInbox, setWhatsappInbox] = useState(null);
  const [expandedInboxGroups, setExpandedInboxGroups] = useState({});
  const [blockedSenders, setBlockedSenders] = useState([]);
  const [spamMessages, setSpamMessages] = useState({ messages: [], msMail: [], whatsapp: [] });
  const [spamResult, setSpamResult] = useState("");
  const [emailPreset, setEmailPreset] = useState("gmail");
  const [emailAddress, setEmailAddress] = useState("");
  const [emailUsername, setEmailUsername] = useState("");
  const [emailAppPassword, setEmailAppPassword] = useState("");
  const [emailAgentNotes, setEmailAgentNotes] = useState("");
  const [emailAgentNotesResult, setEmailAgentNotesResult] = useState("");
  const [emailAccountToken, setEmailAccountToken] = useState("");
  const [emailAccountResult, setEmailAccountResult] = useState("");
  const [msMailClientId, setMsMailClientId] = useState("");
  const [msMailTenant, setMsMailTenant] = useState("common");
  const [msMailAuthResponse, setMsMailAuthResponse] = useState("");
  const [msMailAccountToken, setMsMailAccountToken] = useState("");
  const [msMailDeleteToken, setMsMailDeleteToken] = useState("");
  const [msMailActivationToken, setMsMailActivationToken] = useState("");
  const [msMailResult, setMsMailResult] = useState("");
  const [imapMailUsername, setImapMailUsername] = useState("philip07102000@gmail.com");
  const [imapMailAppPassword, setImapMailAppPassword] = useState("");
  const [imapMailAccountToken, setImapMailAccountToken] = useState("");
  const [imapMailDeleteToken, setImapMailDeleteToken] = useState("");
  const [imapMailActivationToken, setImapMailActivationToken] = useState("");
  const [imapMailResult, setImapMailResult] = useState("");
  const [whatsappAgentNotes, setWhatsappAgentNotes] = useState("");
  const [whatsappAgentNotesResult, setWhatsappAgentNotesResult] = useState("");
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskForwardTo, setNewTaskForwardTo] = useState("");
  const [forwardTask, setForwardTask] = useState(null);
  const [forwardContact, setForwardContact] = useState(null);
  const [forwardChannel, setForwardChannel] = useState("email");
  const [forwardDraft, setForwardDraft] = useState("");
  const [forwardMockResult, setForwardMockResult] = useState("");
  const [forwardApprovalToken, setForwardApprovalToken] = useState("");
  const [forwardApprovalResult, setForwardApprovalResult] = useState("");
  const [forwardAuditPreview, setForwardAuditPreview] = useState("");
  const [forwardDeepLink, setForwardDeepLink] = useState("");
  const [forwardExternalOpenResult, setForwardExternalOpenResult] = useState("");
  const [forwardTokenApproved, setForwardTokenApproved] = useState(false);
  const [calendarSuggestionResult, setCalendarSuggestionResult] = useState("");
  const [calendarMessageText, setCalendarMessageText] = useState("");
  const [calendarDraftTitle, setCalendarDraftTitle] = useState("");
  const [calendarDraftDate, setCalendarDraftDate] = useState("");
  const [calendarDraftStart, setCalendarDraftStart] = useState("");
  const [calendarDraftEnd, setCalendarDraftEnd] = useState("");
  const [calendarDraftLocation, setCalendarDraftLocation] = useState("");
  const [calendarWriteToken, setCalendarWriteToken] = useState("");
  const [calendarWriteApprovalId, setCalendarWriteApprovalId] = useState("");
  const [calendarWriteResult, setCalendarWriteResult] = useState("");
  const [calendarDeleteTokens, setCalendarDeleteTokens] = useState({});
  const [calendarDeleteApprovalIds, setCalendarDeleteApprovalIds] = useState({});
  const [calendarDeleteResult, setCalendarDeleteResult] = useState("");
  const [workdaySyncToken, setWorkdaySyncToken] = useState("");
  const [workdaySyncApprovalId, setWorkdaySyncApprovalId] = useState("");
  const [workdaySyncResult, setWorkdaySyncResult] = useState("");
  const [workdaySyncPreview, setWorkdaySyncPreview] = useState(null);
  const [actionBusy, setActionBusy] = useState(false);
  const colorScheme = useColorScheme();
  const isDarkMode = colorScheme === "dark";
  colors = isDarkMode ? darkColors : lightColors;
  styles = createStyles(colors);
  const currentScreen = active === "Mehr" && moreScreen ? moreScreen : active;
  const currentScreenRef = useRef(currentScreen);
  const openLearningCount = Number(learning?.open_count || isArray(learning?.open_questions).length || 0);
  const connectionKind = getApiUrl().includes("100.") ? "Tailscale" : "LAN";
  const homeCalendarItems = isArray(calendar?.merged_items || calendar?.items || calendar?.calendar_items || []);
  const homeRelevantMails = isArray(msMailInbox?.items || []);
  const todayIso = formatDateOnly(new Date());
  const dueHomeTasks = isArray(tasks).filter((task) => {
    const due = String(task?.due_date || "").slice(0, 10);
    return due && due <= todayIso;
  });
  const urgentHomeTasks = isArray(tasks).filter((task) => {
    const priority = String(task?.priority || "").toLowerCase();
    return priority === "urgent" || priority === "high" || priority === "hoch";
  });
  const headerSummary = `${homeCalendarItems.length} Termine · ${urgentHomeTasks.length} dringende Aufgaben`;
  const syncTime = formatSyncTime(syncStatus.lastSyncedAt);
  const syncLabel = syncStatus.online
    ? `Zuletzt synchronisiert ${syncTime || "--:--"}${syncStatus.queueSize ? ` | ${syncStatus.queueSize} offen` : ""}`
    : `Offline - lokaler Stand${syncTime ? ` von ${syncTime}` : ""}${syncStatus.queueSize ? ` | ${syncStatus.queueSize} offen` : ""}`;

  const navigateTo = (screenName, nestedScreen = "") => {
    setError("");
    if (screenName === "Mehr") {
      setActive("Mehr");
      setMoreScreen(nestedScreen);
      return;
    }
    setActive(screenName);
    setMoreScreen("");
  };

  useEffect(() => {
    if (fontsLoaded || fontLoadError) {
      SplashScreen.hideAsync().catch(() => {});
    }
  }, [fontsLoaded, fontLoadError]);

  const openTokenModal = ({ title, explanation, expectedToken, onConfirm }) => {
    setTokenModal({ title, explanation, expectedToken, onConfirm });
  };


  const updateCheckInFlight = useRef(false);
  const progressTotalRef = useRef(0);

  // Ladefortschritt: zählt abgeschlossene API-Calls pro Screen-Ladevorgang,
  // damit der Ladebalken echten Fortschritt zeigt (hängt vs. lädt).
  const beginProgress = (total) => {
    progressTotalRef.current = total;
    setLoadProgress({ done: 0, total });
  };

  const tracked = (promise) =>
    promise.finally(() => {
      setLoadProgress((current) => ({
        ...current,
        done: Math.min(current.done + 1, progressTotalRef.current),
      }));
    });

  const refreshSyncStatusState = async () => {
    const status = await getSyncStatus();
    setSyncStatus(status);
    return status;
  };

  const applyCached = (setter, normalize = (value) => value) => (value, meta) => {
    setter(normalize(value));
    if (meta?.source === "cache") {
      setLoading(false);
    }
  };

  const cachedRequest = (key, fetcher, setter, options = {}) => {
    const requestOptions = {
      normalize: options.normalize,
      apply: applyCached(setter, options.normalize),
    };
    if (Object.prototype.hasOwnProperty.call(options, "fallback")) {
      requestOptions.fallback = options.fallback;
    }
    return tracked(
      readThroughCache(key, fetcher, requestOptions).then(async (result) => {
        if (result?.status) {
          setSyncStatus(result.status);
        } else {
          await refreshSyncStatusState();
        }
        return result?.value;
      }),
    );
  };

  const rememberOnlineState = async (ok) => {
    setOnline(ok);
    const status = await persistSyncStatus({
      online: Boolean(ok),
      lastError: ok ? "" : "Offline - lokaler Stand",
    });
    setSyncStatus(status);
  };

  const mutateTasksCache = async (updater) => {
    const nextTasks = updater(isArray(tasks));
    setTasks(nextTasks);
    await writeLocalCacheEntry(cacheTypes.tasks, nextTasks);
    await refreshSyncStatusState().catch(() => null);
    return nextTasks;
  };

  const mutateContactsCache = async (updater) => {
    const nextContacts = updater(isArray(contacts));
    setContacts(nextContacts);
    await writeLocalCacheEntry(cacheTypes.contacts, nextContacts);
    setContactNotesDrafts(
      Object.fromEntries(nextContacts.map((contact) => [contact.id, contact.notes || ""])),
    );
    await refreshSyncStatusState().catch(() => null);
    return nextContacts;
  };

  useEffect(() => {
    refreshSyncStatusState().catch(() => null);
  }, []);

  useEffect(() => {
    let isMounted = true;

    const applyAvailableUpdate = async () => {
      if (__DEV__) {
        setUpdateStatus("Update: Entwicklung");
        return;
      }

      // Doppelte Checks vermeiden (Kaltstart + Vordergrund gleichzeitig).
      if (updateCheckInFlight.current) {
        return;
      }
      updateCheckInFlight.current = true;

      try {
        const update = await Updates.checkForUpdateAsync();
        if (!isMounted) {
          return;
        }

        if (!update.isAvailable) {
          setUpdateStatus("Update: aktuell");
          return;
        }

        setUpdateStatus("Update: wird installiert…");
        await Updates.fetchUpdateAsync();
        if (isMounted) {
          // reloadAsync startet die App mit dem neuen Bundle neu.
          await Updates.reloadAsync();
        }
      } catch (err) {
        if (isMounted) {
          setUpdateStatus("Update: später erneut");
        }
      } finally {
        updateCheckInFlight.current = false;
      }
    };

    // 1. Kaltstart: sofort prüfen.
    applyAvailableUpdate();

    // 2. Warmstart: jedes Mal prüfen, wenn die App in den Vordergrund kommt.
    const subscription = AppState.addEventListener("change", (nextState) => {
      if (nextState === "active") {
        applyAvailableUpdate();
      }
    });

    return () => {
      isMounted = false;
      subscription.remove();
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    getApiTokenStatus()
      .then((configured) => {
        if (isMounted) {
          setApiTokenConfigured(configured);
        }
      })
      .catch(() => {});

    const ping = async () => {
      const ok = await checkHealth();
      if (isMounted) {
        await rememberOnlineState(ok);
        if (ok) {
          await flushWriteQueue().catch(() => null);
          await refreshSyncStatusState();
        }
      }
    };

    ping();
    const timer = setInterval(ping, 30000);
    return () => {
      isMounted = false;
      clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    // Registration is idempotent. Retry periodically so a temporarily offline
    // phone or backend registers automatically once connectivity returns.
    const register = () => registerForPushNotifications().catch(() => null);
    register();
    const timer = setInterval(register, 60_000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    currentScreenRef.current = currentScreen;
  }, [currentScreen]);

  useEffect(() => {
    // Server-sent events: refresh the visible screen when server data
    // changes elsewhere (debounced — invalidations arrive in bursts).
    let timer = null;
    const unsubscribe = subscribeLiveEvents(() => {
      if (timer) {
        clearTimeout(timer);
      }
      timer = setTimeout(() => {
        loadScreenData(currentScreenRef.current).catch(() => null);
      }, 1200);
    });
    return () => {
      if (timer) {
        clearTimeout(timer);
      }
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    // Alarm fired or tapped -> speak the morning briefing.
    let unsubscribe = () => {};
    // Trigger notifications don't survive a reboot, so re-arm from saved
    // settings on every launch (idempotent — fixed trigger ID gets replaced).
    restoreScheduledAlarm().catch(() => null);
    initAlarmHandlers(() => {
      playMorningBriefing().catch(() => null);
    })
      .then((cleanup) => {
        if (typeof cleanup === "function") {
          unsubscribe = cleanup;
        }
      })
      .catch(() => null);
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    let isMounted = true;

    const load = async () => {
      setLoading(true);
      setError("");

      try {
        await loadScreenData(currentScreen, { silentErrors: false });
      } catch (err) {
        if (isMounted) {
          setError(normalizeApiError(err));
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    load();
    return () => {
      isMounted = false;
    };
  }, [active, moreScreen]);

  // Alle Screen-Daten parallel laden: jede Anfrage meldet ihren Abschluss an den
  // Ladebalken. Vorher liefen z.B. im Setup-Screen 10 Anfragen nacheinander.
  const loadScreenData = async (screenName) => {
    if (screenName === "Home") {
      const homePrefs = { ...defaultCalendarViewPrefs, range_preset: "heute", day_start: "06:00", day_end: "22:00" };
      beginProgress(5);
      const [dashboardPayload, taskPayload, calendarPayload, learningPayload, msMailPayload] = await Promise.all([
        cachedRequest(cacheTypes.dashboard, getDashboard, setDashboard, { fallback: null }),
        cachedRequest(cacheTypes.tasks, getTasks, setTasks, { fallback: [], normalize: isArray }),
        cachedRequest(
          `${cacheTypes.calendar}:home`,
          () => getCalendar(resolveCalendarViewQuery(homePrefs)),
          setCalendar,
          { fallback: null },
        ),
        cachedRequest(cacheTypes.learning, getLearning, setLearning, { fallback: null }),
        cachedRequest(
          `${cacheTypes.unifiedMailInbox}:home`,
          () => getUnifiedMailMessages(5),
          setMsMailInbox,
          { fallback: { items: [] } },
        ),
      ]);
      setDashboard(dashboardPayload);
      setTasks(isArray(taskPayload));
      setCalendar(calendarPayload);
      setLearning(learningPayload);
      setMsMailInbox(msMailPayload);
      return;
    }

    if (screenName === "Mehr") {
      beginProgress(1);
      const payload = await cachedRequest(cacheTypes.learning, getLearning, setLearning, { fallback: null });
      setLearning(payload);
      return;
    }

    if (screenName === "Dashboard") {
      beginProgress(1);
      const payload = await cachedRequest(cacheTypes.dashboard, getDashboard, setDashboard, { fallback: null });
      setDashboard(payload);
      return;
    }

    if (screenName === "Tasks") {
      beginProgress(1);
      const payload = await cachedRequest(cacheTypes.tasks, getTasks, setTasks, { fallback: [], normalize: isArray });
      setTasks(isArray(payload));
      return;
    }

    if (screenName === "Nachrichten") {
      beginProgress(6);
      const [messagePayload, suggestions, inbox, msInbox, whatsapp, contactPayload] = await Promise.all([
        cachedRequest(
          cacheTypes.messages,
          getMessages,
          (payload) => setMessages(isArray(payload?.items || [])),
          { fallback: { items: [] } },
        ),
        cachedRequest(
          cacheTypes.messageSuggestions,
          getMessageSuggestions,
          (payload) => {
            setMessageSuggestions(isArray(payload?.message_suggestions));
            setTaskSuggestions(isArray(payload?.task_suggestions));
          },
          { fallback: { message_suggestions: [], task_suggestions: [] } },
        ),
        cachedRequest(
          cacheTypes.emailInbox,
          () => getEmailInbox(10),
          setEmailInbox,
          { fallback: { connected: false, items: [] } },
        ),
        cachedRequest(
          `${cacheTypes.unifiedMailInbox}:includeAll:${msMailIncludeAll}`,
          () => getUnifiedMailMessages(10, null, false, msMailIncludeAll),
          (payload) => {
            setMsMailInbox(payload);
            setMsMailStatus(payload?.status || null);
          },
          { fallback: { items: [], status: { connected: false, read_enabled: false } } },
        ),
        cachedRequest(
          cacheTypes.whatsappInbox,
          () => getWhatsAppMessages(10),
          setWhatsappInbox,
          { fallback: { items: [], status: { read_enabled: false, connected: false } } },
        ),
        cachedRequest(cacheTypes.contacts, getContacts, setContacts, { fallback: [], normalize: isArray }),
      ]);
      const list = messagePayload?.items || [];
      setMessages(isArray(list));
      setMessageSuggestions(isArray(suggestions?.message_suggestions));
      setTaskSuggestions(isArray(suggestions?.task_suggestions));
      setEmailInbox(inbox);
      setMsMailInbox(msInbox);
      setMsMailStatus(msInbox?.status || null);
      setWhatsappInbox(whatsapp);
      setContacts(isArray(contactPayload));
      return;
    }

    if (screenName === "Spam") {
      beginProgress(4);
      const [blocked, messagePayload, msInbox, whatsapp] = await Promise.all([
        cachedRequest(cacheTypes.blockedSenders, getBlockedSenders, (payload) => setBlockedSenders(isArray(payload?.items)), {
          fallback: { items: [] },
        }),
        cachedRequest(`${cacheTypes.messages}:spam`, () => getMessages(true), () => {}, { fallback: { items: [] } }),
        cachedRequest(
          `${cacheTypes.unifiedMailInbox}:spam`,
          () => getUnifiedMailMessages(50, null, true),
          () => {},
          { fallback: { items: [] } },
        ),
        cachedRequest(`${cacheTypes.whatsappInbox}:spam`, () => getWhatsAppMessages(50, true), () => {}, {
          fallback: { items: [] },
        }),
      ]);
      setBlockedSenders(isArray(blocked?.items));
      setSpamMessages({
        messages: isArray(messagePayload?.items).filter((item) => Number(item?.is_spam || 0) === 1),
        msMail: isArray(msInbox?.items).filter((item) => Number(item?.is_spam || 0) === 1),
        whatsapp: isArray(whatsapp?.items).filter((item) => Number(item?.is_spam || 0) === 1),
      });
      return;
    }

    if (screenName === "Kalender") {
      beginProgress(5);
      const prefs = await cachedRequest(cacheTypes.calendarViewPrefs, getCalendarViewPrefs, setCalendarViewPrefs, {
        fallback: defaultCalendarViewPrefs,
        normalize: (payload) => ({ ...defaultCalendarViewPrefs, ...(payload || {}) }),
      });
      const normalizedPrefs = { ...defaultCalendarViewPrefs, ...(prefs || {}) };
      // Wochenkalender: immer heute + 7 Tage, unabhängig von der gespeicherten Ansicht.
      const weekToday = new Date();
      const weekStart = new Date(weekToday.getFullYear(), weekToday.getMonth(), weekToday.getDate());
      const [payload, weekPayload, calendarStatus] = await Promise.all([
        cachedRequest(
          `${cacheTypes.calendar}:view:${JSON.stringify(resolveCalendarViewQuery(normalizedPrefs))}`,
          () => getCalendar(resolveCalendarViewQuery(normalizedPrefs)),
          setCalendar,
          { fallback: null },
        ),
        cachedRequest(
          `${cacheTypes.weekCalendar}:rolling8`,
          () =>
            getCalendar({
            range_start: formatDateOnly(weekStart),
            range_end: formatDateOnly(addDays(weekStart, 7)),
            day_start: "00:00",
            day_end: "23:59",
            }),
          setWeekCalendar,
          { fallback: null },
        ),
        cachedRequest(cacheTypes.calendarAccountStatus, getCalendarAccountStatus, setCalendarAccountStatus, {
          fallback: null,
        }),
      ]);
      let googlePreview = null;
      if (calendarStatus?.google?.connected) {
        const { rangeStart, rangeEnd } = buildGoogleCalendarRange(30);
        googlePreview = await cachedRequest(
          cacheTypes.googleCalendarPreview,
          () =>
            getGoogleCalendarReadPreview(rangeStart, rangeEnd).catch((err) => ({
            ok: false,
            read_only: true,
            write_enabled: false,
            real_calendar_enabled: false,
            events: [],
            message: normalizeApiError(err),
            blocked_reasons: ["google_calendar_read_failed"],
            external_call_used: true,
            })),
          setGoogleCalendarPreview,
          { fallback: { events: [], read_only: true, write_enabled: false } },
        );
      } else {
        await tracked(Promise.resolve());
      }
      setCalendarViewPrefs(normalizedPrefs);
      setCalendar(payload);
      setWeekCalendar(weekPayload);
      setCalendarAccountStatus(calendarStatus);
      setGoogleCalendarPreview(googlePreview);
      return;
    }

    if (screenName === "Kontakte") {
      beginProgress(1);
      const payload = await cachedRequest(cacheTypes.contacts, getContacts, setContacts, {
        fallback: [],
        normalize: isArray,
      });
      setContacts(isArray(payload));
      setContactNotesDrafts(
        Object.fromEntries(isArray(payload).map((contact) => [contact.id, contact.notes || ""]))
      );
      return;
    }

    if (screenName === "Lernen") {
      beginProgress(1);
      const payload = await cachedRequest(cacheTypes.learning, getLearning, setLearning, { fallback: null });
      setLearning(payload);
      setLearningResult("");
      return;
    }

    if (screenName === "Datenschutz") {
      beginProgress(6);
      const [payload, emailStatus, microsoftStatus, imapStatus, cleanupLog, waStatus] = await Promise.all([
        cachedRequest(cacheTypes.privacy, getPrivacy, setPrivacy, { fallback: null }),
        cachedRequest(cacheTypes.emailAccountStatus, getEmailAccountStatus, setEmailAccountStatus, { fallback: null }),
        cachedRequest(cacheTypes.msMailStatus, getMsMailStatus, setMsMailStatus, { fallback: null }),
        cachedRequest(cacheTypes.imapMailStatus, getImapMailStatus, setImapMailStatus, { fallback: null }),
        cachedRequest(cacheTypes.mailOrganizeLog, getMailOrganizeLog, setMailOrganizeLog, { fallback: null }),
        cachedRequest(cacheTypes.whatsappStatus, getWhatsAppStatus, setWhatsappStatus, { fallback: null }),
      ]);
      setPrivacy(payload);
      setEmailAccountStatus(emailStatus);
      setMsMailStatus(microsoftStatus);
      setImapMailStatus(imapStatus);
      setMailOrganizeLog(cleanupLog);
      setWhatsappStatus(waStatus);
      return;
    }

    if (screenName === "Setup") {
      beginProgress(10);
      const [
        payload,
        privacyPayload,
        policies,
        calendarStatus,
        emailStatus,
        microsoftStatus,
        imapStatus,
        cleanupLog,
        microsoftInbox,
        whatsappNotesPayload,
      ] = await Promise.all([
        cachedRequest(cacheTypes.setupStatus, getSetupStatus, setSetupStatus, { fallback: null }),
        cachedRequest(cacheTypes.privacy, getPrivacy, setPrivacy, { fallback: null }),
        cachedRequest(cacheTypes.accountPolicies, getAccountPolicies, setAccountPolicies, { fallback: null }),
        cachedRequest(cacheTypes.calendarAccountStatus, getCalendarAccountStatus, setCalendarAccountStatus, {
          fallback: null,
        }),
        cachedRequest(cacheTypes.emailAccountStatus, getEmailAccountStatus, setEmailAccountStatus, { fallback: null }),
        cachedRequest(cacheTypes.msMailStatus, getMsMailStatus, setMsMailStatus, { fallback: null }),
        cachedRequest(cacheTypes.imapMailStatus, getImapMailStatus, setImapMailStatus, { fallback: null }),
        cachedRequest(cacheTypes.mailOrganizeLog, getMailOrganizeLog, setMailOrganizeLog, { fallback: null }),
        cachedRequest(
          `${cacheTypes.unifiedMailInbox}:setup:${msMailIncludeAll}`,
          () => getUnifiedMailMessages(10, null, false, msMailIncludeAll),
          setMsMailInbox,
          { fallback: null },
        ),
        cachedRequest(cacheTypes.whatsappAgentNotes, getWhatsAppAgentNotes, (payload) => {}, { fallback: null }),
      ]);
      setSetupStatus(payload);
      setPrivacy(privacyPayload);
      setAccountPolicies(policies);
      setCalendarAccountStatus(calendarStatus);
      setEmailAccountStatus(emailStatus);
      setMsMailStatus(microsoftStatus);
      setImapMailStatus(imapStatus);
      setMailOrganizeLog(cleanupLog);
      setMsMailInbox(microsoftInbox);
      setEmailAgentNotes(emailStatus?.agent_notes || "");
      setWhatsappAgentNotes(whatsappNotesPayload?.agent_notes || "");
    }
  };

  const refreshActive = async () => {
    try {
      setError("");
      await flushWriteQueue().catch(() => null);
      await loadScreenData(currentScreen);
      await refreshSyncStatusState();
    } catch (err) {
      await persistSyncStatus({ online: false, lastError: normalizeApiError(err) }).catch(() => null);
      await refreshSyncStatusState().catch(() => null);
    }
  };

  const handlePullRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshActive();
      const ok = await checkHealth();
      await rememberOnlineState(ok);
      await refreshSyncStatusState();
    } finally {
      setRefreshing(false);
    }
  };

  const handleSaveApiToken = async (remove = false) => {
    const nextToken = remove ? "" : apiTokenDraft.trim();
    if (nextToken && nextToken.length < 32) {
      setApiTokenResult("Der API-Token muss mindestens 32 Zeichen lang sein.");
      return;
    }
    setActionBusy(true);
    try {
      await saveApiToken(nextToken);
      setApiTokenConfigured(Boolean(nextToken));
      setApiTokenDraft("");
      const reachable = await checkHealth();
      await rememberOnlineState(reachable);
      setApiTokenResult(
        nextToken
          ? reachable
            ? "Token sicher gespeichert und von Friday akzeptiert."
            : "Token wurde sicher gespeichert, aber die API hat ihn noch nicht akzeptiert."
          : "Token entfernt. Ohne Token funktioniert Friday nur direkt auf demselben Gerät.",
      );
      if (reachable) {
        await loadScreenData(currentScreen).catch(() => null);
      }
    } catch (err) {
      setApiTokenResult(normalizeApiError(err));
    } finally {
      setActionBusy(false);
    }
  };

  useEffect(() => {
    const subscription = AppState.addEventListener("change", (nextState) => {
      if (nextState === "active") {
        flushWriteQueue()
          .then(() => loadScreenData(currentScreen))
          .then(() => checkHealth())
          .then((ok) => rememberOnlineState(ok))
          .then(() => refreshSyncStatusState())
          .catch(() => refreshSyncStatusState().catch(() => null));
      }
    });
    return () => subscription.remove();
  }, [currentScreen]);

  const handleCreateTask = async () => {
    if (!newTaskTitle.trim()) {
      return;
    }
    setActionBusy(true);
    const forwardTo = newTaskForwardTo.trim();
    const payload = {
      title: newTaskTitle.trim(),
      notes: forwardTo ? `Weiterleiten an: ${forwardTo}` : undefined,
    };
    const tempTask = {
      id: `local-${Date.now()}`,
      title: payload.title,
      notes: payload.notes || "",
      status: "open",
      category: "lokal",
      priority: "normal",
      local_pending: true,
    };
    await mutateTasksCache((current) => [tempTask, ...current]);
    setNewTaskTitle("");
    setNewTaskForwardTo("");
    try {
      await createTask(payload);
      await refreshActive();
    } catch (err) {
      await enqueueOfflineWrite("createTask", { payload });
      await persistSyncStatus({ online: false, lastError: normalizeApiError(err) });
      await refreshSyncStatusState();
    } finally {
      setActionBusy(false);
    }
  };

  const handleCreateContact = async () => {
    if (!newContactName.trim()) {
      return;
    }
    setActionBusy(true);
    const payload = {
      name: newContactName.trim(),
      contact_type: newContactType,
      notes: newContactNotes.trim(),
      email_address: newContactEmail.trim(),
      whatsapp_target: newContactWhatsapp.trim(),
      betreuer: newContactType === "kunde" ? newContactBetreuer : undefined,
    };
    const tempContact = {
      id: `local-${Date.now()}`,
      ...payload,
      local_pending: true,
    };
    await mutateContactsCache((current) => [tempContact, ...current]);
    setNewContactName("");
    setNewContactEmail("");
    setNewContactWhatsapp("");
    setNewContactNotes("");
    setNewContactType("arbeit");
    setNewContactBetreuer("philip");
    try {
      await createContact(payload);
      const payload = await getContacts();
      setContacts(isArray(payload));
      setContactNotesDrafts(
        Object.fromEntries(isArray(payload).map((contact) => [contact.id, contact.notes || ""]))
      );
    } catch (err) {
      await enqueueOfflineWrite("createContact", { payload });
      await persistSyncStatus({ online: false, lastError: normalizeApiError(err) });
      await refreshSyncStatusState();
    } finally {
      setActionBusy(false);
    }
  };

  const handleSaveContactNotes = async (contact) => {
    setActionBusy(true);
    setContactNotesResult("");
    const notes = contactNotesDrafts[contact.id] ?? contact.notes ?? "";
    await mutateContactsCache((current) =>
      current.map((item) => (item.id === contact.id ? { ...item, notes, local_pending: true } : item)),
    );
    try {
      await updateContact(contact.id, { notes });
      const payload = await getContacts();
      setContacts(isArray(payload));
      setContactNotesDrafts(
        Object.fromEntries(isArray(payload).map((item) => [item.id, item.notes || ""]))
      );
      setContactNotesResult("Kontakt-Notiz wurde lokal gespeichert.");
    } catch (err) {
      await enqueueOfflineWrite("updateContactNotes", { contactId: contact.id, notes });
      await persistSyncStatus({ online: false, lastError: normalizeApiError(err) });
      await refreshSyncStatusState();
      setContactNotesResult("Kontakt-Notiz ist lokal gespeichert und wird später synchronisiert.");
    } finally {
      setActionBusy(false);
    }
  };

  const handleAnswerLearningQuestion = async (question, optionId) => {
    setActionBusy(true);
    setLearningResult("");
    try {
      const payload = await answerLearningQuestion(question.id, optionId);
      setLearning(payload);
      setLearningResult(payload?.result?.message || "Antwort wurde lokal gespeichert.");
    } catch (err) {
      setLearningResult(`Lernfrage konnte nicht beantwortet werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleDismissLearningQuestion = async (question) => {
    setActionBusy(true);
    setLearningResult("");
    try {
      const payload = await dismissLearningQuestion(question.id);
      setLearning(payload);
      setLearningResult(payload?.result?.message || "Lernfrage wurde auf später gesetzt.");
    } catch (err) {
      setLearningResult(`Lernfrage konnte nicht verschoben werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleToggleLearnedRule = async (rule) => {
    setActionBusy(true);
    setLearningResult("");
    try {
      const payload = await updateLearnedRule(rule.id, !rule.enabled);
      setLearning(payload);
      setLearningResult(`Regel ist jetzt ${payload?.rule?.enabled ? "aktiv" : "inaktiv"}.`);
    } catch (err) {
      setLearningResult(`Regel konnte nicht geändert werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const updateSenderAssignmentDraft = (sender, patch) => {
    setSenderAssignmentDrafts((current) => {
      const existing = current[sender] || { contact_type: "arbeit", betreuer: "philip" };
      return {
        ...current,
        [sender]: {
          ...existing,
          ...patch,
        },
      };
    });
  };

  const handleAssignSenderContact = async (sender) => {
    if (!String(sender || "").trim()) {
      return;
    }
    const draft = senderAssignmentDrafts[sender] || { contact_type: "arbeit", betreuer: "philip" };
    setActionBusy(true);
    setSenderAssignmentResult("");
    try {
      await createContact({
        name: String(sender).trim(),
        contact_type: draft.contact_type,
        notes: "Aus unbekanntem Absender lokal gespeichert.",
        betreuer: draft.contact_type === "kunde" ? draft.betreuer : undefined,
      });
      setSenderAssignmentResult(
        draft.contact_type === "kunde"
          ? `Kontakt lokal gespeichert: ${sender} ist Kunde, Betreuer: ${betreuerLabel(draft.betreuer)}.`
          : `Kontakt lokal gespeichert: ${sender} (${draft.contact_type}).`,
      );
      const payload = await getContacts();
      setContacts(isArray(payload));
      setSenderAssignmentDrafts((current) => {
        const next = { ...current };
        delete next[sender];
        return next;
      });
    } catch (err) {
      setSenderAssignmentResult(`Kontakt konnte nicht gespeichert werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const openForwardFlow = async (task) => {
    setForwardTask(task);
    setForwardContact(null);
    setForwardChannel("email");
    setForwardDraft("");
    setForwardMockResult("");
    setForwardApprovalToken("");
    setForwardApprovalResult("");
    setForwardAuditPreview("");
    setForwardDeepLink("");
    setForwardExternalOpenResult("");
    setForwardTokenApproved(false);
    if (contacts.length === 0) {
      try {
        const payload = await getContacts();
        setContacts(isArray(payload));
      } catch (err) {
        setError(normalizeApiError(err));
      }
    }
  };

  const closeForwardFlow = () => {
    setForwardTask(null);
    setForwardContact(null);
    setForwardChannel("email");
    setForwardDraft("");
    setForwardMockResult("");
    setForwardApprovalToken("");
    setForwardApprovalResult("");
    setForwardAuditPreview("");
    setForwardDeepLink("");
    setForwardExternalOpenResult("");
    setForwardTokenApproved(false);
  };

  const requestAiForwardDraft = async (task, contact, channel) => {
    if (!task || !contact) {
      return;
    }
    setForwardDraft(buildForwardDraft(task, contact, channel));
    setForwardMockResult("KI-Draft wird lokal vorbereitet…");
    setForwardDeepLink("");
    setForwardExternalOpenResult("");
    setForwardTokenApproved(false);
    try {
      const draft = await buildTaskForwardDraft({
        task_id: task.id,
        contact_id: contact.id,
        channel,
      });
      setForwardDraft(draft?.draft_text || buildForwardDraft(task, contact, channel));
      setForwardDeepLink(draft?.deep_link || "");
      setForwardMockResult(
        [
          `KI verbunden: ${draft?.provider || "mock"} (${draft?.is_mock ? "Mock" : "lokal"})`,
          draft?.provider_output_used ? "Provider-Text übernommen." : "Sicherer lokaler Draft verwendet.",
          `Echter Versand: ${draft?.external_send_enabled ? "aktiv" : "aus"}`,
          draft?.deep_link ? "App-Link vorbereitet. Versand bleibt beim Nutzer." : draft?.deep_link_message,
          draft?.blocked_reasons?.length
            ? `Hinweise: ${draft.blocked_reasons.join(" / ")}`
            : "Keine Blocker.",
        ].join("\n"),
      );
    } catch (err) {
      setForwardMockResult(`KI-Draft nicht erreichbar: ${normalizeApiError(err)}. Lokaler Fallback bleibt aktiv.`);
      setForwardDeepLink("");
    }
  };

  const selectForwardContact = async (contact) => {
    setForwardContact(contact);
    setForwardDraft(buildForwardDraft(forwardTask, contact, forwardChannel));
    setForwardMockResult("");
    setForwardApprovalToken("");
    setForwardApprovalResult("");
    setForwardAuditPreview("");
    setForwardDeepLink("");
    setForwardExternalOpenResult("");
    setForwardTokenApproved(false);
    await requestAiForwardDraft(forwardTask, contact, forwardChannel);
  };

  const selectForwardChannel = async (channel) => {
    setForwardChannel(channel);
    if (forwardTask && forwardContact) {
      setForwardDraft(buildForwardDraft(forwardTask, forwardContact, channel));
    }
    setForwardMockResult("");
    setForwardApprovalToken("");
    setForwardApprovalResult("");
    setForwardAuditPreview("");
    setForwardDeepLink("");
    setForwardExternalOpenResult("");
    setForwardTokenApproved(false);
    await requestAiForwardDraft(forwardTask, forwardContact, channel);
  };

  const checkForwardApprovalToken = (tokenOverride) => {
    const expected = approvalTokenFor(forwardChannel);
    const providedToken = (tokenOverride || forwardApprovalToken).trim();
    if (providedToken !== expected) {
      setForwardApprovalResult(
        `Freigabe abgelehnt. Erwarteter Token: ${expected}. Es wurde nichts gesendet.`,
      );
      setForwardAuditPreview("");
      setForwardTokenApproved(false);
      return;
    }
    setForwardTokenApproved(true);
    setForwardApprovalResult(
      `Freigabe akzeptiert (${expected}). Der Öffnen-Button ist freigegeben; Friday sendet weiterhin nichts.`,
    );
    const target =
      forwardChannel === "whatsapp"
        ? forwardContact?.whatsapp_target || "kein WhatsApp-Ziel gespeichert"
        : forwardContact?.email_address || "keine E-Mail-Adresse gespeichert";
    setForwardAuditPreview(
      [
        "Audit Preview",
        `Zeit: ${new Date().toISOString()}`,
        `Aufgabe: #${forwardTask?.id || "-"} ${forwardTask?.title || "-"}`,
        `Kontakt: ${forwardContact?.name || "-"}`,
        `Kanal: ${channelLabel(forwardChannel)}`,
        `Ziel: ${target}`,
        `Token: ${expected}`,
        "Status: Freigabe akzeptiert, externer App-Link darf geöffnet werden",
      ].join("\n"),
    );
  };

  const openForwardExternalApp = async () => {
    if (!forwardDeepLink) {
      setForwardExternalOpenResult("Kein App-Link verfügbar. Friday hat nichts gesendet.");
      return;
    }

    try {
      await Linking.openURL(forwardDeepLink);
      const result = "Extern geöffnet - Versand liegt beim Nutzer. Friday hat nichts gesendet.";
      setForwardExternalOpenResult(result);
      setForwardAuditPreview((current) =>
        [current, `Status: ${result}`].filter(Boolean).join("\n"),
      );
    } catch (err) {
      setForwardExternalOpenResult(
        `Externe App konnte nicht geöffnet werden: ${normalizeApiError(err)}. Friday hat nichts gesendet.`,
      );
    }
  };

  const sendForwardEmailThroughFriday = async () => {
    if (!forwardTask || !forwardContact || forwardChannel !== "email") {
      return;
    }
    setActionBusy(true);
    try {
      const result = await sendTaskForwardEmail({
        task_id: forwardTask.id,
        contact_id: forwardContact.id,
        subject: `Aufgabe: ${forwardTask.title || ""}`,
        body: forwardDraft,
        approval_token: forwardApprovalToken.trim(),
      });
      setForwardExternalOpenResult(
        result?.sent
          ? `Friday hat die E-Mail gesendet. Message-ID: ${result?.message_id || "-"}`
          : `Friday hat nicht gesendet: ${(result?.guard?.blocked_reasons || []).join(" / ") || result?.message || "blockiert"}`,
      );
    } catch (err) {
      setForwardExternalOpenResult(`E-Mail-Versand blockiert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleConnectEmailAccount = async (tokenOverride) => {
    if (!emailAddress.trim() || !emailAppPassword.trim()) {
      setEmailAccountResult("E-Mail-Adresse und App-Passwort sind erforderlich.");
      return;
    }
    setActionBusy(true);
    setEmailAccountResult("Verbindungstest läuft…");
    try {
      const result = await connectEmailAccount({
        preset_name: emailPreset.trim() || "gmail",
        email_address: emailAddress.trim(),
        username: emailUsername.trim() || emailAddress.trim(),
        app_password: emailAppPassword,
        approval_token: (tokenOverride || emailAccountToken).trim(),
        agent_notes: emailAgentNotes.trim(),
      });
      setEmailAppPassword("");
      setEmailAccountResult(
        result?.saved
          ? "E-Mail-Konto lokal gespeichert. Real-Versand bleibt aus, bis EMAIL AKTIVIEREN separat freigegeben wird."
          : result?.message || "Konto wurde nicht gespeichert.",
      );
      const status = await getEmailAccountStatus();
      setEmailAccountStatus(status);
      setEmailAgentNotes(status?.agent_notes || "");
    } catch (err) {
      setEmailAccountResult(`Konto konnte nicht verbunden werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleSaveEmailAgentNotes = async () => {
    setActionBusy(true);
    setEmailAgentNotesResult("");
    try {
      const result = await updateEmailAgentNotes({ agent_notes: emailAgentNotes });
      setEmailAccountStatus(result?.status || null);
      setEmailAgentNotes(result?.status?.agent_notes || emailAgentNotes);
      setEmailAgentNotesResult(result?.message || "E-Mail-Agent-Notiz wurde lokal gespeichert.");
    } catch (err) {
      setEmailAgentNotesResult(`E-Mail-Agent-Notiz konnte nicht gespeichert werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleSaveWhatsAppAgentNotes = async () => {
    setActionBusy(true);
    setWhatsappAgentNotesResult("");
    try {
      const result = await updateWhatsAppAgentNotes({ agent_notes: whatsappAgentNotes });
      setWhatsappAgentNotes(result?.agent_notes || whatsappAgentNotes);
      setWhatsappAgentNotesResult("WhatsApp-Agent-Notiz wurde lokal gespeichert.");
    } catch (err) {
      setWhatsappAgentNotesResult(`WhatsApp-Agent-Notiz konnte nicht gespeichert werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleTestEmailAccount = async () => {
    setActionBusy(true);
    try {
      const result = await testEmailAccountConnection();
      setEmailAccountResult(
        result?.connected
          ? `SMTP: ${result.smtp_ok ? "OK" : "Fehler"} / IMAP: ${result.imap_ok ? "OK" : "Fehler"}`
          : "Kein E-Mail-Konto verbunden.",
      );
    } catch (err) {
      setEmailAccountResult(`Test fehlgeschlagen: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handlePrepareMsMailAuth = async () => {
    if (!msMailClientId.trim()) {
      setMsMailResult("Microsoft Client-ID ist erforderlich.");
      return;
    }
    setActionBusy(true);
    setMsMailResult("");
    try {
      const result = await connectMsMailAccount({
        client_id: msMailClientId.trim(),
        tenant: msMailTenant.trim() || "common",
      });
      const url = result?.authorization_url || "";
      setMsMailResult(url ? `OAuth-Link geöffnet. Falls nicht: ${url}` : "OAuth-Link konnte nicht erzeugt werden.");
      if (url) {
        await Linking.openURL(url);
      }
    } catch (err) {
      setMsMailResult(`OAuth-Link konnte nicht vorbereitet werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleCompleteMsMailConnect = async (tokenOverride) => {
    if (!msMailClientId.trim() || !msMailAuthResponse.trim()) {
      setMsMailResult("Client-ID und OAuth-Rückgabe-URL sind erforderlich.");
      return;
    }
    setActionBusy(true);
    setMsMailResult("Microsoft-Mail wird verbunden…");
    try {
      const result = await connectMsMailAccount({
        client_id: msMailClientId.trim(),
        tenant: msMailTenant.trim() || "common",
        authorization_response: msMailAuthResponse.trim(),
        approval_token: (tokenOverride || msMailAccountToken).trim(),
      });
      setMsMailAuthResponse("");
      setMsMailResult(
        result?.saved
          ? "Familienhelden-Postfach lokal verschlüsselt gespeichert. Es bleibt nur lesend."
          : result?.message || "Microsoft-Mail-Konto wurde nicht gespeichert.",
      );
      setMsMailStatus(await getMsMailStatus());
    } catch (err) {
      setMsMailResult(`Microsoft-Mail konnte nicht verbunden werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleActivateMsMailRead = async (tokenOverride) => {
    setActionBusy(true);
    setMsMailResult("");
    try {
      const result = await activateMsMailRead({
        approval_token: (tokenOverride || msMailActivationToken).trim(),
        scanner_smoke_passed: true,
        execute_write: true,
      });
      setMsMailResult(
        result?.config_write_performed
          ? "Mail-Lesen wurde in der Config aktiviert. Bitte Friday API neu starten."
          : `Mail-Lesen noch blockiert: ${(result?.blocked_reasons || []).join(" / ") || "Gate nicht erfüllt"}`,
      );
      setMsMailStatus(await getMsMailStatus());
    } catch (err) {
      setMsMailResult(`Aktivierung blockiert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleToggleMsMailIncludeAll = async () => {
    const nextIncludeAll = !msMailIncludeAll;
    setMsMailIncludeAll(nextIncludeAll);
    setActionBusy(true);
    setMsMailResult("");
    try {
      setMsMailInbox(await getUnifiedMailMessages(10, null, false, nextIncludeAll));
    } catch (err) {
      setMsMailResult(`Microsoft-Mail-Ansicht konnte nicht geladen werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleOpenMsMailDetail = async (item) => {
    if (!item?.id) {
      return;
    }
    setActionBusy(true);
    setMsMailResult("");
    try {
      setSelectedMsMailDetail(await getUnifiedMailMessage(item.id));
    } catch (err) {
      setMsMailResult(`Mail-Detail konnte nicht geladen werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleSyncMsMail = async (accountId = null) => {
    const selectedAccountId = typeof accountId === "string" ? accountId : null;
    setActionBusy(true);
    setMsMailResult("");
    try {
      const result = await syncMsMailMessages({
        top: 25,
        ...(selectedAccountId ? { account_id: selectedAccountId } : {}),
      });
      const label = selectedAccountId ? ` fuer ${selectedAccountId}` : "";
      setMsMailResult(`Sync${label} fertig: ${result?.stored_count || 0} Mail-Vorschauen lokal aktualisiert.`);
      setMsMailInbox(await getUnifiedMailMessages(10, null, false, msMailIncludeAll));
      setMsMailStatus(await getMsMailStatus());
      await refreshActive();
    } catch (err) {
      setMsMailResult(`Sync blockiert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleDeleteMsMailAccount = async (accountId, tokenOverride) => {
    if (!accountId) {
      setMsMailResult("Konto-ID fehlt.");
      return;
    }
    setActionBusy(true);
    setMsMailResult("");
    try {
      await deleteMsMailAccount(accountId, {
        approval_token: (tokenOverride || msMailDeleteToken).trim(),
      });
      setMsMailResult(`Postfach ${accountId} wurde lokal getrennt.`);
      setMsMailDeleteToken("");
      setMsMailInbox(await getUnifiedMailMessages(10));
      setMsMailStatus(await getMsMailStatus());
      await refreshActive();
    } catch (err) {
      setMsMailResult(`Trennen blockiert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleConnectImapMailAccount = async (tokenOverride) => {
    if (!imapMailUsername.trim() || !imapMailAppPassword.trim()) {
      setImapMailResult("Gmail-Adresse und App-Passwort sind erforderlich.");
      return;
    }
    setActionBusy(true);
    setImapMailResult("Gmail wird read-only verbunden...");
    try {
      const result = await connectImapMailAccount({
        provider: "gmail",
        host: "imap.gmail.com",
        port: 993,
        username: imapMailUsername.trim(),
        app_password: imapMailAppPassword,
        approval_token: (tokenOverride || imapMailAccountToken).trim(),
      });
      setImapMailAppPassword("");
      setImapMailAccountToken("");
      setImapMailResult(
        result?.saved
          ? "Gmail-Konto lokal verschluesselt gespeichert. Es bleibt nur lesend."
          : result?.message || "Gmail-Konto wurde nicht gespeichert.",
      );
      setImapMailStatus(await getImapMailStatus());
    } catch (err) {
      setImapMailResult(`Gmail konnte nicht verbunden werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleActivateImapMailRead = async (tokenOverride) => {
    setActionBusy(true);
    setImapMailResult("");
    try {
      const result = await activateImapMailRead({
        approval_token: (tokenOverride || imapMailActivationToken).trim(),
        scanner_smoke_passed: true,
        execute_write: true,
      });
      setImapMailResult(
        result?.config_write_performed
          ? "Gmail-Lesen wurde in der Config aktiviert. Bitte Friday API neu starten."
          : `Gmail-Lesen noch blockiert: ${(result?.blocked_reasons || []).join(" / ") || "Gate nicht erfuellt"}`,
      );
      setImapMailStatus(await getImapMailStatus());
    } catch (err) {
      setImapMailResult(`Gmail-Aktivierung blockiert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleActivateMailOrganize = async () => {
    setActionBusy(true);
    setMailOrganizeResult("");
    try {
      const result = await activateMailOrganize({
        approval_token: mailOrganizeToken.trim(),
        scanner_smoke_passed: true,
        execute_write: true,
      });
      setMailOrganizeResult(result?.message || "Gmail-Aufraeumen geprueft.");
      setMailOrganizeLog(await getMailOrganizeLog());
      await refreshActive();
    } catch (err) {
      setMailOrganizeResult(`Gmail-Aufraeumen blockiert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleRunMailOrganize = async () => {
    setActionBusy(true);
    setMailOrganizeResult("");
    try {
      const result = await runMailOrganize({ top: 25, dry_run: false });
      setMailOrganizeResult(`${result?.moved_count || 0} Mail(s) nach Friday/Aussortiert verschoben.`);
      setMailOrganizeLog(await getMailOrganizeLog());
      await refreshActive();
    } catch (err) {
      setMailOrganizeResult(`Gmail-Aufraeumen blockiert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleUndoMailOrganize = async (logId) => {
    setActionBusy(true);
    setMailOrganizeResult("");
    try {
      const result = await undoMailOrganize(logId);
      setMailOrganizeResult(result?.message || "Mail wurde zurueckgeholt.");
      setMailOrganizeLog(await getMailOrganizeLog());
      await refreshActive();
    } catch (err) {
      setMailOrganizeResult(`Rueckgaengig blockiert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleSyncImapMail = async (accountId = null) => {
    const selectedAccountId = typeof accountId === "string" ? accountId : null;
    setActionBusy(true);
    setImapMailResult("");
    try {
      const result = await syncImapMailMessages({
        top: 25,
        ...(selectedAccountId ? { account_id: selectedAccountId } : {}),
      });
      const label = selectedAccountId ? ` fuer ${selectedAccountId}` : "";
      setImapMailResult(`Gmail-Sync${label} fertig: ${result?.stored_count || 0} Mail-Vorschauen lokal aktualisiert.`);
      setMsMailInbox(await getUnifiedMailMessages(10, null, false, msMailIncludeAll));
      setImapMailStatus(await getImapMailStatus());
      setMailOrganizeLog(await getMailOrganizeLog());
      await refreshActive();
    } catch (err) {
      setImapMailResult(`Gmail-Sync blockiert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleDeleteImapMailAccount = async (accountId, tokenOverride) => {
    if (!accountId) {
      setImapMailResult("Gmail-Konto-ID fehlt.");
      return;
    }
    setActionBusy(true);
    setImapMailResult("");
    try {
      await deleteImapMailAccount(accountId, {
        approval_token: (tokenOverride || imapMailDeleteToken).trim(),
      });
      setImapMailResult(`Gmail-Konto ${accountId} wurde lokal getrennt.`);
      setImapMailDeleteToken("");
      setMsMailInbox(await getUnifiedMailMessages(10));
      setImapMailStatus(await getImapMailStatus());
      await refreshActive();
    } catch (err) {
      setImapMailResult(`Gmail-Trennen blockiert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };
  const handleMarkMessageSpam = async (source, messageId, label = "Absender") => {
    setActionBusy(true);
    setSpamResult("");
    try {
      const result = await markMessageSpam(source, messageId);
      const blockedLabel = result?.blocked_sender?.label || label || "Absender";
      setSpamResult(`${blockedLabel} wurde lokal blockiert. Echte Postfächer bleiben unverändert.`);
      await refreshActive();
    } catch (err) {
      setSpamResult(`Blockieren nicht möglich: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleUnblockSender = async (blockedSenderId) => {
    setActionBusy(true);
    setSpamResult("");
    try {
      await unblockSender(blockedSenderId);
      setSpamResult("Absender wurde lokal entblockt.");
      await refreshActive();
    } catch (err) {
      setSpamResult(`Entblocken nicht möglich: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleCreateAccountPolicy = async (tokenOverride) => {
    setActionBusy(true);
    setPolicyResult("");
    try {
      const titleContains = policyTitleContains
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);
      const fixedWindow =
        policyProvider.trim() === "outlook_ics" &&
        policyTransformStart.trim() &&
        policyTransformEnd.trim()
          ? {
              fixed_daily_window: {
                start: policyTransformStart.trim(),
                end: policyTransformEnd.trim(),
              },
            }
          : {};
      const result = await createAccountPolicy({
        provider: policyProvider.trim() || "google_calendar",
        label: policyLabel.trim(),
        role: policyRole.trim() || "source",
        access: policyAccess.trim() || "read",
        include_filters: titleContains.length ? { title_contains: titleContains } : {},
        exclude_filters: {},
        transform: fixedWindow,
        notes: policyNotes,
        enabled: true,
        approval_token: (tokenOverride || policyToken).trim(),
        ics_url: policyProvider.trim() === "outlook_ics" ? policyIcsUrl.trim() : undefined,
      });
      setPolicyResult(result?.message || "Policy wurde gespeichert.");
      setPolicyToken("");
      if (policyProvider.trim() === "outlook_ics") {
        setPolicyIcsUrl("");
      }
      await refreshActive();
    } catch (err) {
      setPolicyResult(`Policy wurde nicht gespeichert: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleCalendarActivationGate = async () => {
    setActionBusy(true);
    setCalendarActivationResult("");
    try {
      const result = await checkCalendarActivationGate({
        approval_token: calendarActivationToken.trim(),
        scanner_smoke_passed: true,
      });
      setCalendarActivationResult(
        result?.allowed
          ? "Kalender-Aktivierung waere erlaubt. Config-Apply bleibt bewusst separat."
          : `Kalender-Aktivierung blockiert: ${(result?.blocked_reasons || []).join(", ")}`,
      );
    } catch (err) {
      setCalendarActivationResult(`Gate konnte nicht geprueft werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleSaveCalendarViewPrefs = async () => {
    setActionBusy(true);
    setCalendarPrefsResult("");
    try {
      const saved = await updateCalendarViewPrefs({
        range_preset: calendarViewPrefs.range_preset || "heute",
        custom_from: calendarViewPrefs.custom_from || null,
        custom_to: calendarViewPrefs.custom_to || null,
        day_start: calendarViewPrefs.day_start || "00:00",
        day_end: calendarViewPrefs.day_end || "23:59",
      });
      const normalizedPrefs = { ...defaultCalendarViewPrefs, ...(saved || {}) };
      const payload = await getCalendar(resolveCalendarViewQuery(normalizedPrefs));
      setCalendarViewPrefs(normalizedPrefs);
      setCalendar(payload);
      setCalendarPrefsResult("Kalenderansicht wurde gespeichert und neu geladen.");
    } catch (err) {
      setCalendarPrefsResult(`Kalenderansicht konnte nicht gespeichert werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleCreateCalendarEventFromMessage = async (tokenOverride) => {
    setActionBusy(true);
    setCalendarWriteResult("");
    try {
      const result = await createCalendarEventFromMessage({
        approval_token: (tokenOverride || calendarWriteToken).trim(),
        approval_id: calendarWriteApprovalId,
        text: calendarMessageText.trim(),
        title: calendarDraftTitle.trim() || undefined,
        date: calendarDraftDate.trim() || undefined,
        start: calendarDraftStart.trim() || undefined,
        end: calendarDraftEnd.trim() || undefined,
        location: calendarDraftLocation.trim() || undefined,
      });
      if (result?.provider_event_created) {
        setCalendarWriteResult("Termin wurde im Google-Kalender gespeichert.");
        setCalendarWriteToken("");
        setCalendarWriteApprovalId("");
        await refreshActive();
      } else if (result?.approval?.id) {
        setCalendarWriteApprovalId(result.approval.id);
        setCalendarWriteResult("Termin-Vorschau ist fünf Minuten gültig. Bitte dieselbe Aktion jetzt erneut bestätigen.");
      } else {
        const reasons = result?.guard?.blocked_reasons || [];
        if (reasons.includes("one_time_approval_invalid")) {
          setCalendarWriteApprovalId("");
        }
        setCalendarWriteResult(`Termin wurde nicht gespeichert: ${reasons.join(", ") || result?.guard?.message || "unbekannt"}`);
      }
    } catch (err) {
      setCalendarWriteResult(`Termin konnte nicht uebernommen werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleDeleteCalendarEvent = async (entry, tokenOverride) => {
    const eventId = entry?.id || entry?.provider_event_id;
    if (!eventId) {
      setCalendarDeleteResult("Termin konnte nicht geloescht werden: Event-ID fehlt.");
      return;
    }
    setActionBusy(true);
    setCalendarDeleteResult("");
    try {
      const result = await deleteCalendarEvent({
        approval_token: (tokenOverride || calendarDeleteTokens[eventId] || "").trim(),
        approval_id: calendarDeleteApprovalIds[eventId] || "",
        provider_event_id: eventId,
        calendar_id: entry?.calendar_id || calendarAccountStatus?.google?.calendar_id || "primary",
      });
      if (result?.provider_event_deleted) {
        setCalendarDeleteResult("Termin wurde geloescht.");
        setCalendarDeleteTokens((current) => ({ ...current, [eventId]: "" }));
        setCalendarDeleteApprovalIds((current) => ({ ...current, [eventId]: "" }));
        await refreshActive();
      } else if (result?.approval?.id) {
        setCalendarDeleteApprovalIds((current) => ({ ...current, [eventId]: result.approval.id }));
        setCalendarDeleteResult("Löschvorschau ist fünf Minuten gültig. Bitte denselben Termin jetzt erneut bestätigen.");
      } else {
        const reasons = result?.guard?.blocked_reasons || [];
        if (reasons.includes("one_time_approval_invalid")) {
          setCalendarDeleteApprovalIds((current) => ({ ...current, [eventId]: "" }));
        }
        setCalendarDeleteResult(`Termin wurde nicht geloescht: ${reasons.join(", ") || result?.guard?.message || "unbekannt"}`);
      }
    } catch (err) {
      setCalendarDeleteResult(`Termin konnte nicht geloescht werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handlePreviewWorkdaySync = async () => {
    setActionBusy(true);
    setWorkdaySyncResult("");
    try {
      const result = await syncWorkdaysToGoogle({ dry_run: true, days: 365 });
      setWorkdaySyncPreview(result);
      setWorkdaySyncApprovalId(result?.approval?.id || "");
      setWorkdaySyncResult(result?.message || "Vorschau geladen.");
    } catch (err) {
      setWorkdaySyncPreview(null);
      setWorkdaySyncApprovalId("");
      setWorkdaySyncResult(`Vorschau fehlgeschlagen: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleRunWorkdaySync = async (tokenOverride) => {
    setActionBusy(true);
    setWorkdaySyncResult("");
    try {
      const result = await syncWorkdaysToGoogle({
        dry_run: false,
        days: 365,
        approval_token: (tokenOverride || workdaySyncToken).trim(),
        approval_id: workdaySyncApprovalId,
      });
      setWorkdaySyncPreview(result);
      setWorkdaySyncResult(result?.message || "Kalenderquellen wurden synchronisiert.");
      if (isArray(result?.created).length) {
        setWorkdaySyncToken("");
        setWorkdaySyncApprovalId("");
        await refreshActive();
      } else if (result?.approval?.id) {
        setWorkdaySyncApprovalId(result.approval.id);
      } else if (isArray(result?.guard?.blocked_reasons).includes("one_time_approval_invalid")) {
        setWorkdaySyncApprovalId("");
      }
    } catch (err) {
      setWorkdaySyncResult(`Eintragen fehlgeschlagen: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleCompleteTask = async (taskId) => {
    setActionBusy(true);
    await mutateTasksCache((current) =>
      current.map((task) => (task.id === taskId ? { ...task, status: "done", local_pending: true } : task)),
    );
    try {
      await completeTask(taskId);
      await refreshActive();
    } catch (err) {
      await enqueueOfflineWrite("completeTask", { taskId });
      await persistSyncStatus({ online: false, lastError: normalizeApiError(err) });
      await refreshSyncStatusState();
    } finally {
      setActionBusy(false);
    }
  };

  const handleSnoozeTask = async (taskId) => {
    const until = new Date();
    until.setDate(until.getDate() + 1);
    const untilIso = until.toISOString().slice(0, 10);
    setActionBusy(true);
    await mutateTasksCache((current) =>
      current.map((task) =>
        task.id === taskId ? { ...task, snoozed_until: untilIso, local_pending: true } : task,
      ),
    );
    try {
      await snoozeTask(taskId, untilIso);
      await refreshActive();
    } catch (err) {
      await enqueueOfflineWrite("snoozeTask", { taskId, until: untilIso });
      await persistSyncStatus({ online: false, lastError: normalizeApiError(err) });
      await refreshSyncStatusState();
    } finally {
      setActionBusy(false);
    }
  };

  const handleArchiveTask = async (taskId) => {
    setActionBusy(true);
    await mutateTasksCache((current) =>
      current.map((task) => (task.id === taskId ? { ...task, status: "archived", local_pending: true } : task)),
    );
    try {
      await archiveTask(taskId);
      await refreshActive();
    } catch (err) {
      await enqueueOfflineWrite("archiveTask", { taskId });
      await persistSyncStatus({ online: false, lastError: normalizeApiError(err) });
      await refreshSyncStatusState();
    } finally {
      setActionBusy(false);
    }
  };

  const handleDeleteTask = async (taskId) => {
    setActionBusy(true);
    await mutateTasksCache((current) => current.filter((task) => task.id !== taskId));
    try {
      await deleteTask(taskId);
      await refreshActive();
    } catch (err) {
      await enqueueOfflineWrite("deleteTask", { taskId });
      await persistSyncStatus({ online: false, lastError: normalizeApiError(err) });
      await refreshSyncStatusState();
    } finally {
      setActionBusy(false);
    }
  };

  const handleMessageSuggestionReply = async (messageId) => {
    try {
      const reply = await getMessageSuggestion(messageId);
      setMessageSuggestions((current) => [
        {
          id: `preview-${messageId}`,
          message_id: messageId,
          suggestion_type: "reply",
          draft_text: reply?.draft_text || "Vorschau nicht verfügbar.",
          status: "preview",
          notes: `Kontakt-Typ: ${reply?.contact_type || "unbekannt"} / Intent: ${reply?.intent || "unbekannt"}`,
          preview: true,
        },
        ...current,
      ]);
    } catch (err) {
      setError(normalizeApiError(err));
    }
  };

  const handleGenerateTaskSuggestionForMessage = async (messageId) => {
    try {
      await generateTaskSuggestionsForMessage(messageId);
      await refreshActive();
    } catch (err) {
      setError(normalizeApiError(err));
    }
  };

  const handleGenerateCalendarSuggestionForMessage = async (messageId) => {
    setActionBusy(true);
    setCalendarSuggestionResult("");
    try {
      const result = await generateCalendarEventSuggestionForMessage(messageId);
      if (result?.created) {
        setCalendarSuggestionResult("Termin-Vorschlag wurde lokal im Review-Flow erstellt.");
      } else if (result?.extraction?.has_event === false) {
        setCalendarSuggestionResult("Kein vollstaendiger Termin erkannt. Es wurde nichts gespeichert.");
      } else {
        setCalendarSuggestionResult("Termin-Vorschlag ist bereits vorhanden oder wurde nicht erstellt.");
      }
      await refreshActive();
    } catch (err) {
      setCalendarSuggestionResult(`Termin-Erkennung fehlgeschlagen: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleMessageSuggestionDecision = async (suggestionId, status) => {
    setActionBusy(true);
    try {
      if (status === "approved") {
        await approveMessageSuggestion(suggestionId);
      } else {
        await rejectMessageSuggestion(suggestionId);
      }
      await refreshActive();
    } catch (err) {
      setError(normalizeApiError(err));
    } finally {
      setActionBusy(false);
    }
  };

  const handleTaskSuggestionDecision = async (suggestionId, status) => {
    setActionBusy(true);
    try {
      if (status === "approved") {
        await approveTaskSuggestion(suggestionId);
      } else {
        await rejectTaskSuggestion(suggestionId);
      }
      await refreshActive();
    } catch (err) {
      setError(normalizeApiError(err));
    } finally {
      setActionBusy(false);
    }
  };

  const renderHomeScreen = () => {
    const nextEvents = homeCalendarItems.slice(0, 3);
    const relevantMails = homeRelevantMails.slice(0, 3);
    const dueTasks = dueHomeTasks.slice(0, 3);
    const learningCount = openLearningCount;
    return (
      <View>
        <SectionTitle>Heute</SectionTitle>
        <View style={styles.homeHero}>
          <View style={styles.cardHeader}>
            <View>
              <Text style={styles.homeEyebrow}>Tagesüberblick</Text>
              <Text style={styles.homeTitle}>Was heute wichtig ist</Text>
            </View>
            <Chip label={connectionKind} color={colors.onAccent} />
          </View>
          <Text style={[styles.cardBody, { color: colors.onAccent }]}>{headerSummary}</Text>
        </View>

        <Card onPress={() => navigateTo("Kalender")}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Heute im Kalender</Text>
            <Badge value={nextEvents.length} />
          </View>
          {nextEvents.map((item, index) => (
            <View key={`${item.id || item.title || index}-home-cal`} style={styles.homeListRow}>
              <Text style={styles.homeListTime}>{String(item.start || item.start_time || "").slice(0, 5) || "--:--"}</Text>
              <View style={{ flex: 1 }}>
                <Text style={styles.cardBody}>{item.title || item.summary || "Termin"}</Text>
                <ReadOnlyChip label={item.policy_label || item.provider || item.item_type || "Quelle"} />
              </View>
            </View>
          ))}
          {nextEvents.length === 0 && <EmptyState icon="calendar" text="Heute ist kein Termin im Filter sichtbar." />}
        </Card>

        <Card onPress={() => navigateTo("Nachrichten")}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Relevante Mails</Text>
            <Badge value={relevantMails.length} />
          </View>
          {relevantMails.map((mail) => (
            <View key={mail.id || mail.message_id} style={styles.homeListRow}>
              <Avatar name={mail.sender || "Mail"} />
              <View style={{ flex: 1 }}>
                <Text style={styles.cardTitle}>{mail.sender || "Unbekannter Absender"}</Text>
                <Text style={styles.cardMeta}>{mail.subject || "Ohne Betreff"}</Text>
              </View>
            </View>
          ))}
          {relevantMails.length === 0 && <EmptyState icon="mail" text="Keine relevanten Mails geladen." />}
        </Card>

        <Card onPress={() => navigateTo("Tasks")}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Fällige Aufgaben</Text>
            <Badge value={dueTasks.length} />
          </View>
          {dueTasks.map((task) => (
            <View key={task.id} style={styles.homeListRow}>
              <Chip label={task.due_date < todayIso ? "überfällig" : "heute"} color={task.due_date < todayIso ? colors.danger : colors.warn} />
              <Text style={[styles.cardBody, { flex: 1 }]}>{task.title}</Text>
            </View>
          ))}
          {dueTasks.length === 0 && <EmptyState icon="check" text="Keine fälligen Aufgaben für heute." />}
        </Card>

        <Card onPress={() => navigateTo("Mehr", "Lernen")}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Friday lernt gerade</Text>
            <Badge value={learningCount} />
          </View>
          <Text style={styles.cardBody}>
            {learningCount ? `${learningCount} offene Frage(n) - jetzt beantworten.` : "Keine offenen Lernfragen. Friday bleibt bereit."}
          </Text>
        </Card>
      </View>
    );
  };

  const renderMoreScreen = () => (
    <View>
      <SectionTitle>{t("nav.Mehr")}</SectionTitle>
      {moreScreens.map((item) => (
        <TouchableOpacity
          key={item.key}
          style={styles.moreItem}
          onPress={() => navigateTo("Mehr", item.key)}
          activeOpacity={0.75}
        >
          <View style={styles.moreIcon}>
            <LineIcon name={item.icon} color={colors.accentStrong} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.cardTitle}>{t(`more.${item.key}.label`)}</Text>
            <Text style={styles.cardMeta}>{t(`more.${item.key}.description`)}</Text>
          </View>
          {item.key === "Lernen" && <Badge value={openLearningCount} />}
        </TouchableOpacity>
      ))}
      <AlarmSettings colors={colors} styles={styles} />
      <View style={styles.moreItem}>
        <View style={{ flex: 1 }}>
          <Text style={styles.cardTitle}>{t("common.language")}</Text>
        </View>
        {SUPPORTED_LOCALES.map((code) => (
          <TouchableOpacity
            key={code}
            onPress={() => changeLocale(code)}
            activeOpacity={0.75}
            style={{
              paddingHorizontal: 12,
              paddingVertical: 6,
              marginLeft: 8,
              borderRadius: 8,
              backgroundColor: locale === code ? colors.accentStrong : colors.surface,
            }}
          >
            <Text
              style={[
                styles.cardMeta,
                locale === code && { color: colors.surface, fontWeight: "700" },
              ]}
            >
              {code.toUpperCase()}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const renderScreenContent = () => {
    if (currentScreen === "Home") {
      return renderHomeScreen();
    }
    if (currentScreen === "Mehr") {
      return renderMoreScreen();
    }
    if (currentScreen === "Dashboard") {
      const summary = dashboard?.summary || {};
      return (
        <View>
          <View style={styles.statGrid}>
            <StatCard label="Offene Aufgaben" value={summary.open_tasks || 0} tint={colors.accent} />
            <StatCard label="Nachrichten" value={summary.messages || 0} tint={colors.sage} />
            <StatCard label="Termine heute" value={summary.calendar_items_today || 0} tint={colors.warn} />
            <StatCard label="Kontakte" value={summary.contacts || 0} tint={colors.danger} />
          </View>
          <Text style={styles.dashboardDate}>Stand: {dashboard?.date || "-"}</Text>
        </View>
      );
    }

    if (currentScreen === "Tasks") {
      return (
        <View>
          <SectionTitle>Aufgabe erfassen</SectionTitle>
          <View style={styles.inputRow}>
            <TextInput
              value={newTaskTitle}
              onChangeText={setNewTaskTitle}
              style={styles.input}
              placeholder="Neue Aufgabe eingeben…"
              placeholderTextColor={colors.textSoft}
              onSubmitEditing={handleCreateTask}
              returnKeyType="done"
            />
            <ActionButton label="Hinzufügen" onPress={handleCreateTask} disabled={actionBusy} />
          </View>
          <View style={styles.forwardBox}>
            <Text style={styles.forwardLabel}>Weiterleiten an Kollege</Text>
            <TextInput
              value={newTaskForwardTo}
              onChangeText={setNewTaskForwardTo}
              style={styles.input}
              placeholder="Name eingeben - lokal, kein Versand"
              placeholderTextColor={colors.textSoft}
              returnKeyType="done"
            />
          </View>
          {forwardTask && (
            <View style={styles.forwardPanel}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>Weiterleiten vorbereiten</Text>
                <Chip label="Entwurf" color={colors.warn} />
              </View>
              <Text style={styles.cardMeta}>Aufgabe: {forwardTask.title}</Text>
              <Text style={styles.forwardLabel}>Kontakt auswählen</Text>
              {contacts.map((contact) => (
                <TouchableOpacity
                  key={contact.id ?? contact.name}
                  style={[
                    styles.contactChoice,
                    forwardContact?.id === contact.id && styles.contactChoiceActive,
                  ]}
                  onPress={() => selectForwardContact(contact)}
                  activeOpacity={0.7}
                >
                  <Text style={styles.contactChoiceText}>{contact.name || "Unbekannt"}</Text>
                  <Text style={styles.cardMeta}>
                    {contact.contact_type || "work"}
                    {contact.email_address ? ` | ${contact.email_address}` : ""}
                    {contact.whatsapp_target ? ` | WhatsApp: ${contact.whatsapp_target}` : ""}
                  </Text>
                </TouchableOpacity>
              ))}
              {contacts.length === 0 && (
                <Text style={styles.cardMeta}>Noch keine Kontakte gespeichert. Lege unten im Kontakte-Tab einen Kontakt an.</Text>
              )}
              <Text style={styles.forwardLabel}>Kanal auswählen</Text>
              <View style={styles.row}>
                <ActionButton
                  small
                  variant={forwardChannel === "email" ? "success" : "ghost"}
                  label="E-Mail"
                  onPress={() => selectForwardChannel("email")}
                />
                <ActionButton
                  small
                  variant={forwardChannel === "whatsapp" ? "success" : "ghost"}
                  label="WhatsApp"
                  onPress={() => selectForwardChannel("whatsapp")}
                />
              </View>
              {!!forwardDraft && (
                <View style={styles.draftBox}>
                  <Text style={styles.forwardLabel}>Automatischer Entwurf</Text>
                  <Text style={styles.draftText}>{forwardDraft}</Text>
                </View>
              )}
              {!!forwardMockResult && (
                <View style={styles.mockResultBox}>
                  <Text style={styles.mockResultText}>{forwardMockResult}</Text>
                </View>
              )}
              {!!forwardDraft && (
                <View style={styles.approvalBox}>
                  <Text style={styles.forwardLabel}>Freigabe-Token vorbereiten</Text>
                  <Text style={styles.cardMeta}>
                    Für echten Versand wäre exakt `{approvalTokenFor(forwardChannel)}` nötig.
                  </Text>
                  <TextInput
                    value={forwardApprovalToken}
                    onChangeText={setForwardApprovalToken}
                    style={styles.input}
                    placeholder={approvalTokenFor(forwardChannel)}
                    placeholderTextColor={colors.textSoft}
                    autoCapitalize="characters"
                    returnKeyType="done"
                  />
                  <ActionButton
                    small
                    variant="ghost"
                    label="Freigabe prüfen"
                    onPress={() => openTokenModal({ title: "Versandfreigabe", explanation: "Friday öffnet nur die externe App. Es wird nicht automatisch gesendet.", expectedToken: approvalTokenFor(forwardChannel), onConfirm: checkForwardApprovalToken })}
                    disabled={forwardApprovalToken.trim() !== approvalTokenFor(forwardChannel)}
                  />
                  {!!forwardApprovalResult && (
                    <Text style={styles.approvalResultText}>{forwardApprovalResult}</Text>
                  )}
                  {forwardTokenApproved && hasForwardTarget(forwardContact, forwardChannel) && !!forwardDeepLink && (
                    <ActionButton
                      small
                      variant="success"
                      label={forwardChannel === "whatsapp" ? "In WhatsApp öffnen" : "Als E-Mail öffnen"}
                      onPress={openForwardExternalApp}
                    />
                  )}
                  {forwardTokenApproved &&
                    forwardChannel === "email" &&
                    emailAccountStatus?.real_email_enabled &&
                    hasForwardTarget(forwardContact, forwardChannel) && (
                      <ActionButton
                        small
                        variant="success"
                        label="Jetzt durch Friday senden"
                        onPress={sendForwardEmailThroughFriday}
                        disabled={actionBusy}
                      />
                    )}
                  {forwardTokenApproved && (!hasForwardTarget(forwardContact, forwardChannel) || !forwardDeepLink) && (
                    <Text style={styles.approvalResultText}>
                      Kein öffnungsfähiges Ziel für {channelLabel(forwardChannel)} vorhanden.
                    </Text>
                  )}
                  {!!forwardExternalOpenResult && (
                    <Text style={styles.approvalResultText}>{forwardExternalOpenResult}</Text>
                  )}
                </View>
              )}
              {!!forwardAuditPreview && (
                <View style={styles.auditBox}>
                  <Text style={styles.forwardLabel}>Lokale Audit-Vorschau</Text>
                  <Text style={styles.auditText}>{forwardAuditPreview}</Text>
                </View>
              )}
              <Text style={styles.forwardSafety}>
                Friday öffnet nach Token nur deine externe App mit Textvorschau. Den Versand bestätigst du selbst.
              </Text>
              <ActionButton small variant="ghost" label="Entwurf schließen" onPress={closeForwardFlow} />
            </View>
          )}
          <SectionTitle>Offene Aufgaben</SectionTitle>
          {tasks.map((task) => (
            <View key={task.id} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{task.title}</Text>
                <Chip label={toPriorityLabel(task.priority)} color={priorityColor(task.priority)} />
              </View>
              <Text style={styles.cardMeta}>
                #{task.id} | {task.category || "allgemein"} | {task.status || "open"}
                {task.due_date ? ` | fällig ${formatDate(task.due_date)}` : ""}
                {task.snoozed_until ? ` | verschoben bis ${formatDate(task.snoozed_until)}` : ""}
              </Text>
              {!!task.notes && <Text style={styles.cardBody}>{task.notes}</Text>}
              <View style={styles.row}>
                <ActionButton
                  small
                  variant="success"
                  label="Erledigt"
                  onPress={() => handleCompleteTask(task.id)}
                  disabled={actionBusy}
                />
                <ActionButton
                  small
                  variant="ghost"
                  label="Auf morgen"
                  onPress={() => handleSnoozeTask(task.id)}
                  disabled={actionBusy}
                />
                <ActionButton
                  small
                  variant="ghost"
                  label="Weiterleiten"
                  onPress={() => openForwardFlow(task)}
                  disabled={actionBusy}
                />
                <ActionButton
                  small
                  variant="ghost"
                  label="Archiv"
                  onPress={() => handleArchiveTask(task.id)}
                  disabled={actionBusy}
                />
                <ActionButton
                  small
                  variant="danger"
                  label="Löschen"
                  onPress={() => handleDeleteTask(task.id)}
                  disabled={actionBusy}
                />
              </View>
            </View>
          ))}
          {tasks.length === 0 && <EmptyState icon="check" text="Alles erledigt - keine Aufgaben offen." />}
        </View>
      );
    }

    if (currentScreen === "Nachrichten") {
      const inboxGroups = groupInboxItems({
        messages,
        emailItems: isArray(emailInbox?.items),
        mailItems: isArray(msMailInbox?.items),
        whatsappItems: isArray(whatsappInbox?.items),
      });
      return (
        <View>
          <SectionTitle>Posteingang ({inboxGroups.length} Kontakte)</SectionTitle>
          <View style={styles.card}>
            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>E-Mail</Text>
              <Chip label={emailInbox?.connected ? "verbunden" : "nicht verbunden"} color={emailInbox?.connected ? colors.sage : colors.textSoft} />
            </View>
            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>Microsoft / Gmail</Text>
              <Chip label={msMailInbox?.status?.read_enabled ? "verbunden" : "nicht verbunden"} color={msMailInbox?.status?.read_enabled ? colors.sage : colors.textSoft} />
            </View>
            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>WhatsApp</Text>
              <Chip label={whatsappInbox?.status?.read_enabled ? "verbunden" : "nicht verbunden"} color={whatsappInbox?.status?.read_enabled ? colors.sage : colors.textSoft} />
            </View>
            <Text style={styles.forwardSafety}>
              Nachrichten derselben Person werden als ein Verlauf zusammengefasst. Erledigte WhatsApp-Verläufe verschwinden automatisch aus dieser Ansicht.
            </Text>
            <View style={styles.row}>
              <ActionButton small variant="ghost" label="Mails synchronisieren" onPress={handleSyncMsMail} disabled={actionBusy} />
              <ActionButton small variant="ghost" label={msMailIncludeAll ? "Nur relevante" : "Alle anzeigen"} onPress={handleToggleMsMailIncludeAll} disabled={actionBusy} />
            </View>
          </View>

          {inboxGroups.map((group) => {
            const expanded = Boolean(expandedInboxGroups[group.key]);
            const latest = group.items[0];
            return (
              <View key={group.key} style={styles.card}>
                <TouchableOpacity
                  activeOpacity={0.78}
                  onPress={() => setExpandedInboxGroups((current) => ({ ...current, [group.key]: !expanded }))}
                >
                  <View style={styles.cardHeader}>
                    <View style={styles.row}>
                      <Avatar name={group.sender} />
                      <View>
                        <Text style={styles.cardTitle}>{group.sender}</Text>
                        <Text style={styles.cardMeta}>{group.count} Nachricht{group.count === 1 ? "" : "en"} · {group.sources.join(" / ")}</Text>
                      </View>
                    </View>
                    <Chip label={expanded ? "schliessen" : "oeffnen"} color={colors.accent} />
                  </View>
                  {!expanded && (
                    <>
                      <Text style={styles.cardMeta}>{latest?.receivedAt || ""}</Text>
                      <Text style={styles.cardBody} numberOfLines={2}>{latest?.body || latest?.title || ""}</Text>
                    </>
                  )}
                </TouchableOpacity>

                {expanded && group.items.map((entry) => (
                  <View key={entry.key} style={styles.cardCompact}>
                    <View style={styles.cardHeader}>
                      <Text style={styles.cardMeta}>{entry.sourceLabel} · {entry.receivedAt || ""}</Text>
                      <Chip label={entry.sourceLabel} color={entry.source === "whatsapp" ? colors.sage : colors.accent} />
                    </View>
                    {!!entry.title && entry.title !== "Nachricht" && <Text style={styles.cardTitle}>{entry.title}</Text>}
                    <Text style={styles.cardBody}>{entry.body || ""}</Text>
                    <View style={styles.row}>
                      {!!entry.localMessageId && (
                        <>
                          <ActionButton small variant="light" label="Antwort" onPress={() => handleMessageSuggestionReply(entry.localMessageId)} disabled={actionBusy} />
                          <ActionButton small variant="ghost" label="Aufgabe" onPress={() => handleGenerateTaskSuggestionForMessage(entry.localMessageId)} disabled={actionBusy} />
                          <ActionButton small variant="ghost" label="Termin" onPress={() => handleGenerateCalendarSuggestionForMessage(entry.localMessageId)} disabled={actionBusy} />
                        </>
                      )}
                      {["ms_mail", "imap_mail"].includes(entry.source) && (
                        <ActionButton small variant="ghost" label="Details" onPress={() => handleOpenMsMailDetail(entry.raw)} disabled={actionBusy} />
                      )}
                      <ActionButton small variant="danger" label="Spam" onPress={() => handleMarkMessageSpam(entry.source, entry.spamRef, group.sender)} disabled={actionBusy} />
                    </View>
                  </View>
                ))}

                {!senderHasContact(group.sender, contacts) && expanded && (
                  <View style={styles.assignmentBox}>
                    <Text style={styles.forwardLabel}>Unbekannter Absender</Text>
                    <View style={styles.row}>
                      {contactTypeOptions.map((option) => {
                        const draft = senderAssignmentDrafts[group.sender] || { contact_type: "arbeit", betreuer: "philip" };
                        return (
                          <ActionButton
                            key={`${group.key}-${option.value}`}
                            small
                            variant={draft.contact_type === option.value ? "success" : "ghost"}
                            label={option.label}
                            onPress={() => updateSenderAssignmentDraft(group.sender, { contact_type: option.value })}
                          />
                        );
                      })}
                    </View>
                    <ActionButton small variant="ghost" label="Kontakt speichern" onPress={() => handleAssignSenderContact(group.sender)} disabled={actionBusy} />
                  </View>
                )}
              </View>
            );
          })}
          {inboxGroups.length === 0 && <EmptyState icon="mail" text="Keine offenen Nachrichten." />}
          {!!senderAssignmentResult && <Text style={styles.approvalResultText}>{senderAssignmentResult}</Text>}
          {!!calendarSuggestionResult && (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Termin-Erkennung</Text>
              <Text style={styles.cardBody}>{calendarSuggestionResult}</Text>
            </View>
          )}

          {(messageSuggestions.length > 0 || taskSuggestions.length > 0) && <SectionTitle>Offene Vorschlaege</SectionTitle>}
          {messageSuggestions.map((suggestion) => (
            <View key={suggestion.id} style={styles.card}>
              <Text style={styles.cardBody}>{suggestion.draft_text || "(keine Vorlage)"}</Text>
              <View style={styles.row}>
                <ActionButton small variant="success" label="Annehmen" onPress={() => handleMessageSuggestionDecision(suggestion.id, "approved")} disabled={actionBusy || suggestion.id.toString().startsWith("preview-")} />
                <ActionButton small variant="danger" label="Ablehnen" onPress={() => handleMessageSuggestionDecision(suggestion.id, "rejected")} disabled={actionBusy || suggestion.id.toString().startsWith("preview-")} />
              </View>
            </View>
          ))}
          {taskSuggestions.map((suggestion) => (
            <View key={suggestion.id} style={styles.card}>
              <Text style={styles.cardTitle}>{suggestion.title}</Text>
              {!!suggestion.notes && <Text style={styles.cardBody}>{suggestion.notes}</Text>}
              <View style={styles.row}>
                <ActionButton small variant="success" label="Annehmen" onPress={() => handleTaskSuggestionDecision(suggestion.id, "approved")} disabled={actionBusy} />
                <ActionButton small variant="danger" label="Ablehnen" onPress={() => handleTaskSuggestionDecision(suggestion.id, "rejected")} disabled={actionBusy} />
              </View>
            </View>
          ))}
        </View>
      );
    }

    if (currentScreen === "Spam") {
      const totalSpam =
        spamMessages.messages.length + spamMessages.msMail.length + spamMessages.whatsapp.length;
      return (
        <View>
          <SectionTitle>Spam / Blockiert</SectionTitle>
          <View style={styles.privacyBanner}>
            <LineIcon name="alert" color={colors.accentStrong} />
            <Text style={styles.privacyBannerText}>
              Alles hier ist lokal. Friday verschiebt oder löscht nichts im echten Postfach.
            </Text>
          </View>
          {!!spamResult && <Text style={styles.approvalResultText}>{spamResult}</Text>}

          <SectionTitle>Blockierte Absender ({blockedSenders.length})</SectionTitle>
          {blockedSenders.map((sender) => (
            <View key={sender.id} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{sender.label || sender.sender_key}</Text>
                <Chip label={sender.source || "lokal"} color={colors.danger} />
              </View>
              <Text style={styles.cardMeta}>Blockiert seit: {sender.created_at || "-"}</Text>
              <ActionButton
                small
                variant="ghost"
                label="Entblocken / Wiederherstellen"
                onPress={() => handleUnblockSender(sender.id)}
                disabled={actionBusy}
              />
            </View>
          ))}
          {blockedSenders.length === 0 && (
            <View style={styles.card}>
              <Text style={styles.cardBody}>Keine lokal blockierten Absender.</Text>
            </View>
          )}

          <SectionTitle>Lokale Spam-Nachrichten ({totalSpam})</SectionTitle>
          {spamMessages.messages.map((message) => (
            <View key={`message-${message.id}`} style={styles.card}>
              <Text style={styles.cardTitle}>{message.sender || "Unbekannt"}</Text>
              <Text style={styles.cardMeta}>Lokale Nachricht #{message.id}</Text>
              <Text style={styles.cardBody}>{message.text || ""}</Text>
            </View>
          ))}
          {spamMessages.msMail.map((item) => (
            <View key={`ms-${item.message_id || item.id}`} style={styles.card}>
              <Text style={styles.cardTitle}>{item.subject || "(ohne Betreff)"}</Text>
              <Text style={styles.cardMeta}>Von: {item.sender || "-"}</Text>
              <Text style={styles.cardMeta}>Quelle: {item.source === "imap_mail" ? "Gmail" : "Microsoft"} / Postfach: {item.account_username || item.account_id || "-"}</Text>
              <Text style={styles.cardBody}>{item.snippet || ""}</Text>
            </View>
          ))}
          {spamMessages.whatsapp.map((item) => (
            <View key={`wa-${item.id}`} style={styles.card}>
              <Text style={styles.cardTitle}>{item.sender_name || "WhatsApp"}</Text>
              <Text style={styles.cardMeta}>Nummer: {item.sender_number_masked || "hash:unknown"}</Text>
              <Text style={styles.cardBody}>{item.body || ""}</Text>
            </View>
          ))}
          {totalSpam === 0 && (
            <EmptyState icon="alert" text="Keine lokalen Spam-Nachrichten." />
          )}
        </View>
      );
    }

    if (currentScreen === "Kalender") {
      const items = isArray(calendar?.merged_items || calendar?.items || calendar?.calendar_items || []);
      const googleConnected = Boolean(calendarAccountStatus?.google?.connected);
      const policies = isArray(accountPolicies?.items || accountPolicies?.policies || accountPolicies);
      const weekDays = buildWeekDays(weekCalendar, googleCalendarPreview);
      const weekTodayKey = formatDateOnly(new Date());
      const weekFirst = weekDays[0];
      const weekLast = weekDays[weekDays.length - 1];
      const upcomingItems = [...items]
        .sort((left, right) => String(left.start || left.date || "").localeCompare(String(right.start || right.date || "")))
        .slice(0, 12);
      return (
        <View>
          <SectionTitle>Verbundene Kalender</SectionTitle>
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>Google Kalender</Text>
              <Chip label={googleConnected ? "verbunden" : "nicht verbunden"} color={googleConnected ? colors.sage : colors.textSoft} />
            </View>
            <Text style={styles.cardMeta}>{calendarAccountStatus?.google?.calendar_id || "Kein Google-Kalender verbunden"}</Text>
          </View>
          {policies.map((policy, index) => (
            <View key={policy.id || `${policy.provider || "calendar"}-${index}`} style={styles.cardCompact}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{policy.label || policy.name || policy.provider || "Kalenderquelle"}</Text>
                <Chip label={policy.enabled === false ? "pausiert" : "verbunden"} color={policy.enabled === false ? colors.textSoft : colors.sage} />
              </View>
              <Text style={styles.cardMeta}>{policy.provider || policy.role || "lokale Kalenderquelle"}</Text>
            </View>
          ))}
          {!googleConnected && policies.length === 0 && <EmptyState icon="calendar" text="Noch kein Kalender verbunden." />}

          <SectionTitle>Wochenkalender</SectionTitle>
          <Text style={styles.cardMeta}>
            {weekdayLabel(weekFirst.date)} {shortDateLabel(weekFirst.date)} bis {weekdayLabel(weekLast.date)} {shortDateLabel(weekLast.date)}
          </Text>
          <View style={styles.weekGrid}>
            {weekDays.map((day) => {
              const isToday = day.key === weekTodayKey;
              const visibleEvents = day.events.slice(0, 4);
              const hiddenCount = day.events.length - visibleEvents.length;
              return (
                <View key={day.key} style={[styles.weekTile, isToday && styles.weekTileToday]}>
                  <View style={styles.weekTileHeader}>
                    <Text style={[styles.weekTileDay, isToday && styles.weekTileDayToday]}>{isToday ? "Heute" : weekdayLabel(day.date)}</Text>
                    <Text style={styles.weekTileDate}>{shortDateLabel(day.date)}</Text>
                  </View>
                  <Text style={[styles.weekTileHours, day.hours === 0 && styles.weekTileHoursFree]}>{day.hours > 0 ? `${formatHoursLabel(day.hours)} verplant` : "frei"}</Text>
                  {visibleEvents.map((entry, index) => (
                    <Text key={`${day.key}-event-${index}`} style={styles.weekTileEvent} numberOfLines={1}>
                      {eventTimeLabel(entry) ? `${eventTimeLabel(entry)} · ` : ""}{entry.title || entry.summary || "Termin"}
                    </Text>
                  ))}
                  {hiddenCount > 0 && <Text style={styles.weekTileMore}>+{hiddenCount} weitere</Text>}
                </View>
              );
            })}
          </View>

          <SectionTitle>Anstehende Termine</SectionTitle>
          {upcomingItems.map((entry) => (
            <View key={`${entry.provider || entry.item_type || "local"}-${entry.id ?? `${entry.date}-${entry.start}`}`} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{entry.title || entry.summary || "Termin"}</Text>
                <Chip label={entry.policy_label || entry.provider || entry.item_type || "Kalender"} color={colors.accent} />
              </View>
              <Text style={styles.cardMeta}>{formatCalendarMoment(entry.start)} - {formatCalendarMoment(entry.end)}</Text>
              {!!entry.location && <Text style={styles.cardMeta}>Ort: {entry.location}</Text>}
            </View>
          ))}
          {upcomingItems.length === 0 && <EmptyState icon="calendar" text="Keine anstehenden Termine in dieser Woche." />}
        </View>
      );
    }

    if (currentScreen === "Kontakte") {
      return (
        <View>
          <SectionTitle>Kontakt erfassen</SectionTitle>
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Häufigen Kontakt speichern</Text>
            <TextInput
              value={newContactName}
              onChangeText={setNewContactName}
              style={styles.input}
              placeholder="Name der Person"
              placeholderTextColor={colors.textSoft}
              returnKeyType="done"
            />
            <TextInput
              value={newContactEmail}
              onChangeText={setNewContactEmail}
              style={[styles.input, styles.inputStacked]}
              placeholder="E-Mail-Adresse optional"
              placeholderTextColor={colors.textSoft}
              keyboardType="email-address"
              autoCapitalize="none"
              returnKeyType="done"
            />
            <TextInput
              value={newContactWhatsapp}
              onChangeText={setNewContactWhatsapp}
              style={[styles.input, styles.inputStacked]}
              placeholder="WhatsApp-Ziel optional"
              placeholderTextColor={colors.textSoft}
              keyboardType="phone-pad"
              returnKeyType="done"
            />
            <Text style={styles.forwardLabel}>Kontaktart</Text>
            <View style={styles.row}>
              {contactTypeOptions.map((option) => (
                <ActionButton
                  key={`new-contact-${option.value}`}
                  small
                  variant={newContactType === option.value ? "success" : "ghost"}
                  label={option.label}
                  onPress={() => setNewContactType(option.value)}
                />
              ))}
            </View>
            {newContactType === "kunde" && (
              <>
                <Text style={styles.forwardLabel}>Betreuer</Text>
                <View style={styles.row}>
                  {betreuerOptions.map((option) => (
                    <ActionButton
                      key={`new-contact-betreuer-${option.value}`}
                      small
                      variant={newContactBetreuer === option.value ? "success" : "ghost"}
                      label={option.label}
                      onPress={() => setNewContactBetreuer(option.value)}
                    />
                  ))}
                </View>
              </>
            )}
            <TextInput
              value={newContactNotes}
              onChangeText={setNewContactNotes}
              style={[styles.input, styles.inputStacked]}
              placeholder="Notiz, z.B. E-Mail oder WhatsApp-Name"
              placeholderTextColor={colors.textSoft}
              returnKeyType="done"
            />
            <ActionButton
              label="Kontakt lokal speichern"
              onPress={handleCreateContact}
              disabled={actionBusy || !newContactName.trim()}
            />
            <Text style={styles.forwardSafety}>
              Kontakt wird nur lokal gespeichert. Es wird keine Nachricht gesendet.
            </Text>
          </View>
          <SectionTitle>Kontakte</SectionTitle>
          {contacts.map((contact) => (
            <View key={contact.id ?? contact.name} style={styles.card}>
              <View style={styles.cardHeader}>
                <View style={styles.contactRow}>
                  <View style={styles.avatar}>
                    <Text style={styles.avatarText}>
                      {(contact.name || "?").trim().charAt(0).toUpperCase()}
                    </Text>
                  </View>
                  <Text style={styles.cardTitle}>{contact.name || "Unbekannt"}</Text>
                </View>
                <Chip label={contact.contact_type || "other"} color={colors.sage} />
              </View>
              {!!contact.notes && <Text style={styles.cardBody}>{contact.notes}</Text>}
              {contact.contact_type === "kunde" && !!contact.betreuer && (
                <Text style={styles.cardMeta}>
                  Betreuer: {betreuerLabel(contact.betreuer)}
                </Text>
              )}
              {!!contact.email_address && <Text style={styles.cardMeta}>E-Mail: {contact.email_address}</Text>}
              {!!contact.whatsapp_target && <Text style={styles.cardMeta}>WhatsApp: {contact.whatsapp_target}</Text>}
              <TextInput
                value={contactNotesDrafts[contact.id] ?? contact.notes ?? ""}
                onChangeText={(value) =>
                  setContactNotesDrafts((current) => ({ ...current, [contact.id]: value }))
                }
                style={styles.input}
                placeholder="Agent-Notiz fuer diese Person"
                placeholderTextColor={colors.textSoft}
                multiline
              />
              <ActionButton
                small
                variant="ghost"
                label="Kontakt-Notiz speichern"
                onPress={() => handleSaveContactNotes(contact)}
                disabled={actionBusy}
              />
            </View>
          ))}
          {!!contactNotesResult && <Text style={styles.approvalResultText}>{contactNotesResult}</Text>}
          {contacts.length === 0 && <EmptyState icon="contacts" text="Keine Kontakte." />}
        </View>
      );
    }

    if (currentScreen === "Lernen") {
      const questions = isArray(learning?.open_questions);
      const rules = isArray(learning?.learned_rules);
      return (
        <View>
          <View style={styles.privacyBanner}>
            <LineIcon name="learning" color={colors.accentStrong} />
            <Text style={styles.privacyBannerText}>
              Lernen speichert lokale Regeln und Präferenzen. Das ist kein Modell-Nachtraining.
            </Text>
          </View>
          <View style={styles.statGrid}>
            <StatCard label="Offene Fragen" value={learning?.open_count || 0} tint={colors.accent} />
            <StatCard label="Gelernte Regeln" value={learning?.rule_count || 0} tint={colors.sage} />
          </View>
          {!!learningResult && <Text style={styles.approvalResultText}>{learningResult}</Text>}
          <SectionTitle>Offene Lernfragen</SectionTitle>
          {questions.map((question) => {
            const optionsPayload = question.options || {};
            const options = isArray(optionsPayload.items);
            const evidence = isArray(optionsPayload.evidence);
            return (
              <View key={question.id} style={styles.card}>
                <View style={styles.cardHeader}>
                  <Text style={styles.cardTitle}>{question.question_text}</Text>
                  <Chip label={question.kind || "Routine"} color={colors.warn} />
                </View>
                {evidence.map((item, index) => (
                  <Text key={`${question.id}-evidence-${index}`} style={styles.cardMeta}>
                    Hinweis: {item}
                  </Text>
                ))}
                <View style={styles.row}>
                  {options.map((option) => (
                    <ActionButton
                      key={`${question.id}-${option.id}`}
                      small
                      variant={option.id === "ignorieren" ? "ghost" : "success"}
                      label={option.label || option.id}
                      onPress={() => handleAnswerLearningQuestion(question, option.id)}
                      disabled={actionBusy}
                    />
                  ))}
                </View>
                <ActionButton
                  small
                  variant="ghost"
                  label="Später"
                  onPress={() => handleDismissLearningQuestion(question)}
                  disabled={actionBusy}
                />
              </View>
            );
          })}
          {questions.length === 0 && <EmptyState icon="learning" text="Keine offenen Lernfragen." />}
          <SectionTitle>Bereits gelernt</SectionTitle>
          {rules.map((rule) => (
            <View key={rule.id} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{rule.kind || "Regel"}</Text>
                <Chip label={rule.enabled ? "aktiv" : "inaktiv"} color={rule.enabled ? colors.success : colors.textSoft} />
              </View>
              <Text style={styles.cardMeta}>Schlüssel: {rule.key || "-"}</Text>
              <Text style={styles.cardBody}>{JSON.stringify(rule.value || {}, null, 2)}</Text>
              <ActionButton
                small
                variant={rule.enabled ? "ghost" : "success"}
                label={rule.enabled ? "Regel deaktivieren" : "Regel aktivieren"}
                onPress={() => handleToggleLearnedRule(rule)}
                disabled={actionBusy}
              />
            </View>
          ))}
          {rules.length === 0 && <EmptyState icon="learning" text="Noch keine Regeln gelernt." />}
          <Text style={styles.forwardSafety}>
            Alle Lernregeln bleiben lokal. Friday sendet dadurch keine Nachrichten und erstellt keine Termine automatisch.
          </Text>
        </View>
      );
    }

    if (currentScreen === "Datenschutz") {
      const external = privacy?.external_services || {};
      const writes = privacy?.writes || {};
      const note = privacy?.notes || "";
      const services = [
        ["E-Mail", external.email],
        ["WhatsApp", external.whatsapp],
        ["SMS", external.sms],
        ["Kalender", external.calendar],
        ["Wetter", external.weather],
        ["Musik", external.music],
      ];
      const writeRows = [
        ["Exporte", writes.exports],
        ["Nachrichten senden", writes.messages_send],
        ["Kontakte ändern", writes.contacts_write],
      ];
      const boundaryRows = [
        ["E-Mail-Versand gesperrt", !external.email],
        ["WhatsApp-Versand gesperrt", !external.whatsapp],
        ["SMS gesperrt", !external.sms],
        ["Cloud-KI gesperrt", true],
        ["Schreibaktionen tokenpflichtig", !writes.messages_send && !writes.contacts_write],
      ];
      return (
        <View>
          <View style={styles.privacyHero}>
            <View style={styles.privacyHeroTop}>
              <View style={styles.privacyHeroIcon}>
                <LineIcon name="privacy" color={colors.onAccent} />
              </View>
              <Text style={styles.privacyHeroTitle}>Alles läuft lokal</Text>
            </View>
            <Text style={styles.privacyHeroText}>
              Modus: {privacy?.mode || "local"}. Daten bleiben auf deinen Geräten; externe Aktionen sind hart begrenzt.
            </Text>
          </View>
          <SectionTitle>API-Sicherheit</SectionTitle>
          <View style={styles.card}>
            <Text style={styles.cardTitle}>
              Netzwerkzugriff: {apiTokenConfigured ? "Token eingerichtet" : "nur lokal"}
            </Text>
            <Text style={styles.cardBody}>
              Für WLAN, Tailscale oder Tunnel muss derselbe FRIDAY_API_TOKEN auf Server und Handy
              eingerichtet sein. Der Token wird ausschließlich im Geräte-Keystore gespeichert.
            </Text>
            <TextInput
              value={apiTokenDraft}
              onChangeText={setApiTokenDraft}
              style={styles.input}
              placeholder="API-Token einfügen (mindestens 32 Zeichen)"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
              autoCorrect={false}
              secureTextEntry
            />
            <View style={styles.row}>
              <ActionButton
                small
                variant="success"
                label="Token sicher speichern"
                onPress={() => handleSaveApiToken(false)}
                disabled={actionBusy || !apiTokenDraft.trim()}
              />
              {apiTokenConfigured && (
                <ActionButton
                  small
                  variant="ghost"
                  label="Token entfernen"
                  onPress={() => handleSaveApiToken(true)}
                  disabled={actionBusy}
                />
              )}
            </View>
            {!!apiTokenResult && <Text style={styles.approvalResultText}>{apiTokenResult}</Text>}
          </View>
          <SectionTitle>Status</SectionTitle>
          <View style={styles.card}>
            {services.map(([label, value]) => (
              <ListRow key={label}>
                <Text style={styles.privacyLabel}>{label}</Text>
                <PrivacyStatusPill active={Boolean(value)} inactiveLabel="AUS" />
              </ListRow>
            ))}
            {writeRows.map(([label, value]) => (
              <ListRow key={label}>
                <Text style={styles.privacyLabel}>{label}</Text>
                <PrivacyStatusPill active={Boolean(value)} inactiveLabel="DEAKTIVIERT" />
              </ListRow>
            ))}
          </View>
          {!!note && <Text style={styles.privacyNote}>{note}</Text>}
          <SectionTitle>Lokale Grenzen</SectionTitle>
          <View style={styles.card}>
            {boundaryRows.map(([label, enabled]) => (
              <ListRow key={label}>
                <Text style={styles.privacyLabel}>{label}</Text>
                <ToggleSwitch enabled={Boolean(enabled)} />
              </ListRow>
            ))}
          </View>
          <SectionTitle>Konten</SectionTitle>
          <View style={styles.card}>
            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>E-Mail-Konto</Text>
              <Chip
                label={emailAccountStatus?.connected ? "verbunden" : "nicht verbunden"}
                color={emailAccountStatus?.connected ? colors.sage : colors.textSoft}
              />
            </View>
            <Text style={styles.cardMeta}>
              Real-Versand: {emailAccountStatus?.real_email_enabled ? "aktiv" : "aus"}
            </Text>
            <Text style={styles.cardMeta}>
              Letzter Test OK: {emailAccountStatus?.last_test_ok ? "ja" : "nein"}
            </Text>
            <Text style={styles.cardMeta}>
              Agent-Notiz vorhanden: {emailAccountStatus?.agent_notes_configured ? "ja" : "nein"}
            </Text>
            <Text style={styles.forwardSafety}>
              Am sichersten verbindest du das Konto direkt am PC. Ueber Handy wird das App-Passwort zur lokalen PC-API gesendet:
              Tailscale ist verschluesselt, Heim-LAN-HTTP nicht.
            </Text>
            <TextInput
              value={emailPreset}
              onChangeText={setEmailPreset}
              style={styles.input}
              placeholder="Preset: gmail/outlook/gmx/web.de"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <TextInput
              value={emailAddress}
              onChangeText={setEmailAddress}
              style={styles.input}
              placeholder="E-Mail-Adresse"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
              keyboardType="email-address"
            />
            <TextInput
              value={emailUsername}
              onChangeText={setEmailUsername}
              style={styles.input}
              placeholder="Benutzername (leer = E-Mail)"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <TextInput
              value={emailAppPassword}
              onChangeText={setEmailAppPassword}
              style={styles.input}
              placeholder="App-Passwort"
              placeholderTextColor={colors.textSoft}
              secureTextEntry
              autoCapitalize="none"
            />
            <TextInput
              value={emailAgentNotes}
              onChangeText={setEmailAgentNotes}
              style={styles.input}
              placeholder="Agent-Notiz fuer lokale KI-Entwuerfe"
              placeholderTextColor={colors.textSoft}
              multiline
            />
            <TextInput
              value={emailAccountToken}
              onChangeText={setEmailAccountToken}
              style={styles.input}
              placeholder="KONTO SPEICHERN"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <View style={styles.row}>
              <ActionButton
                small
                variant="success"
                label="Konto verbinden"
                onPress={() => openTokenModal({ title: "E-Mail-Konto speichern", explanation: "Das Konto wird lokal am PC gespeichert. Real-Versand bleibt aus.", expectedToken: "KONTO SPEICHERN", onConfirm: handleConnectEmailAccount })}
                disabled={actionBusy || emailAccountToken.trim() !== "KONTO SPEICHERN"}
              />
              <ActionButton
                small
                variant="ghost"
                label="Verbindung testen"
                onPress={handleTestEmailAccount}
                disabled={actionBusy}
              />
            </View>
            {!!emailAccountResult && <Text style={styles.approvalResultText}>{emailAccountResult}</Text>}
            {emailAccountStatus?.connected && (
              <ActionButton
                small
                variant="ghost"
                label="E-Mail-Agent-Notiz speichern"
                onPress={handleSaveEmailAgentNotes}
                disabled={actionBusy}
              />
            )}
            {!!emailAgentNotesResult && (
              <Text style={styles.approvalResultText}>{emailAgentNotesResult}</Text>
            )}
          </View>

          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>Familienhelden-Postfach (nur lesen)</Text>
              <Chip
                label={msMailStatus?.connected ? "verbunden" : "nicht verbunden"}
                color={msMailStatus?.connected ? colors.sage : colors.textSoft}
              />
            </View>
            <Text style={styles.cardMeta}>
              Lesen aktiv: {msMailStatus?.read_enabled ? "ja" : "nein"} / Real-Versand: {msMailStatus?.real_email_enabled ? "aktiv" : "aus"}
            </Text>
            <Text style={styles.cardMeta}>
              Postfaecher: {msMailStatus?.account_count || 0} / Mindestens ein Test OK: {msMailStatus?.last_test_ok ? "ja" : "nein"}
            </Text>
            {isArray(msMailStatus?.accounts).map((account) => (
              <View key={account.account_id || account.id} style={styles.cardCompact}>
                <Text style={styles.cardTitle}>{account.username_masked || account.account_id}</Text>
                <Text style={styles.cardMeta}>
                  ID: {account.account_id || account.id} / Test OK: {account.last_test_ok ? "ja" : "nein"}
                </Text>
                <View style={styles.row}>
                  <ActionButton
                    small
                    variant="ghost"
                    label="Dieses Postfach synchronisieren"
                    onPress={() => handleSyncMsMail(account.account_id || account.id)}
                    disabled={actionBusy}
                  />
                  <ActionButton
                    small
                    variant="danger"
                    label="Postfach trennen"
                    onPress={() => handleDeleteMsMailAccount(account.account_id || account.id)}
                    disabled={actionBusy}
                  />
                </View>
              </View>
            ))}
            {isArray(msMailStatus?.accounts).length === 0 && (
              <Text style={styles.cardBody}>Noch kein Microsoft-Postfach verbunden.</Text>
            )}
            <Text style={styles.forwardSafety}>
              Microsoft Graph wird nur mit Mail.Read genutzt. Kein Mail.Send, kein automatischer Versand.
            </Text>
            <TextInput
              value={msMailClientId}
              onChangeText={setMsMailClientId}
              style={styles.input}
              placeholder="Azure Client-ID"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <TextInput
              value={msMailTenant}
              onChangeText={setMsMailTenant}
              style={styles.input}
              placeholder="Tenant: common oder Tenant-ID"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <View style={styles.row}>
              <ActionButton
                small
                variant="ghost"
                label="OAuth-Link öffnen"
                onPress={handlePrepareMsMailAuth}
                disabled={actionBusy}
              />
              <ActionButton
                small
                variant="success"
                label="Mail-Sync starten"
                onPress={handleSyncMsMail}
                disabled={actionBusy}
              />
            </View>
            <TextInput
              value={msMailAuthResponse}
              onChangeText={setMsMailAuthResponse}
              style={styles.input}
              placeholder="OAuth-Rückgabe-URL von localhost hier einfügen"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
              multiline
            />
            <TextInput
              value={msMailAccountToken}
              onChangeText={setMsMailAccountToken}
              style={styles.input}
              placeholder="KONTO SPEICHERN"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <ActionButton
              small
              variant="success"
              label="Microsoft-Mail verbinden"
              onPress={() => openTokenModal({ title: "Microsoft-Mail-Konto speichern", explanation: "Das Token-Bundle wird lokal verschlüsselt gespeichert. Mail bleibt read-only.", expectedToken: "KONTO SPEICHERN", onConfirm: handleCompleteMsMailConnect })}
              disabled={actionBusy || msMailAccountToken.trim() !== "KONTO SPEICHERN"}
            />
            <TextInput
              value={msMailDeleteToken}
              onChangeText={setMsMailDeleteToken}
              style={styles.input}
              placeholder="KONTO LOESCHEN zum Trennen eines Postfachs"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <TextInput
              value={msMailActivationToken}
              onChangeText={setMsMailActivationToken}
              style={styles.input}
              placeholder="MAIL LESEN AKTIVIEREN"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <ActionButton
              small
              variant="ghost"
              label="Read-Gate aktivieren"
              onPress={handleActivateMsMailRead}
              disabled={actionBusy}
            />
            {!!msMailResult && <Text style={styles.approvalResultText}>{msMailResult}</Text>}
            {isArray(msMailInbox?.items).slice(0, 3).map((item, index) => (
              <View key={`${item.message_id || "ms-mail-setup"}-${index}`} style={styles.cardCompact}>
                <Text style={styles.cardTitle}>{item.subject || "(ohne Betreff)"}</Text>
                <Text style={styles.cardMeta}>Von: {item.sender || "-"}</Text>
                <Text style={styles.cardBody}>{item.snippet || ""}</Text>
              </View>
            ))}
          </View>
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>Gmail (nur lesen)</Text>
              <Chip
                label={imapMailStatus?.connected ? "verbunden" : "nicht verbunden"}
                color={imapMailStatus?.connected ? colors.sage : colors.textSoft}
              />
            </View>
            <Text style={styles.cardMeta}>
              Lesen aktiv: {imapMailStatus?.read_enabled ? "ja" : "nein"} / Real-Versand: {imapMailStatus?.real_email_enabled ? "aktiv" : "aus"}
            </Text>
            <Text style={styles.cardMeta}>
              Konten: {imapMailStatus?.account_count || 0} / IMAP: imap.gmail.com:993 / SMTP: aus
            </Text>
            <Text style={styles.forwardSafety}>
              Gmail nutzt nur IMAP read-only mit App-Passwort. Friday liest lokal, speichert Vorschauen in SQLite und sendet keine Mail.
            </Text>
            {isArray(imapMailStatus?.accounts).map((account) => (
              <View key={account.account_id || account.id} style={styles.cardCompact}>
                <Text style={styles.cardTitle}>{account.username_masked || account.account_id}</Text>
                <Text style={styles.cardMeta}>
                  ID: {account.account_id || account.id} / Test OK: {account.last_test_ok ? "ja" : "nein"}
                </Text>
                <View style={styles.row}>
                  <ActionButton
                    small
                    variant="ghost"
                    label="Dieses Gmail-Konto synchronisieren"
                    onPress={() => handleSyncImapMail(account.account_id || account.id)}
                    disabled={actionBusy}
                  />
                  <ActionButton
                    small
                    variant="danger"
                    label="Gmail trennen"
                    onPress={() => handleDeleteImapMailAccount(account.account_id || account.id)}
                    disabled={actionBusy}
                  />
                </View>
              </View>
            ))}
            {isArray(imapMailStatus?.accounts).length === 0 && (
              <Text style={styles.cardBody}>Noch kein Gmail-Konto verbunden.</Text>
            )}
            <TextInput
              value={imapMailUsername}
              onChangeText={setImapMailUsername}
              style={styles.input}
              placeholder="Gmail-Adresse"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
              keyboardType="email-address"
            />
            <TextInput
              value={imapMailAppPassword}
              onChangeText={setImapMailAppPassword}
              style={styles.input}
              placeholder="Gmail App-Passwort"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
              secureTextEntry
            />
            <TextInput
              value={imapMailAccountToken}
              onChangeText={setImapMailAccountToken}
              style={styles.input}
              placeholder="KONTO SPEICHERN"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <View style={styles.row}>
              <ActionButton
                small
                variant="success"
                label="Gmail verbinden"
                onPress={() => openTokenModal({ title: "Gmail-Konto speichern", explanation: "Das App-Passwort wird lokal verschluesselt gespeichert. Gmail bleibt read-only.", expectedToken: "KONTO SPEICHERN", onConfirm: handleConnectImapMailAccount })}
                disabled={actionBusy || imapMailAccountToken.trim() !== "KONTO SPEICHERN"}
              />
              <ActionButton
                small
                variant="success"
                label="Gmail-Sync starten"
                onPress={handleSyncImapMail}
                disabled={actionBusy}
              />
            </View>
            <TextInput
              value={imapMailDeleteToken}
              onChangeText={setImapMailDeleteToken}
              style={styles.input}
              placeholder="KONTO LOESCHEN zum Trennen"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <TextInput
              value={imapMailActivationToken}
              onChangeText={setImapMailActivationToken}
              style={styles.input}
              placeholder="MAIL LESEN AKTIVIEREN"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <ActionButton
              small
              variant="success"
              label="Gmail-Read-Gate aktivieren"
              onPress={handleActivateImapMailRead}
              disabled={actionBusy}
            />
            {!!imapMailResult && <Text style={styles.approvalResultText}>{imapMailResult}</Text>}
          </View>          <View style={styles.card}>
            <Text style={styles.cardTitle}>WhatsApp</Text>
            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>Read-Bridge</Text>
              <Chip
                label={whatsappStatus?.read_enabled ? "aktiv" : "aus"}
                color={whatsappStatus?.read_enabled ? colors.warn : colors.textSoft}
              />
            </View>
            <Text style={styles.cardMeta}>
              Verbunden erkannt: {whatsappStatus?.connected ? "ja" : "nein"}
            </Text>
            <Text style={styles.cardMeta}>
              Letzter Empfang: {whatsappStatus?.last_received_at || "-"}
            </Text>
            <Text style={styles.cardMeta}>
              Agent-Notiz vorhanden: {whatsappStatus?.agent_notes_configured ? "ja" : "nein"}
            </Text>
            <Text style={styles.cardBody}>
              WhatsApp-Senden bleibt ueber dein Handy: Friday befuellt die Nachricht, du tippst selbst auf Senden.
              Die Read-Bridge liest nur eingehende Einzelchats und nutzt keine Auto-Antwort.
            </Text>
            <TextInput
              value={whatsappAgentNotes}
              onChangeText={setWhatsappAgentNotes}
              style={styles.input}
              placeholder="WhatsApp-Agent-Notiz fuer lokale KI-Entwuerfe"
              placeholderTextColor={colors.textSoft}
              multiline
            />
            <ActionButton
              small
              variant="ghost"
              label="WhatsApp-Agent-Notiz speichern"
              onPress={handleSaveWhatsAppAgentNotes}
              disabled={actionBusy}
            />
            {!!whatsappAgentNotesResult && (
              <Text style={styles.approvalResultText}>{whatsappAgentNotesResult}</Text>
            )}
            <Text style={styles.forwardSafety}>
              Risiko: WhatsApp-Web-Bridges koennen gegen WhatsApp-Regeln verstossen. Nutzung auf eigenes Risiko.
            </Text>
          </View>
        </View>
      );
    }

    if (currentScreen === "Setup") {
      const safetyFlags = setupStatus?.safety_flags || {};
      const setupSteps = Array.isArray(setupStatus?.setup_steps) ? setupStatus.setup_steps : [];
      return (
        <View>
          <SectionTitle>Setup & Status</SectionTitle>
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>Friday lokal</Text>
              <Chip label={setupStatus?.local_mode ? "lokal" : "prüfen"} color={setupStatus?.local_mode ? colors.success : colors.warn} />
            </View>
            <Text style={styles.cardMeta}>App: {setupStatus?.app_name || "Friday"}</Text>
            <Text style={styles.cardMeta}>Version: {setupStatus?.app_version || "-"}</Text>
            <Text style={styles.cardBody}>
              Setup prüft lokale Module, KI-Status und Safety-Flags. Externe Aktionen bleiben gesperrt.
            </Text>
          </View>

          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>KI & Kalender</Text>
              <Chip label={setupStatus?.ai?.local_ollama_enabled ? "KI aktiv" : "KI aus"} color={setupStatus?.ai?.local_ollama_enabled ? colors.success : colors.textSoft} />
            </View>
            <Text style={styles.cardMeta}>Provider: {setupStatus?.ai?.provider || "-"}</Text>
            <Text style={styles.cardMeta}>Modell: {setupStatus?.ai?.model || "-"}</Text>
            <Text style={styles.cardBody}>
              Termin-Erkennung: KI darf Rohdaten liefern, Python löst Datum und Uhrzeit deterministisch auf.
            </Text>
            <Text style={styles.forwardSafety}>
              Kalender-Schreiben: {setupStatus?.calendar?.real_enabled ? "aktiv" : "aus"} - Vorschläge gehen immer in den Review.
            </Text>
          </View>

          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>Kalender-Konto</Text>
              <Chip
                label={calendarAccountStatus?.google?.connected ? "verbunden" : "nicht verbunden"}
                color={calendarAccountStatus?.google?.connected ? colors.sage : colors.textSoft}
              />
            </View>
            <Text style={styles.cardMeta}>
              Google-Kalender: {calendarAccountStatus?.google?.calendar_id || "noch nicht verbunden"}
            </Text>
            <Text style={styles.cardMeta}>
              Verbindungstest OK: {calendarAccountStatus?.google?.last_test_ok ? "ja" : "nein"}
            </Text>
            <Text style={styles.forwardSafety}>
              OAuth-Anmeldung laeuft am PC. Echte Termine brauchen spaeter exakt `TERMIN SPEICHERN`.
            </Text>
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Account-Policy speichern</Text>
            <TextInput
              value={policyLabel}
              onChangeText={setPolicyLabel}
              style={styles.input}
              placeholder="Label, z.B. Google Hauptkalender"
              placeholderTextColor={colors.textSoft}
            />
            <TextInput
              value={policyProvider}
              onChangeText={setPolicyProvider}
              style={styles.input}
              placeholder="Provider: google_calendar"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <TextInput
              value={policyRole}
              onChangeText={setPolicyRole}
              style={styles.input}
              placeholder="Rolle: main/source"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <TextInput
              value={policyAccess}
              onChangeText={setPolicyAccess}
              style={styles.input}
              placeholder="Zugriff: read/read_write"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <TextInput
              value={policyTitleContains}
              onChangeText={setPolicyTitleContains}
              style={styles.input}
              placeholder="Genehmigungsliste Titel enthaelt, z.B. PH"
              placeholderTextColor={colors.textSoft}
            />
            <TextInput
              value={policyNotes}
              onChangeText={setPolicyNotes}
              style={styles.input}
              placeholder="Notiz fuer KI-Kontext"
              placeholderTextColor={colors.textSoft}
              multiline
            />
            {policyProvider.trim() === "outlook_ics" && (
              <>
                <Text style={styles.forwardSafety}>
                  PH-Zeitfenster fuer diese Outlook-ICS-Quelle: Termine werden lokal als Tagesblock angezeigt.
                </Text>
                <View style={styles.row}>
                  <TextInput
                    value={policyTransformStart}
                    onChangeText={setPolicyTransformStart}
                    style={[styles.input, { flex: 1 }]}
                    placeholder="Start 08:00"
                    placeholderTextColor={colors.textSoft}
                    autoCapitalize="none"
                  />
                  <TextInput
                    value={policyTransformEnd}
                    onChangeText={setPolicyTransformEnd}
                    style={[styles.input, { flex: 1 }]}
                    placeholder="Ende 18:00"
                    placeholderTextColor={colors.textSoft}
                    autoCapitalize="none"
                  />
                </View>
              </>
            )}
            <TextInput
              value={policyIcsUrl}
              onChangeText={setPolicyIcsUrl}
              style={styles.input}
              placeholder="Outlook ICS URL nur fuer provider outlook_ics"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <TextInput
              value={policyToken}
              onChangeText={setPolicyToken}
              style={styles.input}
              placeholder="POLICY SPEICHERN"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <ActionButton
              label="Policy lokal speichern"
              onPress={() => openTokenModal({ title: "Policy speichern", explanation: "Die Account-Policy wird lokal gespeichert.", expectedToken: "POLICY SPEICHERN", onConfirm: handleCreateAccountPolicy })}
              disabled={actionBusy || !policyLabel.trim() || policyToken.trim() !== "POLICY SPEICHERN"}
            />
            {!!policyResult && <Text style={styles.approvalResultText}>{policyResult}</Text>}
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Gespeicherte Policies</Text>
            {isArray(accountPolicies?.items).map((policy) => (
              <View key={policy.id || policy.label} style={styles.cardCompact}>
                <View style={styles.privacyRow}>
                  <Text style={styles.privacyLabel}>{policy.label}</Text>
                  <Chip label={`${policy.provider} / ${policy.role}`} color={policy.enabled ? colors.sage : colors.textSoft} />
                </View>
                {!!policy.transform?.fixed_daily_window && (
                  <Text style={styles.cardMeta}>
                    Zeitfenster: {policy.transform.fixed_daily_window.start} - {policy.transform.fixed_daily_window.end}
                  </Text>
                )}
              </View>
            ))}
            {isArray(accountPolicies?.items).length === 0 && (
              <Text style={styles.cardBody}>Noch keine Account-Policy gespeichert.</Text>
            )}
            {!!accountPolicies?.ai_context && (
              <Text style={styles.forwardSafety}>{accountPolicies.ai_context}</Text>
            )}
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Kalender aktivieren</Text>
            <Text style={styles.cardBody}>
              Dieses Gate prueft nur, ob Aktivierung erlaubt waere. Der echte Config-Apply bleibt ein separater Schritt.
            </Text>
            <TextInput
              value={calendarActivationToken}
              onChangeText={setCalendarActivationToken}
              style={styles.input}
              placeholder="KALENDER AKTIVIEREN"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <ActionButton
              label="Aktivierungs-Gate pruefen"
              onPress={handleCalendarActivationGate}
              disabled={actionBusy}
            />
            {!!calendarActivationResult && (
              <Text style={styles.approvalResultText}>{calendarActivationResult}</Text>
            )}
          </View>

          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>Posteingang aufraeumen (Gmail)</Text>
              <Chip
                label={privacy?.external_services?.mail_organize ? "aktiv" : "aus"}
                color={privacy?.external_services?.mail_organize ? colors.warn : colors.textSoft}
              />
            </View>
            <Text style={styles.cardBody}>
              Friday verschiebt nur offensichtliche Gmail-Noise-Mails reversibel nach Friday/Aussortiert.
              Es wird nichts geloescht und nichts gesendet.
            </Text>
            <TextInput
              value={mailOrganizeToken}
              onChangeText={setMailOrganizeToken}
              style={styles.input}
              placeholder="POSTFACH AUFRAEUMEN"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <View style={styles.row}>
              <ActionButton
                label="Aufraeumen aktivieren"
                onPress={handleActivateMailOrganize}
                disabled={actionBusy || mailOrganizeToken.trim() !== "POSTFACH AUFRAEUMEN"}
              />
              <ActionButton
                label="Jetzt aufraeumen"
                onPress={handleRunMailOrganize}
                disabled={actionBusy || !privacy?.external_services?.mail_organize}
              />
            </View>
            {!!mailOrganizeResult && <Text style={styles.approvalResultText}>{mailOrganizeResult}</Text>}
            {isArray(mailOrganizeLog?.items).slice(0, 5).map((entry) => (
              <View key={entry.id} style={styles.cardCompact}>
                <Text style={styles.cardMeta}>{entry.sender || "Unbekannter Absender"}</Text>
                <Text style={styles.cardBody}>{entry.subject || "Ohne Betreff"}</Text>
                <Text style={styles.forwardSafety}>
                  Label: {entry.to_label} / Rueckgaengig: {entry.undone ? "ja" : "nein"}
                </Text>
                {!entry.undone && (
                  <ActionButton
                    label="Zurueck in Posteingang"
                    onPress={() => handleUndoMailOrganize(entry.id)}
                    disabled={actionBusy || !privacy?.external_services?.mail_organize}
                  />
                )}
              </View>
            ))}
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Verbindungen</Text>
            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>E-Mail</Text>
              <Chip label={setupStatus?.email?.configured ? "konfiguriert" : "nicht verbunden"} color={setupStatus?.email?.configured ? colors.warn : colors.textSoft} />
            </View>
            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>Familienhelden-Mail ({setupStatus?.ms_mail?.account_count || 0})</Text>
              <Chip
                label={setupStatus?.ms_mail?.read_enabled ? "read-only aktiv" : "read-only aus"}
                color={setupStatus?.ms_mail?.read_enabled ? colors.warn : colors.textSoft}
              />
            </View>
            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>Gmail nur lesen ({setupStatus?.imap_mail?.account_count || 0})</Text>
              <Chip
                label={setupStatus?.imap_mail?.read_enabled ? "read-only aktiv" : "read-only aus"}
                color={setupStatus?.imap_mail?.read_enabled ? colors.warn : colors.textSoft}
              />
            </View>            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>WhatsApp Read-Bridge</Text>
              <Chip label={setupStatus?.whatsapp?.read_enabled ? "aktiv" : "aus"} color={setupStatus?.whatsapp?.read_enabled ? colors.warn : colors.textSoft} />
            </View>
            <Text style={styles.forwardSafety}>
              Echte Nachrichten werden nur nach eigenen harten Gates vorbereitet. Friday sendet hier nichts automatisch.
            </Text>
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Safety-Flags</Text>
            {Object.entries(safetyFlags).map(([key, value]) => (
              <View key={key} style={styles.privacyRow}>
                <Text style={styles.privacyLabel}>{key}</Text>
                <Chip label={String(value)} color={value === false ? colors.textSoft : colors.success} />
              </View>
            ))}
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Setup-Schritte</Text>
            {setupSteps.map((step) => (
              <View key={step.key || step.label} style={styles.privacyRow}>
                <Text style={styles.privacyLabel}>{step.label || step.title || step.key}</Text>
                <Chip label={step.status || "offen"} color={step.status === "ready" ? colors.success : colors.warn} />
              </View>
            ))}
            {setupSteps.length === 0 && (
              <Text style={styles.cardBody}>Setup-Status konnte noch nicht geladen werden.</Text>
            )}
          </View>
        </View>
      );
    }

    return null;
  };

  if (!fontsLoaded && !fontLoadError) {
    return null;
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle={isDarkMode ? "light-content" : "dark-content"} backgroundColor={colors.bg} />
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handlePullRefresh}
            tintColor={colors.accent}
            colors={[colors.accent]}
            progressBackgroundColor={colors.surface}
          />
        }
      >
        <View style={styles.header}>
          <View style={styles.brandRow}>
            <LogoMark />
            <View style={styles.brandTextBlock}>
              <Text style={styles.brandKicker}>FRIDAY</Text>
              <Text style={styles.heading}>{greeting()}, Philip</Text>
              <Text style={styles.subheading}>{todayLabel()} | {headerSummary}</Text>
            </View>
          </View>
          <View style={styles.statusPill}>
            <View
              style={[
                styles.statusDot,
                { backgroundColor: online === null ? colors.warn : online ? colors.success : colors.danger },
              ]}
            />
            <Text style={styles.statusText}>
              {online === null ? "Prüfe…" : online ? `Verbunden | ${connectionKind}` : "Offline"}
            </Text>
          </View>
        </View>
        <Text style={[styles.syncStatusText, !syncStatus.online && styles.syncStatusTextOffline]}>
          {syncLabel}
        </Text>

        {loading && (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="small" color={colors.accent} />
            <View style={styles.progressTrack}>
              <View
                style={[
                  styles.progressFill,
                  {
                    width: `${
                      loadProgress.total
                        ? Math.max(6, Math.round((loadProgress.done / loadProgress.total) * 100))
                        : 6
                    }%`,
                  },
                ]}
              />
            </View>
            <Text style={styles.progressText}>
              {currentScreen} lädt… {loadProgress.done}/{loadProgress.total || "?"} Anfragen
            </Text>
          </View>
        )}
        {!!error && (
          <View style={styles.errorBanner}>
            <Text style={styles.errorText}>{error}</Text>
            <ActionButton small variant="ghost" label="Erneut versuchen" onPress={refreshActive} />
          </View>
        )}
        {active === "Mehr" && moreScreen && (
          <TouchableOpacity style={styles.backToMore} onPress={() => setMoreScreen("")} activeOpacity={0.75}>
            <Text style={styles.backToMoreText}>Zurück zu Mehr</Text>
          </TouchableOpacity>
        )}
        {!loading && !error && renderScreenContent()}
        {actionBusy && <Text style={styles.busyHint}>{t("common.busy")}</Text>}
        <Text style={styles.footer}>Friday 1.0 | {t("common.footer")} | {updateStatus} | {getApiUrl()}</Text>
      </ScrollView>
      {active === "Home" && <PushToTalk colors={colors} />}
      <View style={styles.bottomTabBar}>
        {bottomTabs.map((tab) => {
          const selected = active === tab.key;
          const badgeValue = tab.key === "Mehr" ? openLearningCount : 0;
          return (
            <TouchableOpacity
              key={tab.key}
              style={[styles.bottomTabItem, selected && styles.bottomTabItemActive]}
              onPress={() => navigateTo(tab.key)}
              activeOpacity={0.76}
            >
              <LineIcon name={tab.icon} color={selected ? colors.accentStrong : colors.muted} />
              <Text style={[styles.bottomTabLabel, selected && styles.bottomTabTextActive]}>{t(`nav.${tab.key}`)}</Text>
              <Badge value={badgeValue} />
            </TouchableOpacity>
          );
        })}
      </View>
      <ConfirmTokenModal
        visible={Boolean(tokenModal)}
        title={tokenModal?.title || "Freigabe"}
        explanation={tokenModal?.explanation || "Bitte bestätige die Aktion mit dem exakten Token."}
        expectedToken={tokenModal?.expectedToken || ""}
        onCancel={() => setTokenModal(null)}
        onConfirm={(value) => {
          const current = tokenModal;
          setTokenModal(null);
          current?.onConfirm?.(value);
        }}
      />
    </SafeAreaView>
  );
}

function createStyles(themeColors) {
  const colors = themeColors;
  const softShadow = createSoftShadow(colors);
  return StyleSheet.create(withFigtreeFonts({
  container: {
    backgroundColor: colors.bg,
    flex: 1,
    paddingTop: Platform.OS === "android" ? StatusBar.currentHeight : 0,
  },
  scroll: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  brandRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  logo: {
    width: 48,
    height: 48,
    borderRadius: 16,
    backgroundColor: colors.accent,
    alignItems: "center",
    justifyContent: "center",
    ...softShadow,
  },
  logoText: {
    color: "#f5efe2",
    fontSize: 25,
    fontWeight: "800",
  },
  heading: {
    color: colors.text,
    fontSize: 22,
    fontWeight: "800",
  },
  subheading: {
    color: colors.textSoft,
    fontSize: 13,
    marginTop: 2,
  },
  statusPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    backgroundColor: colors.surface,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 7,
    ...softShadow,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  statusText: {
    color: colors.textSoft,
    fontSize: 11,
    fontWeight: "600",
  },
  tabScroll: {
    marginTop: 16,
    marginBottom: 16,
  },
  tabs: {
    flexDirection: "row",
    gap: 8,
  },
  tab: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: colors.surface,
    ...softShadow,
  },
  tabActive: {
    backgroundColor: colors.accent,
  },
  tabIcon: {
    color: colors.textSoft,
    fontSize: 13,
  },
  tabText: {
    color: colors.textSoft,
    fontSize: 13,
    fontWeight: "600",
  },
  tabTextActive: {
    color: "#f5efe2",
  },
  loadingBox: {
    paddingVertical: 48,
    alignItems: "center",
  },
  errorBanner: {
    backgroundColor: "#f7e7e1",
    borderRadius: 18,
    padding: 16,
    marginBottom: 14,
    gap: 10,
    ...softShadow,
  },
  errorText: {
    color: "#a4543f",
    fontSize: 14,
  },
  statGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  statCard: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    borderTopWidth: 4,
    padding: 16,
    width: "48%",
    flexGrow: 1,
    ...softShadow,
  },
  statValue: {
    fontSize: 32,
    fontWeight: "800",
  },
  statLabel: {
    color: colors.textSoft,
    fontSize: 12,
    marginTop: 4,
    fontWeight: "600",
  },
  dashboardDate: {
    color: colors.textSoft,
    fontSize: 12,
    marginTop: 16,
    textAlign: "center",
  },
  sectionTitle: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "700",
    marginTop: 18,
    marginBottom: 10,
  },
  card: {
    backgroundColor: colors.card,
    borderRadius: 20,
    padding: 16,
    marginBottom: 12,
    ...softShadow,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 8,
    marginBottom: 6,
  },
  cardTitle: {
    color: colors.text,
    fontSize: 15,
    fontWeight: "700",
    flexShrink: 1,
  },
  cardBody: {
    color: "#4a5344",
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 4,
  },
  cardMeta: {
    color: colors.textSoft,
    fontSize: 12,
    marginBottom: 4,
  },
  cardCompact: {
    borderTopWidth: 1,
    borderTopColor: colors.line,
    paddingTop: 10,
    marginTop: 10,
  },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  chipDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  chipText: {
    fontSize: 11,
    fontWeight: "700",
  },
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 8,
  },
  button: {
    borderRadius: 14,
    paddingHorizontal: 16,
    paddingVertical: 11,
    alignItems: "center",
    justifyContent: "center",
    ...softShadow,
  },
  buttonSmall: {
    paddingHorizontal: 13,
    paddingVertical: 9,
    borderRadius: 12,
  },
  buttonPrimary: {
    backgroundColor: colors.accent,
  },
  buttonSuccess: {
    backgroundColor: colors.success,
  },
  buttonDanger: {
    backgroundColor: colors.danger,
  },
  buttonLight: {
    backgroundColor: colors.cream,
  },
  buttonGhost: {
    backgroundColor: colors.buttonGhostBg,
    borderWidth: 1.5,
    borderColor: colors.accent,
    shadowOpacity: 0,
    elevation: 0,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: colors.buttonSolidText,
    fontSize: 14,
    fontWeight: "700",
  },
  buttonLightText: {
    color: colors.buttonLightText,
    fontSize: 14,
    fontWeight: "700",
  },
  buttonTextSmall: {
    fontSize: 12,
  },
  buttonGhostText: {
    color: colors.buttonGhostText,
    fontSize: 14,
    fontWeight: "700",
  },
  inputRow: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 14,
  },
  input: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 14,
    color: colors.text,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 14,
    ...softShadow,
  },
  inputHalf: {
    minWidth: 135,
  },
  inputStacked: {
    marginTop: 10,
    marginBottom: 12,
  },
  forwardBox: {
    backgroundColor: colors.surface,
    borderRadius: 18,
    marginBottom: 14,
    padding: 12,
    ...softShadow,
  },
  assignmentBox: {
    backgroundColor: colors.accentSoft,
    borderColor: colors.border,
    borderRadius: 18,
    borderWidth: 1,
    marginTop: 12,
    padding: 12,
  },
  forwardLabel: {
    color: colors.textSoft,
    fontSize: 12,
    fontWeight: "700",
    marginBottom: 8,
  },
  forwardPanel: {
    backgroundColor: colors.surface,
    borderRadius: 22,
    marginBottom: 16,
    padding: 16,
    ...softShadow,
  },
  contactChoice: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderRadius: 15,
    borderWidth: 1,
    marginBottom: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  contactChoiceActive: {
    backgroundColor: colors.accentSoft,
    borderColor: colors.accent,
  },
  contactChoiceText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "700",
  },
  draftBox: {
    backgroundColor: colors.card,
    borderRadius: 16,
    marginTop: 12,
    padding: 12,
  },
  draftText: {
    color: colors.text,
    fontSize: 13,
    lineHeight: 19,
  },
  mockResultBox: {
    backgroundColor: colors.accentSoft,
    borderRadius: 14,
    marginTop: 10,
    padding: 12,
  },
  mockResultText: {
    color: colors.deep,
    fontSize: 12,
    fontWeight: "700",
    lineHeight: 18,
  },
  approvalBox: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: 16,
    borderWidth: 1,
    gap: 8,
    marginTop: 12,
    padding: 12,
  },
  approvalResultText: {
    color: colors.deep,
    fontSize: 12,
    fontWeight: "700",
    lineHeight: 18,
  },
  auditBox: {
    backgroundColor: "#f4ead8",
    borderRadius: 16,
    marginTop: 12,
    padding: 12,
  },
  auditText: {
    color: colors.deep,
    fontSize: 12,
    lineHeight: 18,
  },
  forwardSafety: {
    color: colors.textSoft,
    fontSize: 11,
    lineHeight: 16,
    marginTop: 10,
    marginBottom: 8,
  },
  slotCard: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: 16,
    paddingHorizontal: 15,
    paddingVertical: 12,
    marginBottom: 8,
    ...softShadow,
  },
  slotText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "600",
  },
  slotFree: {
    color: colors.success,
    fontSize: 12,
    fontWeight: "700",
  },
  contactRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    flexShrink: 1,
  },
  avatar: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: colors.accentSoft,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarText: {
    color: colors.accent,
    fontSize: 16,
    fontWeight: "800",
  },
  privacyBanner: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    backgroundColor: colors.accentSoft,
    borderRadius: 18,
    padding: 16,
    ...softShadow,
  },
  privacyBannerIcon: {
    fontSize: 20,
  },
  privacyBannerText: {
    color: colors.deep,
    fontSize: 13,
    flex: 1,
    lineHeight: 18,
  },
  privacyRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 7,
  },
  privacyLabel: {
    color: "#4a5344",
    fontSize: 14,
  },
  privacyNote: {
    color: colors.textSoft,
    fontSize: 12,
    marginTop: 12,
    lineHeight: 18,
  },
  empty: {
    alignItems: "center",
    paddingVertical: 28,
  },
  emptyIcon: {
    fontSize: 28,
    color: colors.textSoft,
    marginBottom: 8,
  },
  emptyText: {
    color: colors.textSoft,
    fontSize: 13,
  },
  busyHint: {
    color: colors.textSoft,
    fontSize: 12,
    textAlign: "center",
    marginTop: 10,
  },
  footer: {
    color: "#a8a390",
    fontSize: 11,
    textAlign: "center",
    marginTop: 26,
  },

  container: {
    backgroundColor: colors.bg,
    flex: 1,
    paddingTop: Platform.OS === "android" ? StatusBar.currentHeight : 0,
  },
  scroll: {
    padding: 18,
    paddingBottom: 48,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 8,
    backgroundColor: colors.surface,
    borderColor: "rgba(83,106,72,0.10)",
    borderWidth: 1,
    borderRadius: 28,
    padding: 14,
    ...softShadow,
  },
  brandRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    flex: 1,
  },
  brandTextBlock: {
    flexShrink: 1,
  },
  brandKicker: {
    color: colors.sage,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 2.4,
    marginBottom: 2,
  },
  logoMark: {
    backgroundColor: colors.accentStrong,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
    borderColor: "rgba(255,250,240,0.42)",
    borderWidth: 1,
    ...softShadow,
  },
  logoHalo: {
    position: "absolute",
    borderColor: "rgba(247,241,227,0.48)",
    borderWidth: 1.5,
    transform: [{ rotate: "-18deg" }],
  },
  logoLeaf: {
    position: "absolute",
    right: 11,
    top: 8,
    backgroundColor: colors.leaf,
    transform: [{ rotate: "36deg" }],
    opacity: 0.95,
  },
  logoNeedle: {
    position: "absolute",
    backgroundColor: colors.cream,
    transform: [{ rotate: "36deg" }],
  },
  logoHome: {
    position: "absolute",
    left: 13,
    bottom: 13,
    backgroundColor: colors.gold,
    transform: [{ rotate: "-18deg" }],
  },
  logoCore: {
    position: "absolute",
    backgroundColor: colors.cream,
  },
  heading: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "900",
    letterSpacing: -0.3,
  },
  subheading: {
    color: colors.textSoft,
    fontSize: 12,
    marginTop: 3,
    fontWeight: "600",
  },
  statusPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    backgroundColor: colors.accentSoft,
    borderRadius: 999,
    paddingHorizontal: 11,
    paddingVertical: 8,
    borderColor: "rgba(83,106,72,0.12)",
    borderWidth: 1,
  },
  statusText: {
    color: colors.accentStrong,
    fontSize: 11,
    fontWeight: "800",
  },
  tabScroll: {
    marginTop: 12,
    marginBottom: 16,
  },
  tabs: {
    flexDirection: "row",
    gap: 9,
  },
  tab: {
    minHeight: 44,
    flexDirection: "row",
    alignItems: "center",
    gap: 7,
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "rgba(255,250,240,0.88)",
    borderColor: "rgba(83,106,72,0.10)",
    borderWidth: 1,
  },
  tabActive: {
    backgroundColor: colors.accentStrong,
    borderColor: colors.accentStrong,
  },
  tabIcon: {
    color: colors.textSoft,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 0.5,
    textTransform: "uppercase",
  },
  tabText: {
    color: colors.textSoft,
    fontSize: 13,
    fontWeight: "800",
  },
  tabTextActive: {
    color: colors.onAccent,
  },
  card: {
    backgroundColor: colors.card,
    borderRadius: 24,
    padding: 17,
    marginBottom: 13,
    borderColor: "rgba(83,106,72,0.10)",
    borderWidth: 1,
    ...softShadow,
  },
  cardCompact: {
    borderTopWidth: 1,
    borderTopColor: colors.line,
    paddingTop: 11,
    marginTop: 11,
  },
  cardTitle: {
    color: colors.text,
    fontSize: 15,
    fontWeight: "900",
    flexShrink: 1,
    letterSpacing: -0.1,
  },
  cardBody: {
    color: "#46513f",
    fontSize: 14,
    lineHeight: 21,
    marginBottom: 4,
  },
  cardMeta: {
    color: colors.textSoft,
    fontSize: 12,
    marginBottom: 4,
    fontWeight: "600",
  },
  statCard: {
    backgroundColor: colors.surface,
    borderRadius: 24,
    borderTopWidth: 0,
    borderLeftWidth: 4,
    padding: 17,
    width: "48%",
    flexGrow: 1,
    borderColor: "rgba(83,106,72,0.10)",
    ...softShadow,
  },
  statValue: {
    fontSize: 33,
    fontWeight: "900",
    letterSpacing: -1.0,
  },
  statLabel: {
    color: colors.textSoft,
    fontSize: 12,
    marginTop: 5,
    fontWeight: "800",
  },
  sectionTitle: {
    color: colors.text,
    fontSize: 17,
    fontWeight: "900",
    marginTop: 20,
    marginBottom: 10,
    letterSpacing: -0.2,
  },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  chipText: {
    fontSize: 11,
    fontWeight: "900",
  },
  button: {
    minHeight: 44,
    borderRadius: 16,
    paddingHorizontal: 17,
    paddingVertical: 12,
    alignItems: "center",
    justifyContent: "center",
    ...softShadow,
  },
  buttonPrimary: {
    backgroundColor: colors.accentStrong,
  },
  buttonSuccess: {
    backgroundColor: colors.success,
  },
  buttonDanger: {
    backgroundColor: colors.clay,
  },
  buttonLight: {
    backgroundColor: colors.cream,
  },
  buttonGhost: {
    backgroundColor: colors.buttonGhostBg,
    borderWidth: 1.5,
    borderColor: colors.accent,
    shadowOpacity: 0,
    elevation: 0,
  },
  buttonText: {
    color: colors.buttonSolidText,
    fontSize: 14,
    fontWeight: "900",
  },
  buttonLightText: {
    color: colors.buttonLightText,
    fontSize: 14,
    fontWeight: "900",
  },
  buttonGhostText: {
    color: colors.buttonGhostText,
    fontSize: 14,
    fontWeight: "900",
  },
  input: {
    flex: 1,
    minHeight: 46,
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderColor: "rgba(83,106,72,0.12)",
    borderWidth: 1,
    color: colors.text,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 14,
  },
  empty: {
    alignItems: "center",
    paddingVertical: 30,
    backgroundColor: "rgba(255,250,240,0.58)",
    borderRadius: 22,
    borderColor: "rgba(83,106,72,0.08)",
    borderWidth: 1,
  },
  errorBanner: {
    backgroundColor: "#f7e6dc",
    borderRadius: 22,
    padding: 16,
    marginBottom: 14,
    gap: 10,
    borderColor: "rgba(184,106,85,0.18)",
    borderWidth: 1,
  },
  footer: {
    color: colors.muted,
    fontSize: 11,
    textAlign: "center",
    marginTop: 26,
    lineHeight: 17,
  },
  homeHero: {
    backgroundColor: colors.accentStrong,
    borderRadius: 24,
    padding: 18,
    marginBottom: 14,
    ...softShadow,
  },
  homeEyebrow: {
    color: colors.accentSoft,
    fontSize: 12,
    fontWeight: "900",
    letterSpacing: 1.6,
    textTransform: "uppercase",
  },
  homeTitle: {
    color: colors.onAccent,
    fontSize: 26,
    lineHeight: 34,
    fontWeight: "900",
    marginTop: 4,
  },
  homeListRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    paddingVertical: 8,
  },
  homeListTime: {
    color: colors.accentStrong,
    fontSize: 13,
    fontWeight: "900",
    width: 48,
  },
  bottomTabBar: {
    minHeight: 74,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    backgroundColor: colors.surface,
    borderTopColor: colors.line,
    borderTopWidth: 1,
    paddingHorizontal: 8,
    paddingTop: 8,
    paddingBottom: Platform.OS === "ios" ? 20 : 10,
  },
  bottomTabItem: {
    minWidth: 58,
    minHeight: 50,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 8,
    position: "relative",
  },
  bottomTabItemActive: {
    backgroundColor: colors.accentSoft,
  },
  bottomTabIcon: {
    color: colors.textSoft,
    fontSize: 15,
    fontWeight: "900",
  },
  bottomTabLabel: {
    color: colors.textSoft,
    fontSize: 11,
    fontWeight: "800",
    marginTop: 2,
  },
  bottomTabTextActive: {
    color: colors.accentStrong,
  },
  badge: {
    minWidth: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: colors.danger,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 6,
  },
  badgeText: {
    color: colors.onAccent,
    fontSize: 10,
    fontWeight: "900",
  },
  moreItem: {
    minHeight: 72,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    backgroundColor: colors.card,
    borderRadius: 20,
    padding: 14,
    marginBottom: 10,
    ...softShadow,
  },
  moreIcon: {
    width: 44,
    height: 44,
    borderRadius: 15,
    backgroundColor: colors.accentSoft,
    alignItems: "center",
    justifyContent: "center",
  },
  moreIconText: {
    color: colors.accentStrong,
    fontWeight: "900",
  },
  backToMore: {
    alignSelf: "flex-start",
    minHeight: 44,
    borderRadius: 999,
    backgroundColor: colors.accentSoft,
    paddingHorizontal: 16,
    paddingVertical: 11,
    marginBottom: 12,
  },
  backToMoreText: {
    color: colors.accentStrong,
    fontWeight: "900",
  },
  filterBar: {
    flexDirection: "row",
    backgroundColor: colors.accentSoft,
    borderRadius: 999,
    padding: 4,
    marginBottom: 12,
  },
  filterOption: {
    minHeight: 38,
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 999,
  },
  filterOptionActive: {
    backgroundColor: colors.accentStrong,
  },
  filterText: {
    color: colors.accentStrong,
    fontWeight: "900",
    fontSize: 12,
  },
  filterTextActive: {
    color: colors.onAccent,
  },
  modalBackdrop: {
    flex: 1,
    backgroundColor: "rgba(28,36,26,0.52)",
    alignItems: "center",
    justifyContent: "center",
    padding: 20,
  },
  modalCard: {
    width: "100%",
    maxWidth: 390,
    backgroundColor: colors.card,
    borderRadius: 24,
    padding: 18,
    gap: 10,
    ...softShadow,
  },
  weekGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    marginTop: 8,
  },
  weekTile: {
    width: "48%",
    flexGrow: 1,
    backgroundColor: colors.card,
    borderRadius: 18,
    borderColor: "rgba(83,106,72,0.10)",
    borderWidth: 1,
    padding: 12,
    ...softShadow,
  },
  weekTileToday: {
    backgroundColor: colors.accentSoft,
    borderColor: colors.accentStrong,
    borderWidth: 1.5,
  },
  weekTileHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  weekTileDay: {
    color: colors.text,
    fontSize: 13,
    fontWeight: "900",
  },
  weekTileDayToday: {
    color: colors.accentStrong,
  },
  weekTileDate: {
    color: colors.textSoft,
    fontSize: 11,
    fontWeight: "700",
  },
  weekTileHours: {
    color: colors.accentStrong,
    fontSize: 12,
    fontWeight: "800",
    marginBottom: 6,
  },
  weekTileHoursFree: {
    color: colors.textSoft,
  },
  weekTileEvent: {
    color: "#46513f",
    fontSize: 11,
    lineHeight: 16,
    marginBottom: 2,
  },
  weekTileMore: {
    color: colors.textSoft,
    fontSize: 11,
    fontWeight: "700",
    marginTop: 2,
  },
  progressTrack: {
    width: "100%",
    height: 8,
    borderRadius: 999,
    backgroundColor: colors.accentSoft,
    marginTop: 14,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    borderRadius: 999,
    backgroundColor: colors.accentStrong,
  },
  progressText: {
    color: colors.textSoft,
    fontSize: 12,
    fontWeight: "700",
    marginTop: 8,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 12,
    backgroundColor: colors.surface,
    borderColor: colors.line,
    borderWidth: 1,
    borderRadius: 22,
    padding: 14,
    ...softShadow,
  },
  brandRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    flex: 1,
  },
  brandKicker: {
    color: colors.sage,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 1.6,
    marginBottom: 2,
  },
  heading: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "800",
  },
  subheading: {
    color: colors.textSoft,
    fontSize: 12,
    marginTop: 3,
    fontWeight: "500",
  },
  logoMark: {
    backgroundColor: colors.accentStrong,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
    borderColor: colors.line,
    borderWidth: 1,
    ...softShadow,
  },
  statusPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    backgroundColor: colors.accentSoft,
    borderRadius: 999,
    paddingHorizontal: 11,
    paddingVertical: 8,
    borderColor: colors.line,
    borderWidth: 1,
  },
  statusText: {
    color: colors.accentStrong,
    fontSize: 11,
    fontWeight: "800",
  },
  syncStatusText: {
    color: colors.textSoft,
    fontSize: 11,
    fontWeight: "600",
    marginTop: -4,
    marginBottom: 12,
    textAlign: "right",
  },
  syncStatusTextOffline: {
    color: colors.warn,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    padding: 16,
    marginBottom: 12,
    borderColor: colors.line,
    borderWidth: 1,
    ...softShadow,
  },
  cardTitle: {
    color: colors.text,
    fontSize: 15,
    fontWeight: "800",
    flexShrink: 1,
  },
  cardBody: {
    color: colors.text,
    fontSize: 14,
    lineHeight: 21,
    marginBottom: 4,
  },
  cardMeta: {
    color: colors.textSoft,
    fontSize: 12,
    marginBottom: 4,
    fontWeight: "500",
  },
  sectionTitle: {
    color: colors.textSoft,
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 1,
    marginTop: 18,
    marginBottom: 8,
    textTransform: "uppercase",
  },
  statCard: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    borderLeftWidth: 4,
    padding: 16,
    width: "48%",
    flexGrow: 1,
    borderColor: colors.line,
    borderWidth: 1,
    ...softShadow,
  },
  statValue: {
    fontSize: 32,
    fontWeight: "800",
  },
  statLabel: {
    color: colors.textSoft,
    fontSize: 12,
    marginTop: 5,
    fontWeight: "700",
  },
  chip: {
    alignItems: "center",
    alignSelf: "flex-start",
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  chipText: {
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.8,
  },
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 8,
  },
  listRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
    paddingVertical: 11,
    borderBottomColor: colors.line,
    borderBottomWidth: 1,
  },
  button: {
    minHeight: 44,
    borderRadius: 16,
    paddingHorizontal: 17,
    paddingVertical: 12,
    alignItems: "center",
    justifyContent: "center",
    ...softShadow,
  },
  buttonText: {
    color: colors.buttonSolidText,
    fontSize: 14,
    fontWeight: "800",
  },
  buttonLightText: {
    color: colors.buttonLightText,
    fontSize: 14,
    fontWeight: "800",
  },
  buttonGhostText: {
    color: colors.buttonGhostText,
    fontSize: 14,
    fontWeight: "800",
  },
  input: {
    flex: 1,
    minHeight: 46,
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderColor: colors.line,
    borderWidth: 1,
    color: colors.text,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 14,
  },
  forwardBox: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    marginBottom: 14,
    padding: 16,
    borderColor: colors.line,
    borderWidth: 1,
    ...softShadow,
  },
  assignmentBox: {
    backgroundColor: colors.accentSoft,
    borderColor: colors.line,
    borderRadius: 18,
    borderWidth: 1,
    marginTop: 12,
    padding: 12,
  },
  forwardPanel: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    marginBottom: 16,
    padding: 16,
    borderColor: colors.line,
    borderWidth: 1,
    ...softShadow,
  },
  contactChoice: {
    backgroundColor: colors.surface,
    borderColor: colors.line,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  draftBox: {
    backgroundColor: colors.surface,
    borderColor: colors.line,
    borderRadius: 16,
    borderWidth: 1,
    marginTop: 12,
    padding: 12,
  },
  approvalBox: {
    backgroundColor: colors.surface,
    borderColor: colors.line,
    borderRadius: 16,
    borderWidth: 1,
    gap: 8,
    marginTop: 12,
    padding: 12,
  },
  auditBox: {
    backgroundColor: colors.surface,
    borderColor: colors.line,
    borderRadius: 16,
    borderWidth: 1,
    marginTop: 12,
    padding: 12,
  },
  slotCard: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderColor: colors.line,
    borderWidth: 1,
    paddingHorizontal: 15,
    paddingVertical: 12,
    marginBottom: 8,
    ...softShadow,
  },
  empty: {
    alignItems: "center",
    gap: 8,
    paddingVertical: 26,
    backgroundColor: colors.surface,
    borderRadius: 20,
    borderColor: colors.line,
    borderWidth: 1,
  },
  emptyText: {
    color: colors.textSoft,
    fontSize: 13,
    fontWeight: "500",
  },
  errorBanner: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    padding: 16,
    marginBottom: 14,
    gap: 10,
    borderColor: colors.clay,
    borderWidth: 1,
  },
  errorText: {
    color: colors.clay,
    fontSize: 14,
    fontWeight: "600",
  },
  homeHero: {
    backgroundColor: colors.accentStrong,
    borderRadius: 20,
    padding: 18,
    marginBottom: 14,
    ...softShadow,
  },
  homeEyebrow: {
    color: colors.accentSoft,
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  homeTitle: {
    color: colors.onAccent,
    fontSize: 25,
    lineHeight: 32,
    fontWeight: "800",
    marginTop: 4,
  },
  homeListRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    paddingVertical: 11,
    borderBottomColor: colors.line,
    borderBottomWidth: 1,
  },
  homeListTime: {
    color: colors.accentStrong,
    fontSize: 13,
    fontWeight: "800",
    width: 48,
  },
  privacyBanner: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    backgroundColor: colors.accentSoft,
    borderRadius: 20,
    padding: 16,
    marginBottom: 12,
    ...softShadow,
  },
  privacyBannerText: {
    color: colors.accentStrong,
    fontSize: 13,
    flex: 1,
    lineHeight: 18,
    fontWeight: "600",
  },
  privacyHero: {
    backgroundColor: colors.accentStrong,
    borderRadius: 20,
    padding: 18,
    marginBottom: 12,
    ...softShadow,
  },
  privacyHeroTop: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 10,
  },
  privacyHeroIcon: {
    width: 44,
    height: 44,
    borderRadius: 16,
    backgroundColor: `${colors.onAccent}1f`,
    alignItems: "center",
    justifyContent: "center",
  },
  privacyHeroTitle: {
    color: colors.onAccent,
    fontSize: 22,
    lineHeight: 28,
    fontWeight: "800",
  },
  privacyHeroText: {
    color: colors.accentSoft,
    fontSize: 13,
    lineHeight: 19,
    fontWeight: "500",
  },
  privacyRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
    paddingVertical: 11,
    borderBottomColor: colors.line,
    borderBottomWidth: 1,
  },
  privacyLabel: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "600",
    flex: 1,
  },
  privacyNote: {
    color: colors.textSoft,
    fontSize: 12,
    marginTop: 12,
    lineHeight: 18,
  },
  privacyStatusPill: {
    borderRadius: 999,
    backgroundColor: `${colors.success}22`,
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  privacyStatusPillWarn: {
    backgroundColor: `${colors.warn}22`,
  },
  privacyStatusText: {
    color: colors.success,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.8,
  },
  privacyStatusTextWarn: {
    color: colors.warn,
  },
  toggleSwitch: {
    width: 42,
    height: 24,
    borderRadius: 999,
    backgroundColor: colors.line,
    padding: 3,
    justifyContent: "center",
  },
  toggleSwitchOn: {
    backgroundColor: `${colors.success}55`,
  },
  toggleKnob: {
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: colors.surface,
  },
  toggleKnobOn: {
    alignSelf: "flex-end",
    backgroundColor: colors.success,
  },
  bottomTabBar: {
    minHeight: 74,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    backgroundColor: colors.surface,
    borderTopColor: colors.line,
    borderTopWidth: 1,
    paddingHorizontal: 8,
    paddingTop: 8,
    paddingBottom: Platform.OS === "ios" ? 20 : 10,
  },
  bottomTabItem: {
    minWidth: 58,
    minHeight: 50,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 8,
    position: "relative",
  },
  bottomTabItemActive: {
    backgroundColor: colors.accentSoft,
  },
  bottomTabLabel: {
    color: colors.muted,
    fontSize: 11,
    fontWeight: "700",
    marginTop: 2,
  },
  bottomTabTextActive: {
    color: colors.accentStrong,
  },
  badgeText: {
    color: colors.onAccent,
    fontSize: 10,
    fontWeight: "800",
  },
  moreItem: {
    minHeight: 72,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    backgroundColor: colors.surface,
    borderRadius: 20,
    padding: 14,
    marginBottom: 10,
    borderColor: colors.line,
    borderWidth: 1,
    ...softShadow,
  },
  moreIcon: {
    width: 44,
    height: 44,
    borderRadius: 15,
    backgroundColor: colors.accentSoft,
    alignItems: "center",
    justifyContent: "center",
  },
  weekTile: {
    width: "48%",
    flexGrow: 1,
    backgroundColor: colors.surface,
    borderRadius: 18,
    borderColor: colors.line,
    borderWidth: 1,
    padding: 12,
    ...softShadow,
  },
  weekTileEvent: {
    color: colors.text,
    fontSize: 11,
    lineHeight: 16,
    marginBottom: 2,
  },
  modalCard: {
    width: "100%",
    maxWidth: 390,
    backgroundColor: colors.surface,
    borderRadius: 20,
    padding: 18,
    gap: 10,
    ...softShadow,
  },
  footer: {
    color: colors.muted,
    fontSize: 11,
    textAlign: "center",
    marginTop: 26,
    lineHeight: 17,
  },
  }));
}

let styles = createStyles(colors);
