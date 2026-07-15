const baseConfig = require("./app.json");

module.exports = ({ config }) => {
  const plugins = config.plugins ?? baseConfig.expo.plugins ?? [];
  const notificationPlugin = "expo-notifications";
  const secureStorePlugin = "expo-secure-store";
  const configuredPluginNames = plugins.map((plugin) =>
    Array.isArray(plugin) ? plugin[0] : plugin,
  );
  const requiredPlugins = [notificationPlugin, secureStorePlugin].filter(
    (plugin) => !configuredPluginNames.includes(plugin),
  );

  return {
    ...config,
    android: {
      ...config.android,
      googleServicesFile:
        process.env.GOOGLE_SERVICES_JSON ?? "./google-services.json",
    },
    plugins: [...plugins, ...requiredPlugins],
  };
};
