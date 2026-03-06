/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        baton: {
          DEFAULT: "#f59e0b",
          dim: "rgba(245, 158, 11, 0.15)",
        },
        energy: {
          DEFAULT: "#06b6d4",
          dim: "rgba(6, 182, 212, 0.15)",
        },
        surface: {
          0: "#09090b",
          1: "#18181b",
          2: "#27272a",
        },
      },
      keyframes: {
        glow: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        "pulse-ring": {
          "0%": { transform: "scale(0.8)", opacity: "1" },
          "100%": { transform: "scale(2)", opacity: "0" },
        },
        "slide-in": {
          "0%": { transform: "translateX(100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        "snap-in": {
          "0%": { transform: "scale(1.05)", opacity: "0.8" },
          "50%": { transform: "scale(0.98)" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
      },
      animation: {
        glow: "glow 2.4s ease-in-out infinite",
        "pulse-ring": "pulse-ring 1s cubic-bezier(0.4, 0, 0.6, 1) forwards",
        "slide-in": "slide-in 0.2s ease-out",
        "snap-in": "snap-in 0.3s ease-out",
      },
    },
  },
  plugins: [],
};
