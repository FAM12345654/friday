import React, { useEffect, useState } from "react";
import * as Updates from "expo-updates";
import {
  ActivityIndicator,
  Linking,
  Platform,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

import {
  approveMessageSuggestion,
  approveTaskSuggestion,
  archiveTask,
  buildTaskForwardDraft,
  checkHealth,
  completeTask,
  connectEmailAccount,
  createAccountPolicy,
  createCalendarEventFromMessage,
  createContact,
  createTask,
  deleteCalendarEvent,
  deleteTask,
  getAccountPolicies,
  getCalendarAccountStatus,
  getEmailAccountStatus,
  getEmailInbox,
  generateCalendarEventSuggestionForMessage,
  getWhatsAppMessages,
  getWhatsAppStatus,
  generateTaskSuggestionsForMessage,
  getApiUrl,
  getCalendar,
  getGoogleCalendarReadPreview,
  getContacts,
  getDashboard,
  getMessageSuggestion,
  getMessageSuggestions,
  getMessages,
  getPrivacy,
  getSetupStatus,
  getTasks,
  checkCalendarActivationGate,
  sendTaskForwardEmail,
  testEmailAccountConnection,
  rejectMessageSuggestion,
  rejectTaskSuggestion,
} from "./src/api/client";

const screens = [
  { key: "Dashboard", icon: "◈" },
  { key: "Tasks", icon: "✓" },
  { key: "Nachrichten", icon: "✉" },
  { key: "Kalender", icon: "▦" },
  { key: "Kontakte", icon: "☺" },
  { key: "Datenschutz", icon: "🛡" },
  { key: "Setup", icon: "⚙" },
];

const colors = {
  bg: "#f6f1e4",
  surface: "#fdfaf1",
  card: "#fbf7ec",
  border: "#e7dfca",
  accent: "#5c7150",
  accentSoft: "#e9eddd",
  sage: "#7d9270",
  deep: "#36442e",
  text: "#2e3627",
  textSoft: "#84907b",
  success: "#5f7f52",
  warn: "#b8924a",
  danger: "#bb6b58",
};

const softShadow = {
  shadowColor: colors.deep,
  shadowOffset: { width: 0, height: 3 },
  shadowOpacity: 0.08,
  shadowRadius: 10,
  elevation: 2,
};

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

function ActionButton({ label, onPress, disabled, variant = "primary", small }) {
  const variantStyle =
    variant === "danger"
      ? styles.buttonDanger
      : variant === "ghost"
        ? styles.buttonGhost
        : variant === "success"
          ? styles.buttonSuccess
          : styles.buttonPrimary;
  const textStyle =
    variant === "ghost" ? styles.buttonGhostText : styles.buttonText;
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
  return (
    <View style={[styles.chip, { backgroundColor: `${color}1f` }]}>
      <View style={[styles.chipDot, { backgroundColor: color }]} />
      <Text style={[styles.chipText, { color }]}>{label}</Text>
    </View>
  );
}

function SectionTitle({ children }) {
  return <Text style={styles.sectionTitle}>{children}</Text>;
}

function EmptyState({ icon, text }) {
  return (
    <View style={styles.empty}>
      <Text style={styles.emptyIcon}>{icon}</Text>
      <Text style={styles.emptyText}>{text}</Text>
    </View>
  );
}

function StatCard({ label, value, tint }) {
  return (
    <View style={[styles.statCard, { borderTopColor: tint }]}>
      <Text style={[styles.statValue, { color: tint }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

export default function App() {
  const [active, setActive] = useState("Dashboard");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [updateStatus, setUpdateStatus] = useState("Update: prüfe…");
  const [online, setOnline] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [messages, setMessages] = useState([]);
  const [messageSuggestions, setMessageSuggestions] = useState([]);
  const [taskSuggestions, setTaskSuggestions] = useState([]);
  const [calendar, setCalendar] = useState(null);
  const [googleCalendarPreview, setGoogleCalendarPreview] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [newContactName, setNewContactName] = useState("");
  const [newContactEmail, setNewContactEmail] = useState("");
  const [newContactWhatsapp, setNewContactWhatsapp] = useState("");
  const [newContactNotes, setNewContactNotes] = useState("");
  const [privacy, setPrivacy] = useState(null);
  const [setupStatus, setSetupStatus] = useState(null);
  const [accountPolicies, setAccountPolicies] = useState(null);
  const [calendarAccountStatus, setCalendarAccountStatus] = useState(null);
  const [policyLabel, setPolicyLabel] = useState("Google Hauptkalender");
  const [policyProvider, setPolicyProvider] = useState("google_calendar");
  const [policyRole, setPolicyRole] = useState("main");
  const [policyAccess, setPolicyAccess] = useState("read_write");
  const [policyTitleContains, setPolicyTitleContains] = useState("");
  const [policyNotes, setPolicyNotes] = useState("");
  const [policyIcsUrl, setPolicyIcsUrl] = useState("");
  const [policyToken, setPolicyToken] = useState("");
  const [policyResult, setPolicyResult] = useState("");
  const [calendarActivationToken, setCalendarActivationToken] = useState("");
  const [calendarActivationResult, setCalendarActivationResult] = useState("");
  const [emailAccountStatus, setEmailAccountStatus] = useState(null);
  const [emailInbox, setEmailInbox] = useState(null);
  const [whatsappStatus, setWhatsappStatus] = useState(null);
  const [whatsappInbox, setWhatsappInbox] = useState(null);
  const [emailPreset, setEmailPreset] = useState("gmail");
  const [emailAddress, setEmailAddress] = useState("");
  const [emailUsername, setEmailUsername] = useState("");
  const [emailAppPassword, setEmailAppPassword] = useState("");
  const [emailAccountToken, setEmailAccountToken] = useState("");
  const [emailAccountResult, setEmailAccountResult] = useState("");
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
  const [calendarWriteResult, setCalendarWriteResult] = useState("");
  const [calendarDeleteTokens, setCalendarDeleteTokens] = useState({});
  const [calendarDeleteResult, setCalendarDeleteResult] = useState("");
  const [actionBusy, setActionBusy] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const applyAvailableUpdate = async () => {
      if (__DEV__) {
        setUpdateStatus("Update: Entwicklung");
        return;
      }

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
          await Updates.reloadAsync();
        }
      } catch (err) {
        if (isMounted) {
          setUpdateStatus("Update: später erneut");
        }
      }
    };

    applyAvailableUpdate();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    const ping = async () => {
      const ok = await checkHealth();
      if (isMounted) {
        setOnline(ok);
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
    let isMounted = true;

    const load = async () => {
      setLoading(true);
      setError("");

      try {
        await loadScreenData(active, { silentErrors: false });
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
  }, [active]);

  const loadScreenData = async (screenName) => {
    if (screenName === "Dashboard") {
      const payload = await getDashboard();
      setDashboard(payload);
      return;
    }

    if (screenName === "Tasks") {
      const payload = await getTasks();
      setTasks(isArray(payload));
      return;
    }

    if (screenName === "Nachrichten") {
      const messagePayload = await getMessages();
      const suggestions = await getMessageSuggestions();
      const inbox = await getEmailInbox(10).catch((err) => ({
        connected: false,
        items: [],
        message: normalizeApiError(err),
      }));
      const whatsapp = await getWhatsAppMessages(10).catch((err) => ({
        items: [],
        status: { read_enabled: false, connected: false },
        message: normalizeApiError(err),
      }));
      const list = messagePayload?.items || [];
      setMessages(isArray(list));
      setMessageSuggestions(isArray(suggestions?.message_suggestions));
      setTaskSuggestions(isArray(suggestions?.task_suggestions));
      setEmailInbox(inbox);
      setWhatsappInbox(whatsapp);
      return;
    }

    if (screenName === "Kalender") {
      const payload = await getCalendar();
      const calendarStatus = await getCalendarAccountStatus().catch(() => null);
      let googlePreview = null;
      if (calendarStatus?.google?.connected) {
        const { rangeStart, rangeEnd } = buildGoogleCalendarRange(30);
        googlePreview = await getGoogleCalendarReadPreview(rangeStart, rangeEnd).catch((err) => ({
          ok: false,
          read_only: true,
          write_enabled: false,
          real_calendar_enabled: false,
          events: [],
          message: normalizeApiError(err),
          blocked_reasons: ["google_calendar_read_failed"],
          external_call_used: true,
        }));
      }
      setCalendar(payload);
      setCalendarAccountStatus(calendarStatus);
      setGoogleCalendarPreview(googlePreview);
      return;
    }

    if (screenName === "Kontakte") {
      const payload = await getContacts();
      setContacts(isArray(payload));
      return;
    }

    if (screenName === "Datenschutz") {
      const payload = await getPrivacy();
      const emailStatus = await getEmailAccountStatus().catch(() => null);
      const waStatus = await getWhatsAppStatus().catch(() => null);
      setPrivacy(payload);
      setEmailAccountStatus(emailStatus);
      setWhatsappStatus(waStatus);
      return;
    }

    if (screenName === "Setup") {
      const payload = await getSetupStatus();
      const policies = await getAccountPolicies().catch(() => null);
      const calendarStatus = await getCalendarAccountStatus().catch(() => null);
      setSetupStatus(payload);
      setAccountPolicies(policies);
      setCalendarAccountStatus(calendarStatus);
    }
  };

  const refreshActive = async () => {
    try {
      setError("");
      await loadScreenData(active);
    } catch (err) {
      setError(normalizeApiError(err));
    }
  };

  const handlePullRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshActive();
      setOnline(await checkHealth());
    } finally {
      setRefreshing(false);
    }
  };

  const handleCreateTask = async () => {
    if (!newTaskTitle.trim()) {
      return;
    }
    setActionBusy(true);
    try {
      const forwardTo = newTaskForwardTo.trim();
      await createTask({
        title: newTaskTitle,
        notes: forwardTo ? `Weiterleiten an: ${forwardTo}` : undefined,
      });
      setNewTaskTitle("");
      setNewTaskForwardTo("");
      await refreshActive();
    } catch (err) {
      setError(normalizeApiError(err));
    } finally {
      setActionBusy(false);
    }
  };

  const handleCreateContact = async () => {
    if (!newContactName.trim()) {
      return;
    }
    setActionBusy(true);
    try {
      await createContact({
        name: newContactName.trim(),
        contact_type: "work",
        notes: newContactNotes.trim(),
        email_address: newContactEmail.trim(),
        whatsapp_target: newContactWhatsapp.trim(),
      });
      setNewContactName("");
      setNewContactEmail("");
      setNewContactWhatsapp("");
      setNewContactNotes("");
      const payload = await getContacts();
      setContacts(isArray(payload));
    } catch (err) {
      setError(normalizeApiError(err));
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

  const checkForwardApprovalToken = () => {
    const expected = approvalTokenFor(forwardChannel);
    if (forwardApprovalToken.trim() !== expected) {
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
      const result = "Extern geöffnet — Versand liegt beim Nutzer. Friday hat nichts gesendet.";
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

  const handleConnectEmailAccount = async () => {
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
        approval_token: emailAccountToken.trim(),
      });
      setEmailAppPassword("");
      setEmailAccountResult(
        result?.saved
          ? "E-Mail-Konto lokal gespeichert. Real-Versand bleibt aus, bis EMAIL AKTIVIEREN separat freigegeben wird."
          : result?.message || "Konto wurde nicht gespeichert.",
      );
      const status = await getEmailAccountStatus();
      setEmailAccountStatus(status);
    } catch (err) {
      setEmailAccountResult(`Konto konnte nicht verbunden werden: ${normalizeApiError(err)}`);
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

  const handleCreateAccountPolicy = async () => {
    setActionBusy(true);
    setPolicyResult("");
    try {
      const titleContains = policyTitleContains
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);
      const result = await createAccountPolicy({
        provider: policyProvider.trim() || "google_calendar",
        label: policyLabel.trim(),
        role: policyRole.trim() || "source",
        access: policyAccess.trim() || "read",
        include_filters: titleContains.length ? { title_contains: titleContains } : {},
        exclude_filters: {},
        notes: policyNotes,
        enabled: true,
        approval_token: policyToken.trim(),
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

  const handleCreateCalendarEventFromMessage = async () => {
    setActionBusy(true);
    setCalendarWriteResult("");
    try {
      const result = await createCalendarEventFromMessage({
        approval_token: calendarWriteToken.trim(),
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
        await refreshActive();
      } else {
        const reasons = result?.guard?.blocked_reasons || [];
        setCalendarWriteResult(`Termin wurde nicht gespeichert: ${reasons.join(", ") || result?.guard?.message || "unbekannt"}`);
      }
    } catch (err) {
      setCalendarWriteResult(`Termin konnte nicht uebernommen werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleDeleteCalendarEvent = async (entry) => {
    const eventId = entry?.id || entry?.provider_event_id;
    if (!eventId) {
      setCalendarDeleteResult("Termin konnte nicht geloescht werden: Event-ID fehlt.");
      return;
    }
    setActionBusy(true);
    setCalendarDeleteResult("");
    try {
      const result = await deleteCalendarEvent({
        approval_token: (calendarDeleteTokens[eventId] || "").trim(),
        provider_event_id: eventId,
        calendar_id: entry?.calendar_id || calendarAccountStatus?.google?.calendar_id || "primary",
      });
      if (result?.provider_event_deleted) {
        setCalendarDeleteResult("Termin wurde geloescht.");
        setCalendarDeleteTokens((current) => ({ ...current, [eventId]: "" }));
        await refreshActive();
      } else {
        const reasons = result?.guard?.blocked_reasons || [];
        setCalendarDeleteResult(`Termin wurde nicht geloescht: ${reasons.join(", ") || result?.guard?.message || "unbekannt"}`);
      }
    } catch (err) {
      setCalendarDeleteResult(`Termin konnte nicht geloescht werden: ${normalizeApiError(err)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const handleCompleteTask = async (taskId) => {
    setActionBusy(true);
    try {
      await completeTask(taskId);
      await refreshActive();
    } catch (err) {
      setError(normalizeApiError(err));
    } finally {
      setActionBusy(false);
    }
  };

  const handleArchiveTask = async (taskId) => {
    setActionBusy(true);
    try {
      await archiveTask(taskId);
      await refreshActive();
    } catch (err) {
      setError(normalizeApiError(err));
    } finally {
      setActionBusy(false);
    }
  };

  const handleDeleteTask = async (taskId) => {
    setActionBusy(true);
    try {
      await deleteTask(taskId);
      await refreshActive();
    } catch (err) {
      setError(normalizeApiError(err));
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

  const renderScreenContent = () => {
    if (active === "Dashboard") {
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

    if (active === "Tasks") {
      return (
        <View>
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
            <ActionButton label="＋" onPress={handleCreateTask} disabled={actionBusy} />
          </View>
          <View style={styles.forwardBox}>
            <Text style={styles.forwardLabel}>Weiterleiten an Kollege</Text>
            <TextInput
              value={newTaskForwardTo}
              onChangeText={setNewTaskForwardTo}
              style={styles.input}
              placeholder="Name eingeben — lokal, kein Versand"
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
                    {contact.email_address ? ` • ${contact.email_address}` : ""}
                    {contact.whatsapp_target ? ` • WhatsApp: ${contact.whatsapp_target}` : ""}
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
                    onPress={checkForwardApprovalToken}
                    disabled={!forwardApprovalToken.trim()}
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
          {tasks.map((task) => (
            <View key={task.id} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{task.title}</Text>
                <Chip label={toPriorityLabel(task.priority)} color={priorityColor(task.priority)} />
              </View>
              <Text style={styles.cardMeta}>
                #{task.id} • {task.category || "allgemein"} • {task.status || "open"}
                {task.due_date ? ` • fällig ${formatDate(task.due_date)}` : ""}
              </Text>
              {!!task.notes && <Text style={styles.cardBody}>{task.notes}</Text>}
              <View style={styles.row}>
                <ActionButton
                  small
                  variant="success"
                  label="✓ Erledigt"
                  onPress={() => handleCompleteTask(task.id)}
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
          {tasks.length === 0 && <EmptyState icon="✓" text="Alles erledigt — keine Aufgaben offen." />}
        </View>
      );
    }

    if (active === "Nachrichten") {
      return (
        <View>
          <SectionTitle>Nachrichten ({messages.length})</SectionTitle>
          {messages.map((message) => (
            <View key={message.id} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{message.sender || "Unbekannt"}</Text>
                <Text style={styles.cardMeta}>#{message.id}</Text>
              </View>
              <Text style={styles.cardBody}>{message.text || ""}</Text>
              <View style={styles.row}>
                <ActionButton
                  small
                  label="Antwort-Vorschlag"
                  onPress={() => handleMessageSuggestionReply(message.id)}
                  disabled={actionBusy}
                />
                <ActionButton
                  small
                  variant="ghost"
                  label="Aufgabe ableiten"
                  onPress={() => handleGenerateTaskSuggestionForMessage(message.id)}
                  disabled={actionBusy}
                />
                <ActionButton
                  small
                  variant="ghost"
                  label="Termin erkennen"
                  onPress={() => handleGenerateCalendarSuggestionForMessage(message.id)}
                  disabled={actionBusy}
                />
              </View>
            </View>
          ))}
          {!!calendarSuggestionResult && (
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>Termin-Erkennung</Text>
                <Chip label="Review" color={colors.warn} />
              </View>
              <Text style={styles.cardBody}>{calendarSuggestionResult}</Text>
              <Text style={styles.forwardSafety}>
                Friday erstellt nur einen lokalen Vorschlag. Es wird kein Kalendertermin geschrieben.
              </Text>
            </View>
          )}
          {messages.length === 0 && <EmptyState icon="✉" text="Keine Nachrichten." />}
          <SectionTitle>E-Mail-Posteingang (nur lesen)</SectionTitle>
          {!emailInbox?.connected && (
            <View style={styles.card}>
              <Text style={styles.cardBody}>
                {emailInbox?.message || "Kein E-Mail-Konto verbunden."}
              </Text>
            </View>
          )}
          {emailInbox?.connected && isArray(emailInbox.items).map((item, index) => (
            <View key={`${item.subject || "mail"}-${index}`} style={styles.card}>
              <Text style={styles.cardTitle}>{item.subject || "(ohne Betreff)"}</Text>
              <Text style={styles.cardMeta}>Von: {item.sender || "-"}</Text>
              <Text style={styles.cardMeta}>{item.date || ""}</Text>
              <Text style={styles.cardBody}>{item.text_preview || ""}</Text>
            </View>
          ))}

          <SectionTitle>WhatsApp (mitgelesen, letzte 10)</SectionTitle>
          <View style={styles.card}>
            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>Read-Bridge</Text>
              <Chip
                label={whatsappInbox?.status?.read_enabled ? "aktiv" : "aus"}
                color={whatsappInbox?.status?.read_enabled ? colors.warn : colors.textSoft}
              />
            </View>
            <Text style={styles.forwardSafety}>
              Nur Mitlesen. Senden nur durch dich per WhatsApp-Link. Nutzung auf eigenes Risiko.
            </Text>
          </View>
          {isArray(whatsappInbox?.items).map((item, index) => (
            <View key={`${item.synthetic_message_id || "wa"}-${index}`} style={styles.card}>
              <Text style={styles.cardTitle}>{item.sender_name || "WhatsApp"}</Text>
              <Text style={styles.cardMeta}>{item.received_at || ""}</Text>
              <Text style={styles.cardMeta}>Nummer: {item.sender_number_masked || "hash:unknown"}</Text>
              <Text style={styles.cardBody}>{item.body || ""}</Text>
            </View>
          ))}
          {isArray(whatsappInbox?.items).length === 0 && (
            <View style={styles.card}>
              <Text style={styles.cardBody}>Keine lokal gespiegelten WhatsApp-Nachrichten.</Text>
            </View>
          )}

          <SectionTitle>Antwort-Vorschläge</SectionTitle>
          {messageSuggestions.map((suggestion) => (
            <View key={suggestion.id} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardMeta}>
                  Nachricht #{suggestion.message_id || "-"} • {suggestion.suggestion_type || "reply"}
                </Text>
                <Chip
                  label={suggestion.status || "offen"}
                  color={suggestion.status === "preview" ? colors.sage : colors.warn}
                />
              </View>
              <Text style={styles.cardBody}>{suggestion.draft_text || "(keine Vorlage)"}</Text>
              {!!suggestion.notes && <Text style={styles.cardMeta}>{suggestion.notes}</Text>}
              <View style={styles.row}>
                <ActionButton
                  small
                  variant="success"
                  label="Annehmen"
                  onPress={() => handleMessageSuggestionDecision(suggestion.id, "approved")}
                  disabled={actionBusy || suggestion.id.toString().startsWith("preview-")}
                />
                <ActionButton
                  small
                  variant="danger"
                  label="Ablehnen"
                  onPress={() => handleMessageSuggestionDecision(suggestion.id, "rejected")}
                  disabled={actionBusy || suggestion.id.toString().startsWith("preview-")}
                />
              </View>
            </View>
          ))}

          <SectionTitle>Aufgaben-Vorschläge</SectionTitle>
          {taskSuggestions.map((suggestion) => (
            <View key={suggestion.id} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{suggestion.title}</Text>
                <Chip label={toPriorityLabel(suggestion.priority)} color={priorityColor(suggestion.priority)} />
              </View>
              <Text style={styles.cardMeta}>
                Aus Nachricht #{suggestion.message_id || "-"} • {suggestion.status || "offen"}
              </Text>
              {!!suggestion.notes && <Text style={styles.cardBody}>{suggestion.notes}</Text>}
              <View style={styles.row}>
                <ActionButton
                  small
                  variant="success"
                  label="Annehmen"
                  onPress={() => handleTaskSuggestionDecision(suggestion.id, "approved")}
                  disabled={actionBusy}
                />
                <ActionButton
                  small
                  variant="danger"
                  label="Ablehnen"
                  onPress={() => handleTaskSuggestionDecision(suggestion.id, "rejected")}
                  disabled={actionBusy}
                />
              </View>
            </View>
          ))}
          {messageSuggestions.length === 0 && taskSuggestions.length === 0 && (
            <EmptyState icon="💡" text="Noch keine Vorschläge." />
          )}
        </View>
      );
    }

    if (active === "Kalender") {
      const items = isArray(calendar?.items || calendar?.calendar_items || []);
      const slots = isArray(calendar?.free_slots || []);
      const googleEvents = isArray(googleCalendarPreview?.events);
      const sourceEvents = isArray(calendar?.source_events);
      const sourceErrors = isArray(calendar?.source_errors);
      const googleConnected = Boolean(calendarAccountStatus?.google?.connected);
      return (
        <View>
          <SectionTitle>Termin übernehmen</SectionTitle>
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Nachricht in Kalendertermin umwandeln</Text>
            <Text style={styles.cardBody}>
              Friday erkennt den Termin lokal, du kannst alles bearbeiten und erst `TERMIN SPEICHERN` schreibt in Google.
            </Text>
            <TextInput
              value={calendarMessageText}
              onChangeText={setCalendarMessageText}
              style={styles.input}
              placeholder="Nachricht mit Termintext"
              placeholderTextColor={colors.textSoft}
              multiline
            />
            <TextInput
              value={calendarDraftTitle}
              onChangeText={setCalendarDraftTitle}
              style={styles.input}
              placeholder="Titel optional überschreiben"
              placeholderTextColor={colors.textSoft}
            />
            <TextInput
              value={calendarDraftDate}
              onChangeText={setCalendarDraftDate}
              style={styles.input}
              placeholder="Datum optional: 2026-07-15"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <TextInput
              value={calendarDraftStart}
              onChangeText={setCalendarDraftStart}
              style={styles.input}
              placeholder="Start optional: 10:00"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <TextInput
              value={calendarDraftEnd}
              onChangeText={setCalendarDraftEnd}
              style={styles.input}
              placeholder="Ende optional: 11:00"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="none"
            />
            <TextInput
              value={calendarDraftLocation}
              onChangeText={setCalendarDraftLocation}
              style={styles.input}
              placeholder="Ort optional"
              placeholderTextColor={colors.textSoft}
            />
            <TextInput
              value={calendarWriteToken}
              onChangeText={setCalendarWriteToken}
              style={styles.input}
              placeholder="TERMIN SPEICHERN"
              placeholderTextColor={colors.textSoft}
              autoCapitalize="characters"
            />
            <ActionButton
              label="Termin übernehmen"
              onPress={handleCreateCalendarEventFromMessage}
              disabled={actionBusy || !calendarMessageText.trim()}
            />
            {!!calendarWriteResult && <Text style={styles.approvalResultText}>{calendarWriteResult}</Text>}
          </View>
          <SectionTitle>Google-Kalender</SectionTitle>
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>Google-Verbindung</Text>
              <Chip
                label={googleConnected ? "verbunden" : "nicht verbunden"}
                color={googleConnected ? colors.success : colors.textSoft}
              />
            </View>
            <Text style={styles.cardMeta}>
              Kalender: {calendarAccountStatus?.google?.calendar_id || "-"}
            </Text>
            <Text style={styles.cardMeta}>
              Verbindungstest: {calendarAccountStatus?.google?.last_test_ok ? "OK" : "nicht geprüft"}
            </Text>
            <Text style={styles.cardMeta}>
              Modus: nur lesen · Schreiben {googleCalendarPreview?.write_enabled ? "aktiv" : "aus"}
            </Text>
            {!!googleCalendarPreview?.message && (
              <Text style={styles.cardBody}>{googleCalendarPreview.message}</Text>
            )}
          </View>
          {googleEvents.map((entry) => (
            <View key={entry.id ?? `${entry.calendar_id}-${entry.start}-${entry.end}`} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{entry.title || "Google-Termin"}</Text>
                <Chip label="Google" color={colors.sage} />
              </View>
              <Text style={styles.cardMeta}>
                {formatCalendarMoment(entry.start)} – {formatCalendarMoment(entry.end)}
              </Text>
              {!!entry.location && <Text style={styles.cardMeta}>Ort: {entry.location}</Text>}
              <TextInput
                value={calendarDeleteTokens[entry.id] || ""}
                onChangeText={(value) =>
                  setCalendarDeleteTokens((current) => ({ ...current, [entry.id]: value }))
                }
                style={styles.input}
                placeholder="TERMIN LOESCHEN"
                placeholderTextColor={colors.textSoft}
                autoCapitalize="characters"
              />
              <ActionButton
                label="Termin löschen"
                onPress={() => handleDeleteCalendarEvent(entry)}
                disabled={actionBusy || !entry.id}
                tone="danger"
              />
            </View>
          ))}
          {!!calendarDeleteResult && <Text style={styles.approvalResultText}>{calendarDeleteResult}</Text>}
          {googleConnected && googleEvents.length === 0 && (
            <EmptyState icon="▦" text="Keine Google-Termine in den nächsten 30 Tagen gefunden." />
          )}
          {!googleConnected && (
            <EmptyState icon="▦" text="Google-Kalender ist noch nicht verbunden." />
          )}
          <SectionTitle>Kalender-Quellen</SectionTitle>
          {sourceEvents.map((entry) => (
            <View key={`${entry.provider}-${entry.id}-${entry.start}`} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{entry.title || "Quellen-Termin"}</Text>
                <Chip label={entry.policy_label || entry.provider || "Quelle"} color={colors.sage} />
              </View>
              <Text style={styles.cardMeta}>
                {formatCalendarMoment(entry.start)} – {formatCalendarMoment(entry.end)}
              </Text>
              {!!entry.location && <Text style={styles.cardMeta}>Ort: {entry.location}</Text>}
            </View>
          ))}
          {sourceEvents.length === 0 && <EmptyState icon="▦" text="Keine gefilterten Quellen-Termine gefunden." />}
          {sourceErrors.map((error, index) => (
            <Text key={`${error.policy_id}-${index}`} style={styles.cardMeta}>
              Quelle nicht geladen: {error.provider} · {(error.blocked_reasons || []).join(", ")}
            </Text>
          ))}
          <SectionTitle>Termine am {calendar?.date || "-"}</SectionTitle>
          {items.map((entry) => (
            <View key={entry.id ?? `${entry.date}-${entry.start}-${entry.end}`} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{entry.title || "Termin"}</Text>
                <Chip label={entry.item_type || "busy"} color={colors.accent} />
              </View>
              <Text style={styles.cardMeta}>
                {formatCalendarMoment(entry.start)} – {formatCalendarMoment(entry.end)} • {entry.date || calendar?.date}
              </Text>
            </View>
          ))}
          {items.length === 0 && <EmptyState icon="▦" text="Keine Termine heute." />}
          <SectionTitle>Freie Slots</SectionTitle>
          {slots.map((slot, index) => (
            <View key={`${slot.start}-${slot.end}-${index}`} style={styles.slotCard}>
              <Text style={styles.slotText}>
                {slot.start || "-"} – {slot.end || "-"}
              </Text>
              <Text style={styles.slotFree}>frei</Text>
            </View>
          ))}
          {slots.length === 0 && <EmptyState icon="◷" text="Keine Freizeiten im Standardfenster." />}
        </View>
      );
    }

    if (active === "Kontakte") {
      return (
        <View>
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
              {!!contact.email_address && <Text style={styles.cardMeta}>E-Mail: {contact.email_address}</Text>}
              {!!contact.whatsapp_target && <Text style={styles.cardMeta}>WhatsApp: {contact.whatsapp_target}</Text>}
            </View>
          ))}
          {contacts.length === 0 && <EmptyState icon="☺" text="Keine Kontakte." />}
        </View>
      );
    }

    if (active === "Datenschutz") {
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
      return (
        <View>
          <View style={styles.privacyBanner}>
            <Text style={styles.privacyBannerIcon}>🛡</Text>
            <Text style={styles.privacyBannerText}>
              Modus: {privacy?.mode || "local"} — deine Daten bleiben auf deinen Geräten.
            </Text>
          </View>
          <SectionTitle>Externe Dienste</SectionTitle>
          <View style={styles.card}>
            {services.map(([label, value]) => (
              <View key={label} style={styles.privacyRow}>
                <Text style={styles.privacyLabel}>{label}</Text>
                <Chip
                  label={value ? "aktiv" : "aus"}
                  color={value ? colors.warn : colors.success}
                />
              </View>
            ))}
          </View>
          <SectionTitle>Lokale Schreibzugriffe</SectionTitle>
          <View style={styles.card}>
            {writeRows.map(([label, value]) => (
              <View key={label} style={styles.privacyRow}>
                <Text style={styles.privacyLabel}>{label}</Text>
                <Chip
                  label={value ? "erlaubt" : "gesperrt"}
                  color={value ? colors.sage : colors.textSoft}
                />
              </View>
            ))}
          </View>
          {!!note && <Text style={styles.privacyNote}>{note}</Text>}
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
                onPress={handleConnectEmailAccount}
                disabled={actionBusy}
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
          </View>
          <View style={styles.card}>
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
            <Text style={styles.cardBody}>
              WhatsApp-Senden bleibt ueber dein Handy: Friday befuellt die Nachricht, du tippst selbst auf Senden.
              Die Read-Bridge liest nur eingehende Einzelchats und nutzt keine Auto-Antwort.
            </Text>
            <Text style={styles.forwardSafety}>
              Risiko: WhatsApp-Web-Bridges koennen gegen WhatsApp-Regeln verstossen. Nutzung auf eigenes Risiko.
            </Text>
          </View>
        </View>
      );
    }

    if (active === "Setup") {
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
              Kalender-Schreiben: {setupStatus?.calendar?.real_enabled ? "aktiv" : "aus"} — Vorschläge gehen immer in den Review.
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
              onPress={handleCreateAccountPolicy}
              disabled={actionBusy || !policyLabel.trim()}
            />
            {!!policyResult && <Text style={styles.approvalResultText}>{policyResult}</Text>}
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Gespeicherte Policies</Text>
            {isArray(accountPolicies?.items).map((policy) => (
              <View key={policy.id || policy.label} style={styles.privacyRow}>
                <Text style={styles.privacyLabel}>{policy.label}</Text>
                <Chip label={`${policy.provider} / ${policy.role}`} color={policy.enabled ? colors.sage : colors.textSoft} />
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
            <Text style={styles.cardTitle}>Verbindungen</Text>
            <View style={styles.privacyRow}>
              <Text style={styles.privacyLabel}>E-Mail</Text>
              <Chip label={setupStatus?.email?.configured ? "konfiguriert" : "nicht verbunden"} color={setupStatus?.email?.configured ? colors.warn : colors.textSoft} />
            </View>
            <View style={styles.privacyRow}>
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

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.bg} />
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
            <View style={styles.logo}>
              <Text style={styles.logoText}>F</Text>
            </View>
            <View>
              <Text style={styles.heading}>{greeting()}!</Text>
              <Text style={styles.subheading}>{todayLabel()}</Text>
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
              {online === null ? "Prüfe…" : online ? "Verbunden" : "Offline"}
            </Text>
          </View>
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabScroll}>
          <View style={styles.tabs}>
            {screens.map(({ key, icon }) => (
              <TouchableOpacity
                key={key}
                onPress={() => setActive(key)}
                style={[styles.tab, active === key && styles.tabActive]}
                activeOpacity={0.7}
              >
                <Text style={[styles.tabIcon, active === key && styles.tabTextActive]}>{icon}</Text>
                <Text style={[styles.tabText, active === key && styles.tabTextActive]}>{key}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>

        {loading && (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        )}
        {!!error && (
          <View style={styles.errorBanner}>
            <Text style={styles.errorText}>{error}</Text>
            <ActionButton small variant="ghost" label="Erneut versuchen" onPress={refreshActive} />
          </View>
        )}
        {!loading && !error && renderScreenContent()}
        {actionBusy && <Text style={styles.busyHint}>Aktion läuft…</Text>}
        <Text style={styles.footer}>Friday 1.0 • lokal & privat • {updateStatus} • {getApiUrl()}</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
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
  buttonGhost: {
    backgroundColor: colors.accentSoft,
    shadowOpacity: 0,
    elevation: 0,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: "#f8f5ec",
    fontSize: 14,
    fontWeight: "700",
  },
  buttonTextSmall: {
    fontSize: 12,
  },
  buttonGhostText: {
    color: colors.accent,
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
});
