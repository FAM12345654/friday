import Constants from "expo-constants";

const API_URL =
  process.env.EXPO_PUBLIC_FRIDAY_API_URL ||
  Constants.expoConfig?.extra?.fridayApiDefaultUrl ||
  "https://cholesterol-ampland-donated-treat.trycloudflare.com";

async function callApi(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const payload = await response.json().catch(() => ({ ok: false, message: "Ung?ltiges JSON" }));
  if (!response.ok || payload?.ok === false) {
    throw new Error(payload?.detail || payload?.message || `HTTP ${response.status}`);
  }
  return payload.data;
}

export async function getDashboard() {
  return callApi("/api/dashboard");
}

export async function getTasks() {
  return callApi("/api/tasks");
}

export async function getTask(taskId) {
  return callApi(`/api/tasks/${taskId}`);
}

export async function createTask(payload) {
  return callApi("/api/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateTask(taskId, payload) {
  return callApi(`/api/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function completeTask(taskId) {
  return callApi(`/api/tasks/${taskId}/done`, {
    method: "POST",
  });
}

export async function archiveTask(taskId) {
  return callApi(`/api/tasks/${taskId}/archive`, {
    method: "POST",
  });
}

export async function deleteTask(taskId) {
  return callApi(`/api/tasks/${taskId}`, {
    method: "DELETE",
  });
}

export async function getMessages() {
  return callApi("/api/messages");
}

export async function getMessageSuggestions() {
  return callApi("/api/messages/suggestions");
}

export async function getMessageSuggestion(messageId) {
  return callApi(`/api/messages/${messageId}/reply`);
}

export async function approveMessageSuggestion(suggestionId) {
  return callApi(`/api/messages/suggestions/${suggestionId}/approve`, {
    method: "POST",
  });
}

export async function rejectMessageSuggestion(suggestionId) {
  return callApi(`/api/messages/suggestions/${suggestionId}/reject`, {
    method: "POST",
  });
}

export async function approveTaskSuggestion(suggestionId) {
  return callApi(`/api/messages/task-suggestions/${suggestionId}/approve`, {
    method: "POST",
  });
}

export async function rejectTaskSuggestion(suggestionId) {
  return callApi(`/api/messages/task-suggestions/${suggestionId}/reject`, {
    method: "POST",
  });
}

export async function generateTaskSuggestionsForMessage(messageId) {
  return callApi(`/api/messages/${messageId}/task-suggestions`, {
    method: "POST",
  });
}

export async function getContacts() {
  return callApi("/api/contacts");
}

export async function getPrivacy() {
  return callApi("/api/privacy");
}

export async function getCalendar(date) {
  const query = date ? `?date=${encodeURIComponent(date)}` : "";
  return callApi(`/api/calendar${query}`);
}

export async function getCalendarSlots(messageId, durationMinutes = 60) {
  const query = new URLSearchParams({
    duration_minutes: String(durationMinutes),
  }).toString();
  return callApi(`/api/calendar/${messageId}/slots?${query}`);
}
