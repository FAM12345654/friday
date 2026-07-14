import * as SQLite from "expo-sqlite";

const DB_NAME = "friday_morning_routine.db";
const STATE_ID = 1;

let dbPromise = null;

async function getDb() {
  if (!dbPromise) {
    dbPromise = SQLite.openDatabaseAsync(DB_NAME).then(async (db) => {
      await db.execAsync(`
        PRAGMA journal_mode = WAL;
        CREATE TABLE IF NOT EXISTS morning_routine_state (
          id INTEGER PRIMARY KEY NOT NULL CHECK (id = 1),
          automation_status TEXT NOT NULL DEFAULT 'active',
          skip_date TEXT,
          briefing_date TEXT,
          local_uri TEXT,
          downloaded_at TEXT,
          played_date TEXT,
          last_check_at TEXT,
          alarm_notification_id TEXT,
          alarm_date TEXT,
          alarm_time TEXT,
          alarm_reason TEXT,
          last_error TEXT
        );
        INSERT OR IGNORE INTO morning_routine_state (id, automation_status)
        VALUES (1, 'active');
      `);
      return db;
    });
  }
  return dbPromise;
}

export async function getMorningRoutineState() {
  const db = await getDb();
  return db.getFirstAsync(
    `SELECT automation_status, skip_date, briefing_date, local_uri,
            downloaded_at, played_date, last_check_at,
            alarm_notification_id, alarm_date, alarm_time,
            alarm_reason, last_error
       FROM morning_routine_state WHERE id = ?`,
    [STATE_ID],
  );
}

const ALLOWED_FIELDS = new Set([
  "automation_status",
  "skip_date",
  "briefing_date",
  "local_uri",
  "downloaded_at",
  "played_date",
  "last_check_at",
  "alarm_notification_id",
  "alarm_date",
  "alarm_time",
  "alarm_reason",
  "last_error",
]);

export async function updateMorningRoutineState(values) {
  const entries = Object.entries(values || {}).filter(([key]) => ALLOWED_FIELDS.has(key));
  if (!entries.length) {
    return getMorningRoutineState();
  }
  const db = await getDb();
  const assignments = entries.map(([key]) => `${key} = ?`).join(", ");
  await db.runAsync(
    `UPDATE morning_routine_state SET ${assignments} WHERE id = ?`,
    [...entries.map(([, value]) => value ?? null), STATE_ID],
  );
  return getMorningRoutineState();
}
