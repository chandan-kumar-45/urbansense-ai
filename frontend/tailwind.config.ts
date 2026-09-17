import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0A0E17",
        panel: "#111826",
        card: "#1A2436",
        border: "#2C3A52",
        ink: "#E4E9F2",
        muted: "#7C8AA5",
        signal: {
          good: "#3ED598",
          medium: "#F2B84B",
          high: "#FF6B5E",
          critical: "#FF3B3B",
          info: "#4FA8F7",
        },
      },
      fontFamily: {
        sans: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"],
      },
      boxShadow: {
        panel: "0 0 0 1px #2C3A52",
      },
    },
  },
  plugins: [],
} satisfies Config;
