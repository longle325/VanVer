import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.vanver.app",
  appName: "Vanver",
  webDir: "dist",
  server: {
    // Allow all navigation so BrowserRouter-style paths work if needed
    allowNavigation: ["*"],
    // In dev, point to the Vite dev server for live reload:
    // url: "http://192.168.x.x:5173",
    // cleartext: true,
  },
  plugins: {
    SplashScreen: {
      launchAutoHide: true,
      launchShowDuration: 1500,
      backgroundColor: "#efe1bd", // parchment surface
      showSpinner: false,
    },
    StatusBar: {
      style: "DARK",
      backgroundColor: "#efe1bd",
    },
  },
};

export default config;
