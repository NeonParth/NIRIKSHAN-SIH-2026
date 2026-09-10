/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          900: "#0b1f3a",
          800: "#143156",
          700: "#1b4b7a",
        },
      },
    },
  },
  plugins: [],
};
