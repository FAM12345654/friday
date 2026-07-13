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

async function loadAudioModule() {
  try {
    const module = await import("expo-av");
    return module.Audio;
  } catch (error) {
    return null;
  }
}

async function writeReplyAudio(base64) {
  const FileSystem = await import("expo-file-system/legacy");
  const target = `${FileSystem.cacheDirectory}friday-reply.wav`;
  await FileSystem.writeAsStringAsync(target, base64, {
    encoding: FileSystem.EncodingType.Base64,
  });
  return target;
}

export default function PushToTalk({ colors }) {
  const [phase, setPhase] = useState("idle"); // idle | recording | sending | speaking | error
  const [transcript, setTranscript] = useState("");
  const [reply, setReply] = useState("");
  const [errorText, setErrorText] = useState("");
  const recordingRef = useRef(null);
  const soundRef = useRef(null);

  useEffect(() => {
    return () => {
      recordingRef.current?.stopAndUnloadAsync().catch(() => null);
      soundRef.current?.unloadAsync().catch(() => null);
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
        const Audio = await loadAudioModule();
        if (Audio) {
          setPhase("speaking");
          await Audio.setAudioModeAsync({
            allowsRecordingIOS: false,
            playsInSilentModeIOS: true,
          });
          const fileUri = await writeReplyAudio(result.audio_base64);
          const { sound } = await Audio.Sound.createAsync({ uri: fileUri });
          soundRef.current = sound;
          sound.setOnPlaybackStatusUpdate((status) => {
            if (status?.didJustFinish) {
              sound.unloadAsync().catch(() => null);
              soundRef.current = null;
              setPhase("idle");
            }
          });
          await sound.playAsync();
          return;
        }
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
