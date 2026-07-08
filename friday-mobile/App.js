import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Button,
  SafeAreaView,
  ScrollView,
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
  completeTask,
  createTask,
  deleteTask,
  generateTaskSuggestionsForMessage,
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
  "Dashboard",
  "Tasks",
  "Nachrichten",
  "Kalender",
  "Kontakte",
  "Datenschutz",
];

const formatDate = (value) => {
  if (!value) {
    return "";
  }
  return String(value);
};

const isArray = (value) => (Array.isArray(value) ? value : []);

const toPriorityLabel = (value) => value ? String(value).trim() || "normal" : "normal";

const normalizeApiError = (error) => {
  if (!error || !error.message) {
    return "Unbekannter Fehler";
  }
  return String(error.message);
};

export default function App() {
  const [active, setActive] = useState("Dashboard");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [messages, setMessages] = useState([]);
  const [messageSuggestions, setMessageSuggestions] = useState([]);
  const [taskSuggestions, setTaskSuggestions] = useState([]);
  const [calendar, setCalendar] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [privacy, setPrivacy] = useState(null);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [actionBusy, setActionBusy] = useState(false);

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

  const handleCreateTask = async () => {
    if (!newTaskTitle.trim()) {
      return;
    }
    setActionBusy(true);
    try {
      await createTask({ title: newTaskTitle });
      setNewTaskTitle("");
      await refreshActive();
    } catch (err) {
      setError(normalizeApiError(err));
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
          <Text style={styles.title}>Dashboard ({dashboard?.date || "-"})</Text>
          <Text style={styles.item}>Offene Tasks: {summary.open_tasks || 0}</Text>
          <Text style={styles.item}>Nachrichten: {summary.messages || 0}</Text>
          <Text style={styles.item}>Kalender-Events heute: {summary.calendar_items_today || 0}</Text>
          <Text style={styles.item}>Kontakte: {summary.contacts || 0}</Text>
        </View>
      );
    }

    if (active === "Tasks") {
      return (
        <View>
          <Text style={styles.title}>Aufgaben</Text>
          <Text style={styles.item}>Neue Aufgabe:</Text>
          <View style={styles.row}>
            <TextInput
              value={newTaskTitle}
              onChangeText={setNewTaskTitle}
              style={styles.input}
              placeholder="Titel..."
              placeholderTextColor="#94a3b8"
            />
            <Button title="Hinzufügen" onPress={handleCreateTask} disabled={actionBusy} />
          </View>
          {tasks.map((task) => (
            <View key={task.id} style={styles.card}>
              <Text style={styles.item}>#{task.id} {task.title}</Text>
              <Text style={styles.hint}>
                {task.category || "allgemein"} • {task.status || "open"} • {toPriorityLabel(task.priority)}
              </Text>
              <Text style={styles.hint}>Fällig: {formatDate(task.due_date) || "-"}</Text>
              <View style={styles.row}>
                <TouchableOpacity
                  style={styles.smallButton}
                  onPress={() => handleCompleteTask(task.id)}
                  disabled={actionBusy}
                >
                  <Text style={styles.smallButtonText}>Erledigt</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.smallButton}
                  onPress={() => handleArchiveTask(task.id)}
                  disabled={actionBusy}
                >
                  <Text style={styles.smallButtonText}>Archiv</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.smallButtonDanger}
                  onPress={() => handleDeleteTask(task.id)}
                  disabled={actionBusy}
                >
                  <Text style={styles.smallButtonText}>Löschen</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
          {tasks.length === 0 && <Text style={styles.empty}>Keine Aufgaben gefunden.</Text>}
        </View>
      );
    }

    if (active === "Nachrichten") {
      return (
        <View>
          <Text style={styles.title}>Nachrichten &amp; Vorschläge</Text>
          <Text style={styles.subtitle}>Nachrichten ({messages.length})</Text>
          {messages.map((message) => (
            <View key={message.id} style={styles.card}>
              <Text style={styles.item}>#{message.id} {message.sender || "-"}</Text>
              <Text style={styles.hint}>{message.text || ""}</Text>
              <View style={styles.row}>
                <Button
                  title="Reply-Vorschlag"
                  onPress={() => handleMessageSuggestionReply(message.id)}
                  disabled={actionBusy}
                />
                <Button
                  title="Task-Suggestion prüfen"
                  onPress={() => handleGenerateTaskSuggestionForMessage(message.id)}
                  disabled={actionBusy}
                />
              </View>
            </View>
          ))}
          {messages.length === 0 && <Text style={styles.empty}>Keine Nachrichten.</Text>}

          <Text style={styles.subtitle}>Nachrichten-Vorschläge</Text>
          {messageSuggestions.map((suggestion) => (
            <View key={suggestion.id} style={styles.card}>
              <Text style={styles.item}>ID {suggestion.id} {suggestion.status || ""}</Text>
              <Text style={styles.hint}>
                Message #{suggestion.message_id || "-"} • {suggestion.suggestion_type || "reply"}
              </Text>
              <Text style={styles.hint}>{suggestion.draft_text || "(keine Vorlage)"}</Text>
              <Text style={styles.hint}>{suggestion.notes || ""}</Text>
              <View style={styles.row}>
                <Button
                  title="Annehmen"
                  onPress={() => handleMessageSuggestionDecision(suggestion.id, "approved")}
                  disabled={actionBusy || suggestion.id.toString().startsWith("preview-")}
                />
                <Button
                  title="Ablehnen"
                  onPress={() => handleMessageSuggestionDecision(suggestion.id, "rejected")}
                  disabled={actionBusy || suggestion.id.toString().startsWith("preview-")}
                />
              </View>
            </View>
          ))}

          <Text style={styles.subtitle}>Task-Vorschläge</Text>
          {taskSuggestions.map((suggestion) => (
            <View key={suggestion.id} style={styles.card}>
              <Text style={styles.item}>ID {suggestion.id} {suggestion.status || ""}</Text>
              <Text style={styles.hint}>From message #{suggestion.message_id || "-"}</Text>
              <Text style={styles.item}>{suggestion.title}</Text>
              <Text style={styles.hint}>{suggestion.notes || ""}</Text>
              <Text style={styles.hint}>Priorität: {toPriorityLabel(suggestion.priority)}</Text>
              <View style={styles.row}>
                <Button
                  title="Annehmen"
                  onPress={() => handleTaskSuggestionDecision(suggestion.id, "approved")}
                  disabled={actionBusy}
                />
                <Button
                  title="Ablehnen"
                  onPress={() => handleTaskSuggestionDecision(suggestion.id, "rejected")}
                  disabled={actionBusy}
                />
              </View>
            </View>
          ))}
          {messageSuggestions.length === 0 && taskSuggestions.length === 0 && (
            <Text style={styles.empty}>Noch keine Vorschläge.</Text>
          )}
        </View>
      );
    }

    if (active === "Kalender") {
      const items = isArray(calendar?.items || calendar?.calendar_items || []);
      const slots = isArray(calendar?.free_slots || []);
      return (
        <View>
          <Text style={styles.title}>Kalender ({calendar?.date || "-"})</Text>
          <Text style={styles.subtitle}>Termine</Text>
          {items.map((entry) => (
            <View key={entry.id ?? `${entry.date}-${entry.start}-${entry.end}`} style={styles.card}>
              <Text style={styles.item}>
                {entry.title || "Termin"} ({entry.start || "?"} - {entry.end || "?"})
              </Text>
              <Text style={styles.hint}>Typ: {entry.item_type || "busy"} • Datum: {entry.date || calendar?.date}</Text>
            </View>
          ))}
          {items.length === 0 && <Text style={styles.empty}>Keine Termine.</Text>}
          <Text style={styles.subtitle}>Freie Slots</Text>
          {slots.map((slot, index) => (
            <View key={`${slot.start}-${slot.end}-${index}`} style={styles.card}>
              <Text style={styles.item}>von {slot.start || "-"} bis {slot.end || "-"}</Text>
            </View>
          ))}
          {slots.length === 0 && <Text style={styles.empty}>Keine Freizeiten im Standardfenster.</Text>}
        </View>
      );
    }

    if (active === "Kontakte") {
      return (
        <View>
          <Text style={styles.title}>Kontakte</Text>
          {contacts.map((contact) => (
            <View key={contact.id ?? contact.name} style={styles.card}>
              <Text style={styles.item}>{contact.name || "Unbekannt"}</Text>
              <Text style={styles.hint}>{contact.contact_type || "other"} • {contact.id ? `ID ${contact.id}` : ""}</Text>
              <Text style={styles.hint}>{contact.notes || ""}</Text>
            </View>
          ))}
          {contacts.length === 0 && <Text style={styles.empty}>Keine Kontakte.</Text>}
        </View>
      );
    }

    if (active === "Datenschutz") {
      const external = privacy?.external_services || {};
      const writes = privacy?.writes || {};
      const note = privacy?.notes || "";
      return (
        <View>
          <Text style={styles.title}>Datenschutz</Text>
          <Text style={styles.item}>Mode: {privacy?.mode || "local"}</Text>
          <Text style={styles.subtitle}>Externe Dienste</Text>
          <Text style={styles.hint}>Email: {String(external.email)}</Text>
          <Text style={styles.hint}>WhatsApp: {String(external.whatsapp)}</Text>
          <Text style={styles.hint}>SMS: {String(external.sms)}</Text>
          <Text style={styles.hint}>Kalender: {String(external.calendar)}</Text>
          <Text style={styles.hint}>Weather: {String(external.weather)}</Text>
          <Text style={styles.hint}>Music: {String(external.music)}</Text>
          <Text style={styles.subtitle}>Lokale Schreibzugriffe</Text>
          <Text style={styles.hint}>Exports: {String(writes.exports)}</Text>
          <Text style={styles.hint}>Nachrichten senden: {String(writes.messages_send)}</Text>
          <Text style={styles.hint}>Kontakte-Änderung: {String(writes.contacts_write)}</Text>
          <Text style={styles.subtitle}>Hinweis</Text>
          <Text style={styles.hint}>{note}</Text>
        </View>
      );
    }

    return null;
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.heading}>Friday Mobile</Text>
        <Text style={styles.subheading}>Dark Theme • 6 Bereiche</Text>
        <View style={styles.tabs}>
          {screens.map((screenName) => (
            <TouchableOpacity
              key={screenName}
              onPress={() => setActive(screenName)}
              style={[styles.tab, active === screenName && styles.tabActive]}
            >
              <Text style={[styles.tabText, active === screenName && styles.tabTextActive]}>{screenName}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.contentCard}>
          {loading && <ActivityIndicator color="#60a5fa" />}
          {!!error && <Text style={styles.error}>Fehler: {error}</Text>}
          {!loading && !error && renderScreenContent()}
          {!loading && <Button title="Aktualisieren" onPress={refreshActive} />}
          {actionBusy && <Text style={styles.hint}>Aktion läuft…</Text>}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#0b1220",
    flex: 1,
  },
  scroll: {
    padding: 16,
  },
  heading: {
    color: "#e5e7eb",
    fontSize: 24,
    fontWeight: "700",
  },
  subheading: {
    color: "#94a3b8",
    marginTop: 8,
  },
  title: {
    color: "#f8fafc",
    fontSize: 20,
    marginBottom: 8,
    marginTop: 12,
    fontWeight: "700",
  },
  subtitle: {
    color: "#cbd5e1",
    fontSize: 18,
    marginBottom: 8,
    marginTop: 12,
    fontWeight: "600",
  },
  item: {
    color: "#cbd5e1",
    fontSize: 16,
    marginBottom: 4,
  },
  hint: {
    color: "#94a3b8",
    fontSize: 13,
    marginBottom: 4,
  },
  tabs: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 12,
    marginBottom: 14,
  },
  tab: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#334155",
    backgroundColor: "#0f172a",
  },
  tabActive: {
    backgroundColor: "#2563eb",
    borderColor: "#60a5fa",
  },
  tabText: {
    color: "#cbd5e1",
    fontSize: 12,
    fontWeight: "600",
  },
  tabTextActive: {
    color: "#f8fafc",
  },
  contentCard: {
    backgroundColor: "#111827",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#1f2937",
    padding: 12,
  },
  card: {
    borderWidth: 1,
    borderColor: "#1f2937",
    backgroundColor: "#0b1220",
    borderRadius: 12,
    padding: 10,
    marginBottom: 10,
  },
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 10,
    marginBottom: 4,
  },
  smallButton: {
    backgroundColor: "#334155",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  smallButtonDanger: {
    backgroundColor: "#7f1d1d",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  smallButtonText: {
    color: "#f8fafc",
    fontSize: 12,
    fontWeight: "600",
  },
  input: {
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    color: "#f8fafc",
    paddingHorizontal: 10,
    paddingVertical: 8,
    marginBottom: 8,
    flex: 1,
    minWidth: 180,
  },
  empty: {
    color: "#94a3b8",
    marginTop: 8,
  },
  error: {
    color: "#f87171",
    marginTop: 12,
    fontSize: 16,
  },
  divider: {
    height: 1,
    backgroundColor: "#1e293b",
    marginVertical: 16,
  },
});
