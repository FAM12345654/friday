// Live updates from the server's SSE channel (/api/events).
//
// The API publishes a "change" event whenever server data changes
// (dashboard, mail, calendar); subscribers refetch through the normal
// cached endpoints instead of polling. react-native-sse is pure JS, so
// this works in existing builds via OTA update. Connection failures are
// silent — the app simply falls back to its usual refresh behavior.
import EventSource from "react-native-sse";

import { getApiUrl } from "../api/client";

export function subscribeLiveEvents(onChange) {
  let source = null;
  try {
    source = new EventSource(`${getApiUrl()}/api/events`, {
      // Keep retrying quietly; the server sends keepalives every 15s.
      pollingInterval: 15000,
    });
    source.addEventListener("change", (event) => {
      let payload = null;
      try {
        payload = JSON.parse(event.data);
      } catch (error) {
        payload = null;
      }
      onChange(payload);
    });
    source.addEventListener("error", () => {
      // Offline or server restart: the library reconnects on its own.
    });
  } catch (error) {
    return () => {};
  }

  return () => {
    try {
      source.removeAllEventListeners();
      source.close();
    } catch (error) {
      // already closed
    }
  };
}
