/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{vue,js}',
  ],
  theme: {
    extend: {
      colors: {
        canvas: 'var(--color-canvas-default)',
        'canvas-subtle': 'var(--color-canvas-subtle)',
        'border-default': 'var(--color-border-default)',
        'fg-default': 'var(--color-fg-default)',
        'fg-muted': 'var(--color-fg-muted)',
        'accent-fg': 'var(--color-accent-fg)',
        'accent-em': 'var(--color-accent-emphasis)',
        'btn-bg': 'var(--color-btn-bg)',
        'btn-border': 'var(--color-btn-border)',
        'btn-hover': 'var(--color-btn-hover-bg)',
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', '"Courier New"', 'monospace'],
        ui: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}

