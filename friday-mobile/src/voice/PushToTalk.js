// Push-to-talk voice control for Friday.
//
// Hold the button to record, release to send. The server transcribes
// (faster-whisper), routes the command to the agents and answers with a
// spoken reply (Orpheus German / Kokoro English), which plays back here.
// All native modules load dynamically so builds without them keep working.
import React, { useEffect, useRef, useState } from "react";
import { ActivityIndicator, Text, TouchableOpacity, View } from "react-native";

import { sendVoiceCommandAudio } from "../api/client";
import { t } from "../i18n";
import { loadAudioModule, playBase64Wav } from "./audio";

export default function PushToTalk({ colors }) {
  const [phase, setPhase] = useState("idle"); // idle | recording | sending | speaking | error
  const [transcript, setTranscript] = useState("");
  const [reply, setReply] = useState("");
  const [errorText, setErrorText] = useState("");
  const recordingRef = useRef(null);

  useEffect(() => {
    return () => {
      recordingRef.current?.stopAndUnloadAsync().catch(() => null);
    };
  }, []);

  const startRecording = async () => {
    setErrorText("");
    const Audio = await loadAudioModule();
    if (!Audio) {
      setErrorText(t("voice.noAudioModule"));
      setPhase("error");
      return;
    }
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (!permission.granted) {
        setErrorText(t("voice.noPermission"));
        setPhase("error");
        return;
      }
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY,
      );
      recordingRef.current = recording;
      setPhase("recording");
    } catch (error) {
      setErrorText(String(error?.message || error));
      setPhase("error");
    }
  };

  const stopAndSend = async () => {
    const recording = recordingRef.current;
    recordingRef.current = null;
    if (!recording) {
      setPhase("idle");
      return;
    }
    setPhase("sending");
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      if (!uri) {
        throw new Error(t("voice.noRecording"));
      }
      const result = await sendVoiceCommandAudio(uri, true);
      setTranscript(result?.transcription?.text || "");
      setReply(result?.reply_text || "");

      if (result?.audio_base64) {
        setPhase("speaking");
        await playBase64Wav(result.audio_base64);
      }
      setPhase("idle");
    } catch (error) {
      setErrorText(String(error?.message || error));
      setPhase("error");
    }
  };

  const busy = phase === "sending";
  const recording = phase === "recording";
  const statusText =
    phase === "recording"
      ? t("voice.listening")
      : phase === "sending"
        ? t("voice.thinking")
        : phase === "speaking"
          ? t("voice.speaking")
          : phase === "error"
            ? errorText
            : t("voice.hold");

  return (
    <View
      style={{
        paddingHorizontal: 16,
        paddingVertical: 10,
        gap: 6,
      }}
    >
      {(transcript || reply) && phase !== "recording" && (
        <View
          style={{
            backgroundColor: colors.surface,
            borderRadius: 14,
            padding: 12,
            gap: 4,
          }}
        >
          {transcript ? (
            <Text style={{ color: colors.muted, fontSize: 13 }}>„{transcript}“</Text>
          ) : null}
          {reply ? (
            <Text style={{ color: colors.text, fontSize: 14 }}>{reply}</Text>
          ) : null}
        </View>
      )}
      <TouchableOpacity
        onPressIn={startRecording}
        onPressOut={stopAndSend}
        disabled={busy}
        activeOpacity={0.8}
        style={{
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
          borderRadius: 999,
          paddingVertical: 14,
          backgroundColor: recording ? colors.accentStrong : colors.surface,
        }}
      >
        {busy ? (
          <ActivityIndicator color={colors.accentStrong} />
        ) : (
          <Text style={{ fontSize: 18 }}>{recording ? "🔴" : "🎙️"}</Text>
        )}
        <Text
          style={{
            color: recording ? colors.surface : colors.text,
            fontWeight: "700",
            fontSize: 14,
          }}
        >
          {statusText}
        </Text>
      </TouchableOpacity>
    </View>
  );
}
