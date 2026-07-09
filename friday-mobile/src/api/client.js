import Constants from "expo-constants";

// Kandidaten-URLs: zuhause gewinnt das lokale WLAN, unterwegs der Tunnel.
// Reihenfolge = Präferenz. Die App prüft alle parallel und nimmt den ersten
// erreichbaren Kandidaten in Listenreihenfolge.
const buildCandidates = () => {
  const fromEnvList = (process.env.EXPO_PUBLIC_FRIDAY_API_URLS || "")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
  const fromEnvSingle = process.env.EXPO_PUBLIC_FRIDAY_API_URL;
  const extra = Constants.expoConfig?.extra || {};
  const fromExtraList = Array.isArray(extra.fridayApiUrls) ? extra.fridayApiUrls : [];
  const fromExtraSingle = extra.fridayApiDefaultUrl;

  const merged = [
    ...fromEnvList,
    fromEnvSingle,
    ...fromExtraList,
    fromExtraSingle,
    "http://192.168.178.42:8000",
  ].filter(Boolean);

  return [...new Set(merged)];
};

const CANDIDATES = buildCandidates();

let activeUrl = null;

async function probe(url, timeoutMs = 4000) {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const response = await fetch(`${url}/health`, { signal: controller.signal });
    clearTimeout(timer);
    const payload = await response.json().catch(() => null);
    return Boolean(response.ok && payload?.ok !== false);
  } catch (err) {
    return false;
  }
}

async function resolveApiUrl(force = false) {
  if (activeUrl && !force) {
    return activeUrl;
  }

  const results = await Promise.all(CANDIDATES.map((url) => probe(url)));
  const index = results.findIndex(Boolean);
  activeUrl = index >= 0 ? CANDIDATES[index] : null;
  return activeUrl || CANDIDATES[0];
}

export function getApiUrl() {
  return activeUrl || CANDIDATES[0];
}

export async function checkHealth() {
  await resolveApiUrl(true);
  return activeUrl !== null;
}

const isNetworkError = (error) =>
  /network|abort|fehlgeschlagen|failed to fetch/i.test(String(error?.message || ""));

async function request(baseUrl, path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const payload = await response.json().catch(() => ({ ok: false, message: "Ungültiges JSON" }));
  if (!response.ok || payload?.ok === false) {
    throw new Error(payload?.detail || payload?.message || `HTTP ${response.status}`);
  }
  return payload.data;
}

async function callApi(path, options = {}) {
  const baseUrl = await resolveApiUrl();
  try {
    return await request(baseUrl, path, options);
  } catch (error) {
    if (isNetworkError(error)) {
      const nextUrl = await resolveApiUrl(true);
      if (nextUrl && nextUrl !== baseUrl) {
        return request(nextUrl, path, options);
      }
    }
    throw error;
  }
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

export async function generateCalendarEventSuggestionForMessage(messageId) {
  return callApi(`/api/messages/${messageId}/calendar-event-suggestions`, {
    method: "POST",
  });
}

export async function extractCalendarEvent(payload) {
  return callApi("/api/calendar/extract-event", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getContacts() {
  return callApi("/api/contacts");
}

export async function createContact(payload) {
  return callApi("/api/contacts", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function buildTaskForwardDraft(payload) {
  return callApi("/api/ai/task-forward-draft", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function sendTaskForwardEmail(payload) {
  return callApi("/api/accounts/email/send-task-forward", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getEmailAccountStatus() {
  return callApi("/api/accounts/email/status");
}

export async function connectEmailAccount(payload) {
  return callApi("/api/accounts/email/connect", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function testEmailAccountConnection() {
  return callApi("/api/accounts/email/test", {
    method: "POST",
  });
}

export async function deleteEmailAccount(payload) {
  return callApi("/api/accounts/email", {
    method: "DELETE",
    body: JSON.stringify(payload),
  });
}

export async function getEmailInbox(limit = 10) {
  return callApi(`/api/messages/email-inbox?limit=${encodeURIComponent(String(limit))}`);
}

export async function getWhatsAppStatus() {
  return callApi("/api/whatsapp/status");
}

export async function getWhatsAppMessages(limit = 10) {
  return callApi(`/api/whatsapp/messages?limit=${encodeURIComponent(String(limit))}`);
}

export async function getSetupStatus() {
  return callApi("/api/setup/status");
}

export async function getAccountPolicies() {
  return callApi("/api/accounts/policies");
}

export async function createAccountPolicy(payload) {
  return callApi("/api/accounts/policies", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getCalendarAccountStatus() {
  return callApi("/api/accounts/calendar/status");
}

export async function checkCalendarActivationGate(payload) {
  return callApi("/api/accounts/calendar/activation-gate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getPrivacy() {
  return callApi("/api/privacy");
}

export async function getCalendar(date) {
  const query = date ? `?date=${encodeURIComponent(date)}` : "";
  return callApi(`/api/calendar${query}`);
}

export async function getGoogleCalendarReadPreview(rangeStart, rangeEnd) {
  const query = new URLSearchParams({
    range_start: String(rangeStart),
    range_end: String(rangeEnd),
  }).toString();
  return callApi(`/api/accounts/calendar/google/read-preview?${query}`);
}

export async function getCalendarSlots(messageId, durationMinutes = 60) {
  const query = new URLSearchParams({
    duration_minutes: String(durationMinutes),
  }).toString();
  return callApi(`/api/calendar/${messageId}/slots?${query}`);
}
