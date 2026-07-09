const { app, BrowserWindow } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const net = require("net");

let apiProcess = null;
const apiPort = process.env.FRIDAY_API_PORT || "8000";
const apiHost = process.env.FRIDAY_API_HOST || "0.0.0.0";
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
        const socket = net.createConnection(
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
      ["-m", "uvicorn", "main:app", "--host", apiHost, "--port", apiPort, "--reload"],
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
    },
  });

  mainWindow.loadFile(path.join(__dirname, "index.html"), {
    query: {
      apiHost: apiClientHost,
      apiPort,
    },
  });
}

app.whenReady().then(() => {
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
