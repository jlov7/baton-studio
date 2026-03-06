/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      keyframes: {
        glow: { "0%, 100%": { opacity: "0.6" }, "50%": { opacity: "1" } }
      },
      animation: {
        glow: "glow 2.4s ease-in-out infinite"
      }
    }
  },
  plugins: []
};
