"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");

const projectRoot = path.resolve(__dirname, "..");
const localDataDir = path.join(projectRoot, "local_data", "whatsapp");
const tokenPath = path.join(localDataDir, "bridge_token.txt");
const configPath = path.join(localDataDir, "bridge.config.json");
const apiUrl = process.env.FRIDAY_API_URL || "http://127.0.0.1:8000";
const pairingPhoneNumber = (
  process.env.FRIDAY_WHATSAPP_PAIRING_PHONE ||
  process.env.WHATSAPP_PAIRING_PHONE ||
  ""
).trim();

process.env.PUPPETEER_CACHE_DIR = path.join(localDataDir, "puppeteer-cache");

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function ensureBridgeToken() {
  ensureDir(localDataDir);
  if (fs.existsSync(tokenPath)) {
    return fs.readFileSync(tokenPath, "utf8").trim();
  }
  const token = crypto.randomBytes(32).toString("base64url");
  fs.writeFileSync(tokenPath, token, "utf8");
  return token;
}

function loadBridgeConfig() {
  if (!fs.existsSync(configPath)) {
    return {
      ignoreGroups: true,
      allowChats: [],
      blockChats: []
    };
  }
  try {
    const parsed = JSON.parse(fs.readFileSync(configPath, "utf8"));
    return {
      ignoreGroups: parsed.ignoreGroups !== false,
      allowChats: Array.isArray(parsed.allowChats) ? parsed.allowChats : [],
      blockChats: Array.isArray(parsed.blockChats) ? parsed.blockChats : []
    };
  } catch (_error) {
    return {
      ignoreGroups: true,
      allowChats: [],
      blockChats: []
    };
  }
}

function shouldMirrorChat(chatId, isGroup, bridgeConfig) {
  if (isGroup && bridgeConfig.ignoreGroups) {
    return false;
  }
  if (bridgeConfig.blockChats.includes(chatId)) {
    return false;
  }
  if (bridgeConfig.allowChats.length > 0 && !bridgeConfig.allowChats.includes(chatId)) {
    return false;
  }
  return true;
}

function maskPhoneNumber(phoneNumber) {
  return phoneNumber.replace(/\d(?=\d{4})/g, "*");
}

async function postMessageToFriday(payload, token) {
  const response = await fetch(`${apiUrl}/api/whatsapp/ingest`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Friday-WhatsApp-Bridge-Token": token
    },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(`Friday API rejected mirror event with HTTP ${response.status}`);
  }
  return response.json();
}

async function main() {
  ensureDir(localDataDir);
  const token = ensureBridgeToken();
  const bridgeConfig = loadBridgeConfig();

  console.log("Friday WhatsApp Read-Bridge startet.");
  console.log("Modus: nur eingehende Nachrichten lesen. Kein automatischer Versand.");
  console.log(`API: ${apiUrl}`);
  if (pairingPhoneNumber) {
    if (!/^\d+$/.test(pairingPhoneNumber)) {
      throw new Error("FRIDAY_WHATSAPP_PAIRING_PHONE muss im internationalen Format nur aus Ziffern bestehen.");
    }
    console.log(`Pairing-Code Login aktiv fuer Nummer ${maskPhoneNumber(pairingPhoneNumber)}.`);
  }

  const clientOptions = {
    authStrategy: new LocalAuth({
      clientId: "friday-read-bridge",
      dataPath: path.join(localDataDir, "session")
    }),
    puppeteer: {
      headless: true
    }
  };

  const client = new Client(clientOptions);
  let pairingRequested = false;

  function requestPairingCodeAfterAuthFlow() {
    if (!pairingPhoneNumber || pairingRequested) {
      return;
    }
    pairingRequested = true;
    console.log("WhatsApp Web Auth-Flow geladen. Pairing-Code wird in 5 Sekunden angefordert.");
    setTimeout(async () => {
      try {
        await client.requestPairingCode(pairingPhoneNumber, true, 180000);
      } catch (error) {
        console.log(`WhatsApp Pairing-Code konnte nicht angefordert werden: ${error.message}`);
        pairingRequested = false;
      }
    }, 5000);
  }

  client.on("code", (code) => {
    console.log("WhatsApp Pairing-Code:");
    console.log(code);
    console.log("WhatsApp -> Verknuepfte Geraete -> Mit Telefonnummer verknuepfen -> Code eingeben");
  });

  client.on("qr", (qr) => {
    if (pairingPhoneNumber) {
      requestPairingCodeAfterAuthFlow();
      return;
    }
    console.log("QR-Code fuer lokalen WhatsApp-Web-Login:");
    qrcode.generate(qr, { small: true });
  });

  client.on("ready", () => {
    console.log("WhatsApp Read-Bridge ist bereit.");
  });

  client.on("disconnected", (reason) => {
    console.log(`WhatsApp Read-Bridge getrennt: ${reason || "unbekannt"}`);
  });

  client.on("message", async (message) => {
    try {
      if (message.fromMe) {
        return;
      }

      const chat = await message.getChat();
      if (!shouldMirrorChat(chat.id._serialized, chat.isGroup, bridgeConfig)) {
        return;
      }

      const contact = await message.getContact();
      await postMessageToFriday(
        {
          chat_id: chat.id._serialized,
          sender_name: contact.pushname || contact.name || "WhatsApp",
          sender_number: contact.id ? contact.id._serialized : "",
          body: message.body || "",
          received_at: new Date((message.timestamp || Date.now() / 1000) * 1000).toISOString()
        },
        token
      );
      console.log("Eingehende WhatsApp-Nachricht lokal gespiegelt.");
    } catch (error) {
      console.log(`WhatsApp Read-Bridge konnte ein Ereignis nicht spiegeln: ${error.message}`);
    }
  });

  process.on("SIGINT", async () => {
    console.log("WhatsApp Read-Bridge wird beendet.");
    await client.destroy();
    process.exit(0);
  });

  await client.initialize();
}

main().catch((error) => {
  console.log(`WhatsApp Read-Bridge konnte nicht starten: ${error.message}`);
  process.exit(1);
});
