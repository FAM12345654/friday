import assert from "node:assert/strict";
import test from "node:test";

import {
  isBriefingFileName,
  normalizeMorningAutomation,
  promoteDownloadedBriefing,
  shouldAutoPlayMorningBriefing,
  shouldRefreshMorningAlarm,
} from "../src/morning/morningBriefingPolicy.js";

function buildFileSystem(initialFiles = {}) {
  const files = new Map(Object.entries(initialFiles));
  let failMoveFrom = null;
  return {
    files,
    setFailMoveFrom(uri) {
      failMoveFrom = uri;
    },
    async deleteAsync(uri) {
      files.delete(uri);
    },
    async getInfoAsync(uri) {
      return { exists: files.has(uri), size: files.get(uri)?.length || 0 };
    },
    async moveAsync({ from, to }) {
      if (from === failMoveFrom) throw new Error("simulated move failure");
      if (!files.has(from)) throw new Error(`missing source: ${from}`);
      files.set(to, files.get(from));
      files.delete(from);
    },
    async readDirectoryAsync(directory) {
      return [...files.keys()]
        .filter((uri) => uri.startsWith(directory))
        .map((uri) => uri.slice(directory.length))
        .filter((name) => !name.includes("/"));
    },
  };
}

const directory = "file:///briefings/";
const tempUri = `${directory}friday_briefing_download.tmp`;
const backupUri = `${directory}friday_briefing_previous.tmp`;

test("first and second push each leave exactly one briefing file", async () => {
  const fs = buildFileSystem({ [tempUri]: "first-audio" });
  const firstTarget = `${directory}friday_briefing_2026-07-15.mp3`;
  await promoteDownloadedBriefing({ fileSystem: fs, directory, tempUri, targetUri: firstTarget, backupUri });
  assert.deepEqual([...fs.files.keys()].filter((name) => isBriefingFileName(name.split("/").pop())), [firstTarget]);

  fs.files.set(tempUri, "second-audio");
  const secondTarget = `${directory}friday_briefing_2026-07-16.mp3`;
  await promoteDownloadedBriefing({ fileSystem: fs, directory, tempUri, targetUri: secondTarget, backupUri });
  assert.deepEqual([...fs.files.keys()].filter((name) => isBriefingFileName(name.split("/").pop())), [secondTarget]);
  assert.equal(fs.files.get(secondTarget), "second-audio");
});

test("failed promotion preserves the previous briefing", async () => {
  const previous = `${directory}friday_briefing_2026-07-15.mp3`;
  const target = `${directory}friday_briefing_2026-07-16.mp3`;
  const fs = buildFileSystem({ [previous]: "previous-audio", [tempUri]: "broken-download" });
  fs.setFailMoveFrom(tempUri);

  await assert.rejects(
    promoteDownloadedBriefing({ fileSystem: fs, directory, tempUri, targetUri: target, backupUri }),
    /simulated move failure/,
  );
  assert.equal(fs.files.get(previous), "previous-audio");
});

test("alarm polling refreshes after twelve hours or for a new target date", () => {
  const now = Date.parse("2026-07-14T20:00:00Z");
  assert.equal(shouldRefreshMorningAlarm({ lastCheckAt: "2026-07-14T09:59:59Z", alarmDate: "2026-07-15", targetDate: "2026-07-15", now }), false);
  assert.equal(shouldRefreshMorningAlarm({ lastCheckAt: "2026-07-14T07:59:59Z", alarmDate: "2026-07-15", targetDate: "2026-07-15", now }), true);
  assert.equal(shouldRefreshMorningAlarm({ lastCheckAt: "2026-07-14T19:59:59Z", alarmDate: "2026-07-15", targetDate: "2026-07-16", now }), true);
});

test("briefing auto-play is limited to the morning and once per day", () => {
  const base = { today: "2026-07-15", localUri: "file:///briefing.mp3" };
  assert.equal(shouldAutoPlayMorningBriefing({ ...base, hour: 7, playedDate: null }), true);
  assert.equal(shouldAutoPlayMorningBriefing({ ...base, hour: 4, playedDate: null }), false);
  assert.equal(shouldAutoPlayMorningBriefing({ ...base, hour: 10, playedDate: null }), false);
  assert.equal(shouldAutoPlayMorningBriefing({ ...base, hour: 7, playedDate: "2026-07-15" }), false);
});

test("skip once resets after its selected day", () => {
  assert.deepEqual(
    normalizeMorningAutomation({ status: "skip_once", skipDate: "2026-07-15", today: "2026-07-15" }),
    { status: "active", skipDate: null },
  );
  assert.deepEqual(
    normalizeMorningAutomation({ status: "paused", skipDate: null, today: "2026-07-15" }),
    { status: "paused", skipDate: null },
  );
});
