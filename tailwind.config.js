/** @type {import('tailwindcss').Config} */
module.exports = {
  content: {
    // Since the tailwind executable mind be ran from any place (not just
    // the project root), we need the content files to be relative to the
    // location of the config file (and not the CWD).
    relative: true,
    files: [
      'templates/**/*'
    ]
  },
  theme: {
    fontFamily: {
      'opensans': ['Open Sans', 'sans-serif'],
      'roboto-mono': ['Roboto Mono', 'monospace'],
      'ubuntu': ['Ubuntu', 'sans-serif'],
    },
    extend: {
      colors: {
        'darkmode': {
          // 'bg': '#020617',
          'bg': 'black',
          'text': '#cacaca',
          'colored-title': '#91b7ff'
        },
        'lightmode': {
          'colored-title': '#007bd5'
        }
      }
    },
  },
  plugins: [
    function ({ addVariant }) {
      addVariant('supports-hover', '@media (hover: hover)')
    },
  ],
}

