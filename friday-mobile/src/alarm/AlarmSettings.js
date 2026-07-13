// Alarm settings row for the "Mehr" screen: time input + on/off toggle.
// Scheduling goes through Notifee (see alarm.js); the spoken briefing plays
// when the alarm fires.
import React, { useEffect, useState } from "react";
import { Text, TextInput, TouchableOpacity, View } from "react-native";

import { t } from "../i18n";
import { cancelDailyAlarm, parseAlarmTime, playMorningBriefing, scheduleDailyAlarm } from "./alarm";
import { getAlarmSettings, saveAlarmSettings } from "./alarmStore";

export default function AlarmSettings({ colors, styles }) {
  const [settings, setSettings] = useState({ enabled: false, time: "07:00" });
  const [timeInput, setTimeInput] = useState("07:00");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getAlarmSettings()
      .then((loaded) => {
        setSettings(loaded);
        setTimeInput(loaded.time);
      })
      .catch(() => null);
  }, []);

  const applyAlarm = async (enabled, time) => {
    setBusy(true);
    setStatus("");
    try {
      const parsed = parseAlarmTime(time);
      if (!parsed) {
        setStatus(t("alarm.timeInvalid"));
        return;
      }
      if (enabled) {
        const result = await scheduleDailyAlarm(parsed.hour, parsed.minute);
        if (!result.ok) {
          setStatus(result.reason || t("alarm.failed"));
          return;
        }
        setStatus(`${t("alarm.scheduled")} ${time}`);
      } else {
        await cancelDailyAlarm();
        setStatus(t("alarm.disabled"));
      }
      const saved = await saveAlarmSettings({ enabled, time });
      setSettings(saved);
    } catch (error) {
      setStatus(String(error?.message || error));
    } finally {
      setBusy(false);
    }
  };

  const testBriefing = async () => {
    setBusy(true);
    setStatus(t("alarm.testing"));
    try {
      const data = await playMorningBriefing();
      setStatus(data?.tts_error ? `${t("alarm.textOnly")}: ${data.text}` : "");
    } catch (error) {
      setStatus(String(error?.message || error));
    } finally {
      setBusy(false);
    }
  };

  return (
    <View style={[styles.moreItem, { flexDirection: "column", alignItems: "stretch", gap: 8 }]}>
      <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
        <View style={{ flex: 1 }}>
          <Text style={styles.cardTitle}>{t("alarm.title")}</Text>
          <Text style={styles.cardMeta}>{t("alarm.hint")}</Text>
        </View>
        <TouchableOpacity
          onPress={() => applyAlarm(!settings.enabled, timeInput)}
          disabled={busy}
          activeOpacity={0.75}
          style={{
            paddingHorizontal: 14,
            paddingVertical: 8,
            borderRadius: 999,
            backgroundColor: settings.enabled ? colors.accentStrong : colors.surface,
          }}
        >
          <Text
            style={[
              styles.cardMeta,
              settings.enabled && { color: colors.surface, fontWeight: "700" },
            ]}
          >
            {settings.enabled ? t("alarm.on") : t("alarm.off")}
          </Text>
        </TouchableOpacity>
      </View>
      <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
        <TextInput
          value={timeInput}
          onChangeText={setTimeInput}
          onEndEditing={() => settings.enabled && applyAlarm(true, timeInput)}
          placeholder="07:00"
          placeholderTextColor={colors.muted}
          keyboardType="numbers-and-punctuation"
          maxLength={5}
          style={{
            borderRadius: 10,
            paddingHorizontal: 12,
            paddingVertical: 8,
            backgroundColor: colors.surface,
            color: colors.text,
            fontSize: 16,
            fontWeight: "700",
            minWidth: 80,
            textAlign: "center",
          }}
        />
        <TouchableOpacity onPress={testBriefing} disabled={busy} activeOpacity={0.75}>
          <Text style={[styles.cardMeta, { textDecorationLine: "underline" }]}>
            {t("alarm.test")}
          </Text>
        </TouchableOpacity>
      </View>
      {status ? <Text style={styles.cardMeta}>{status}</Text> : null}
    </View>
  );
}
