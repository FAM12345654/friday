import {
  archiveTask,
  completeTask,
  createContact,
  createTask,
  deleteTask,
  getApiUrl,
  updateContact,
} from "../api/client";
import {
  cacheTypes,
  enqueueWrite,
  getCache,
  getQueueSize,
  getQueuedWrites,
  markQueuedWriteFailed,
  removeQueuedWrite,
  setCache,
} from "./localStore";

export { cacheTypes };

const syncMetaKey = "__sync_meta";

const nowIso = () => new Date().toISOString();

const queueHandlers = {
  createTask: ({ payload }) => createTask(payload),
  completeTask: ({ taskId }) => completeTask(taskId),
  archiveTask: ({ taskId }) => archiveTask(taskId),
  deleteTask: ({ taskId }) => deleteTask(taskId),
  createContact: ({ payload }) => createContact(payload),
  updateContactNotes: ({ contactId, notes }) => updateContact(contactId, { notes }),
};

export function formatSyncTime(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
}

export async function getSyncStatus() {
  const [{ value: meta }, queueSize] = await Promise.all([getCache(syncMetaKey), getQueueSize()]);
  return {
    online: Boolean(meta?.online),
    lastSyncedAt: meta?.lastSyncedAt || null,
    lastError: meta?.lastError || "",
    queueSize,
    apiUrl: meta?.apiUrl || getApiUrl(),
  };
}

export async function setSyncStatus(patch) {
  const current = await getSyncStatus().catch(() => ({
    online: false,
    lastSyncedAt: null,
    lastError: "",
    queueSize: 0,
    apiUrl: getApiUrl(),
  }));
  const next = {
    ...current,
    ...patch,
    apiUrl: patch?.apiUrl || getApiUrl(),
  };
  await setCache(syncMetaKey, next);
  return next;
}

export async function readCachedEntry(key) {
  return getCache(key);
}

export async function writeCachedEntry(key, value) {
  const result = await setCache(key, value);
  await setSyncStatus({ lastSyncedAt: result.updatedAt, online: true, lastError: "" });
  return result;
}

export async function writeLocalCacheEntry(key, value) {
  return setCache(key, value);
}

export async function readThroughCache(key, fetcher, options = {}) {
  const {
    apply,
    normalize = (value) => value,
    allowNull = false,
    fallback,
  } = options;
  const hasFallback = Object.prototype.hasOwnProperty.call(options, "fallback");
  const cached = await getCache(key);
  const hasCache = cached.updatedAt && (allowNull || cached.value !== null);
  if (hasCache && apply) {
    apply(normalize(cached.value), { source: "cache", updatedAt: cached.updatedAt });
  }

  try {
    const networkValue = await fetcher();
    await setCache(key, networkValue);
    const normalized = normalize(networkValue);
    if (apply) {
      apply(normalized, { source: "network", updatedAt: nowIso() });
    }
    const status = await setSyncStatus({ online: true, lastSyncedAt: nowIso(), lastError: "" });
    return { value: normalized, source: "network", status };
  } catch (error) {
    const status = await setSyncStatus({
      online: false,
      lastError: String(error?.message || error || "Offline"),
    });
    if (hasCache) {
      return {
        value: normalize(cached.value),
        source: "cache",
        updatedAt: cached.updatedAt,
        error,
        status,
      };
    }
    if (hasFallback) {
      const normalizedFallback = normalize(fallback);
      if (apply) {
        apply(normalizedFallback, { source: "fallback", updatedAt: null });
      }
      return {
        value: normalizedFallback,
        source: "fallback",
        updatedAt: null,
        error,
        status,
      };
    }
    throw error;
  }
}

export async function enqueueOfflineWrite(type, payload) {
  const entry = await enqueueWrite(type, payload);
  await setSyncStatus({ online: false });
  return entry;
}

export async function flushWriteQueue() {
  const queued = await getQueuedWrites();
  if (!queued.length) {
    return { flushed: 0, remaining: 0 };
  }

  let flushed = 0;
  for (const entry of queued) {
    const handler = queueHandlers[entry.type];
    if (!handler) {
      await markQueuedWriteFailed(entry.id, `Unbekannter Queue-Typ: ${entry.type}`);
      continue;
    }
    try {
      await handler(entry.payload || {});
      await removeQueuedWrite(entry.id);
      flushed += 1;
    } catch (error) {
      await markQueuedWriteFailed(entry.id, error);
      await setSyncStatus({ online: false, lastError: String(error?.message || error) });
      break;
    }
  }

  const remaining = await getQueueSize();
  if (remaining === 0) {
    await setSyncStatus({ online: true, lastSyncedAt: nowIso(), lastError: "" });
  }
  return { flushed, remaining };
}

export async function syncOnForeground(refresh) {
  const result = await flushWriteQueue();
  if (typeof refresh === "function") {
    await refresh();
  }
  return result;
}
