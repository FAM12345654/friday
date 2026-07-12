const { getDefaultConfig } = require("expo/metro-config");

const config = getDefaultConfig(__dirname);

// expo-sqlite auf Web: wa-sqlite.wasm muss als Asset aufgelöst werden,
// SharedArrayBuffer braucht COOP/COEP-Header.
config.resolver.assetExts.push("wasm");

config.server = config.server || {};
const prevEnhance = config.server.enhanceMiddleware;
config.server.enhanceMiddleware = (middleware, server) => {
  const wrapped = prevEnhance ? prevEnhance(middleware, server) : middleware;
  return (req, res, next) => {
    res.setHeader("Cross-Origin-Opener-Policy", "same-origin");
    res.setHeader("Cross-Origin-Embedder-Policy", "require-corp");
    wrapped(req, res, next);
  };
};

module.exports = config;
