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
  createContact,
  createTask,
  deleteTask,
  generateTaskSuggestionsForMessage,
  getApiUrl,
  getCalendar,
  getContacts,
  getDashboard,
  getMessageSuggestion,
  getMessageSuggestions,
  getMessages,
  getPrivacy,
  getTasks,
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
  const [contacts, setContacts] = useState([]);
  const [newContactName, setNewContactName] = useState("");
  const [newContactEmail, setNewContactEmail] = useState("");
  const [newContactWhatsapp, setNewContactWhatsapp] = useState("");
  const [newContactNotes, setNewContactNotes] = useState("");
  const [privacy, setPrivacy] = useState(null);
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
      const list = messagePayload?.items || [];
      setMessages(isArray(list));
      setMessageSuggestions(isArray(suggestions?.message_suggestions));
      setTaskSuggestions(isArray(suggestions?.task_suggestions));
      return;
    }

    if (screenName === "Kalender") {
      const payload = await getCalendar();
      setCalendar(payload);
      return;
    }

    if (screenName === "Kontakte") {
      const payload = await getContacts();
      setContacts(isArray(payload));
      return;
    }

    if (screenName === "Datenschutz") {
      const payload = await getPrivacy();
      setPrivacy(payload);
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
              </View>
            </View>
          ))}
          {messages.length === 0 && <EmptyState icon="✉" text="Keine Nachrichten." />}

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
      return (
        <View>
          <SectionTitle>Termine am {calendar?.date || "-"}</SectionTitle>
          {items.map((entry) => (
            <View key={entry.id ?? `${entry.date}-${entry.start}-${entry.end}`} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{entry.title || "Termin"}</Text>
                <Chip label={entry.item_type || "busy"} color={colors.accent} />
              </View>
              <Text style={styles.cardMeta}>
                {entry.start || "?"} – {entry.end || "?"} • {entry.date || calendar?.date}
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
