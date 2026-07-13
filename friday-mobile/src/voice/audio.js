// Shared audio helpers for the voice module.
//
// Native modules load dynamically so builds without them keep working
// (the caller gets null / a rejected promise instead of a crash).

export async function loadAudioModule() {
  try {
    const module = await import("expo-av");
    return module.Audio;
  } catch (error) {
    return null;
  }
}

async function writeWavFile(base64, filename) {
  const FileSystem = await import("expo-file-system/legacy");
  const target = `${FileSystem.cacheDirectory}${filename}`;
  await FileSystem.writeAsStringAsync(target, base64, {
    encoding: FileSystem.EncodingType.Base64,
  });
  return target;
}

// Plays one base64 WAV and resolves when playback finishes.
// Returns false when no audio module is available.
export async function playBase64Wav(base64, filename = "friday-reply.wav") {
  const Audio = await loadAudioModule();
  if (!Audio || !base64) {
    return false;
  }
  await Audio.setAudioModeAsync({
    allowsRecordingIOS: false,
    playsInSilentModeIOS: true,
  });
  const fileUri = await writeWavFile(base64, filename);
  const { sound } = await Audio.Sound.createAsync({ uri: fileUri });
  await new Promise((resolve) => {
    sound.setOnPlaybackStatusUpdate((status) => {
      if (status?.didJustFinish || status?.error) {
        resolve();
      }
    });
    sound.playAsync().catch(() => resolve());
  });
  await sound.unloadAsync().catch(() => null);
  return true;
}
