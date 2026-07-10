import * as SQLite from "expo-sqlite";

const DB_NAME = "friday_mobile_cache.db";

export const cacheTypes = {
  dashboard: "dashboard",
  tasks: "tasks",
  calendar: "calendar",
  weekCalendar: "weekCalendar",
  calendarViewPrefs: "calendarViewPrefs",
  googleCalendarPreview: "googleCalendarPreview",
  calendarAccountStatus: "calendarAccountStatus",
  messages: "messages",
  messageSuggestions: "messageSuggestions",
  emailInbox: "emailInbox",
  unifiedMailInbox: "unifiedMailInbox",
  whatsappInbox: "whatsappInbox",
  blockedSenders: "blockedSenders",
  spamMessages: "spamMessages",
  contacts: "contacts",
  learning: "learning",
  privacy: "privacy",
  setupStatus: "setupStatus",
  accountPolicies: "accountPolicies",
  emailAccountStatus: "emailAccountStatus",
  msMailStatus: "msMailStatus",
  imapMailStatus: "imapMailStatus",
  mailOrganizeLog: "mailOrganizeLog",
  whatsappStatus: "whatsappStatus",
  whatsappAgentNotes: "whatsappAgentNotes",
};

let dbPromise = null;

const nowIso = () => new Date().toISOString();

async function getDb() {
  if (!dbPromise) {
    dbPromise = SQLite.openDatabaseAsync(DB_NAME).then(async (db) => {
      await db.execAsync(`
        PRAGMA journal_mode = WAL;
        CREATE TABLE IF NOT EXISTS cache_entries (
          key TEXT PRIMARY KEY NOT NULL,
          payload TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS write_queue (
          id TEXT PRIMARY KEY NOT NULL,
          type TEXT NOT NULL,
          payload TEXT NOT NULL,
          created_at TEXT NOT NULL,
          attempts INTEGER NOT NULL DEFAULT 0,
          last_error TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_write_queue_created_at
          ON write_queue(created_at);
      `);
      return db;
    });
  }
  return dbPromise;
}

export async function setCache(key, value, updatedAt = nowIso()) {
  const db = await getDb();
  await db.runAsync(
    "INSERT OR REPLACE INTO cache_entries (key, payload, updated_at) VALUES (?, ?, ?)",
    [key, JSON.stringify(value ?? null), updatedAt],
  );
  return { key, value, updatedAt };
}

export async function getCache(key) {
  const db = await getDb();
  const row = await db.getFirstAsync(
    "SELECT payload, updated_at AS updatedAt FROM cache_entries WHERE key = ?",
    [key],
  );
  if (!row) {
    return { value: null, updatedAt: null };
  }
  try {
    return { value: JSON.parse(row.payload), updatedAt: row.updatedAt };
  } catch {
    return { value: null, updatedAt: row.updatedAt };
  }
}

export async function clearCache(key) {
  const db = await getDb();
  await db.runAsync("DELETE FROM cache_entries WHERE key = ?", [key]);
}

export async function clearAllCache() {
  const db = await getDb();
  await db.runAsync("DELETE FROM cache_entries");
}

export const getCalendarCache = () => getCache(cacheTypes.calendar);
export const setCalendarCache = (value) => setCache(cacheTypes.calendar, value);
export const clearCalendarCache = () => clearCache(cacheTypes.calendar);

export const getTasksCache = () => getCache(cacheTypes.tasks);
export const setTasksCache = (value) => setCache(cacheTypes.tasks, value);
export const clearTasksCache = () => clearCache(cacheTypes.tasks);

export const getInboxCache = () => getCache(cacheTypes.unifiedMailInbox);
export const setInboxCache = (value) => setCache(cacheTypes.unifiedMailInbox, value);
export const clearInboxCache = () => clearCache(cacheTypes.unifiedMailInbox);

export const getContactsCache = () => getCache(cacheTypes.contacts);
export const setContactsCache = (value) => setCache(cacheTypes.contacts, value);
export const clearContactsCache = () => clearCache(cacheTypes.contacts);

export const getLearningCache = () => getCache(cacheTypes.learning);
export const setLearningCache = (value) => setCache(cacheTypes.learning, value);
export const clearLearningCache = () => clearCache(cacheTypes.learning);

export async function enqueueWrite(type, payload) {
  const db = await getDb();
  const id = `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  const createdAt = nowIso();
  await db.runAsync(
    "INSERT INTO write_queue (id, type, payload, created_at) VALUES (?, ?, ?, ?)",
    [id, type, JSON.stringify(payload ?? {}), createdAt],
  );
  return { id, type, payload, createdAt };
}

export async function getQueuedWrites() {
  const db = await getDb();
  const rows = await db.getAllAsync(
    "SELECT id, type, payload, created_at AS createdAt, attempts, last_error AS lastError FROM write_queue ORDER BY created_at ASC",
  );
  return rows.map((row) => {
    let payload = {};
    try {
      payload = JSON.parse(row.payload || "{}");
    } catch {
      payload = {};
    }
    return { ...row, payload };
  });
}

export async function removeQueuedWrite(id) {
  const db = await getDb();
  await db.runAsync("DELETE FROM write_queue WHERE id = ?", [id]);
}

export async function markQueuedWriteFailed(id, error) {
  const db = await getDb();
  await db.runAsync(
    "UPDATE write_queue SET attempts = attempts + 1, last_error = ? WHERE id = ?",
    [String(error?.message || error || "Unbekannter Fehler"), id],
  );
}

export async function getQueueSize() {
  const db = await getDb();
  const row = await db.getFirstAsync("SELECT COUNT(*) AS count FROM write_queue");
  return Number(row?.count || 0);
}
