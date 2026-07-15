const { app, BrowserWindow, net: electronNet, protocol } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const nodeNet = require("net");
const { pathToFileURL } = require("url");

protocol.registerSchemesAsPrivileged([
  {
    scheme: "friday",
    privileges: { standard: true, secure: true, supportFetchAPI: true },
  },
]);

let apiProcess = null;
const apiPort = process.env.FRIDAY_API_PORT || "8000";
const apiHost = process.env.FRIDAY_API_HOST || "127.0.0.1";
const apiClientHost = process.env.FRIDAY_API_CLIENT_HOST || "127.0.0.1";
const skipEmbeddedApi = [
  "1",
  "true",
  "yes",
  "y",
].includes(String(process.env.FRIDAY_SKIP_EMBEDDED_API || "").toLowerCase()) || app.isPackaged;

function isApiPortReachable() {
  const maxAttempts = 12;
  const delayMs = 700;

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  return (async () => {
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      const reachable = await new Promise((resolve) => {
        const socket = nodeNet.createConnection(
          { host: apiClientHost, port: Number(apiPort), timeout: 500 },
          () => {
            socket.end();
            resolve(true);
          },
        );

        socket.on("error", () => {
          resolve(false);
        });
        socket.on("timeout", () => {
          socket.destroy();
          resolve(false);
        });
      });

      if (reachable) {
        return true;
      }

      if (attempt < maxAttempts) {
        await wait(delayMs);
      }
    }

    return false;
  })();
}

function stopApiServer() {
  if (!apiProcess || apiProcess.killed) {
    return;
  }
  apiProcess.removeAllListeners();
  apiProcess.kill();
  apiProcess = null;
}

function startApiServer() {
  if (skipEmbeddedApi) {
    console.log("[Friday API] Embedded API startup is skipped by FRIDAY_SKIP_EMBEDDED_API.");
    return;
  }
  if (apiProcess) {
    return;
  }

  isApiPortReachable().then((reachable) => {
    if (reachable) {
      console.log(`[Friday API] API already available at ${apiClientHost}:${apiPort}; skipping embedded start.`);
      return;
    }

    const pythonBin = process.env.FRIDAY_PYTHON || "python";
    const apiDir = path.join(__dirname, "..", "friday-api");
    const rootDir = path.join(__dirname, "..");

    apiProcess = spawn(
      pythonBin,
      ["-m", "uvicorn", "main:app", "--host", apiHost, "--port", apiPort],
      {
        cwd: apiDir,
        env: {
          ...process.env,
          PYTHONPATH: rootDir,
        },
        stdio: ["ignore", "pipe", "pipe"],
      },
    );

    apiProcess.stdout.on("data", (chunk) => {
      console.log(`[Friday API] ${chunk.toString().trim()}`);
    });
    apiProcess.stderr.on("data", (chunk) => {
      console.error(`[Friday API] ${chunk.toString().trim()}`);
    });
    apiProcess.on("exit", (code) => {
      console.log(`[Friday API] exited with code ${code}`);
      apiProcess = null;
    });
  });
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1180,
    height: 760,
    backgroundColor: "#f6f1e4",
    title: "Friday",
    icon: path.join(__dirname, "assets", "icon.png"),
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  mainWindow.webContents.setWindowOpenHandler(() => ({ action: "deny" }));
  mainWindow.webContents.on("will-navigate", (event, targetUrl) => {
    if (!targetUrl.startsWith("friday://app/")) {
      event.preventDefault();
    }
  });
  mainWindow.webContents.session.setPermissionRequestHandler(
    (_webContents, _permission, callback) => callback(false),
  );

  const query = new URLSearchParams({ apiHost: apiClientHost, apiPort });
  mainWindow.loadURL(`friday://app/index.html?${query.toString()}`);
}

app.whenReady().then(() => {
  protocol.handle("friday", (request) => {
    const requestUrl = new URL(request.url);
    if (requestUrl.hostname !== "app" || requestUrl.pathname !== "/index.html") {
      return new Response("Not found", { status: 404 });
    }
    return electronNet.fetch(pathToFileURL(path.join(__dirname, "index.html")).toString());
  });
  startApiServer();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("before-quit", () => {
  stopApiServer();
});
app.on("will-quit", () => {
  stopApiServer();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
