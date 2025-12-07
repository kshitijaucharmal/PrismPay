/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "brand-green": "#22c55e",
        "brand-dark": "#111111",
        "brand-card": "#1a1a1a",
      },
    },
  },
  plugins: [],
};
