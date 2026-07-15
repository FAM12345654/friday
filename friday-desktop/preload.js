const { contextBridge } = require("electron");

// Keep the API credential out of URLs and renderer source. The local renderer
// can request it only through this narrow, read-only bridge.
contextBridge.exposeInMainWorld("fridayRuntime", {
  apiToken: String(process.env.FRIDAY_API_TOKEN || ""),
});
