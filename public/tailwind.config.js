import presetQuick from "franken-ui/shadcn-ui/preset-quick"

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../templates/**/*.*'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  presets: [presetQuick()]
}
