import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        term: {
          bg: "#0a0e12",
          panel: "#10161d",
          border: "#1e2a36",
          amber: "#ffb000",
          green: "#2ee06f",
          red: "#ff4d4d",
          blue: "#4db8ff",
          dim: "#6b7d8f",
          text: "#c8d6e5",
        },
      },
      fontFamily: {
        mono: ["Consolas", "Menlo", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
