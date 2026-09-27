/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f2fbf7',
          100: '#e1f6ee',
          200: '#c5ecde',
          300: '#99dcc6',
          400: '#64c4a6',
          500: '#3ba987',
          600: '#2b886c',
          700: '#236c57',
          800: '#1e5647',
          900: '#1b473b',
          dark: '#0a2e23',
          darker: '#061d16',
          emerald: '#059669',
          mint: '#10b981',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
