# html2md — Frontend

Vue 3 + Vite single-page application that extracts raw content from any URL, converts it to Markdown, and lets you download the result. Styled with a GitHub-flavored dark/light theme.

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Node.js | ≥ 20 |
| npm | ≥ 10 |
| FastAPI back-end | running on `http://localhost:8000` |

---

## Getting started

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Configure environment

Copy the example env file and (optionally) adjust the API base URL:

```bash
cp .env.example .env
```

`.env` default:

```
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start the development server

```bash
npm run dev
```

The app will be available at **http://localhost:5173**.

The dev server automatically proxies requests to `/api/*` → `http://localhost:8000`, so the FastAPI back-end must be running alongside it.

---

## Available scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start the Vite dev server with hot-module replacement |
| `npm run build` | Production build — outputs to `dist/` |
| `npm run preview` | Serve the production build locally for final checks |

---

## Project structure

```
frontend/
├── src/
│   ├── assets/
│   │   ├── themes.css          # GitHub Light / Dark CSS token variables + global base styles
│   │   └── tailwind.css        # Tailwind @base / @components / @utilities entry
│   ├── composables/
│   │   ├── useTheme.js         # Dark/light mode toggle (persists to localStorage)
│   │   └── useApi.js           # Axios wrapper → POST /extract, POST /convert
│   ├── components/
│   │   ├── AppHeader.vue       # Sticky header with logo and theme toggle button
│   │   ├── UrlInput.vue        # URL field with inline validation and Extract button
│   │   ├── ContentPanel.vue    # Scrollable code panel (raw HTML or Markdown)
│   │   ├── ActionBar.vue       # Convert and Download buttons
│   │   └── LoadingSpinner.vue  # SVG spinner (reduced-motion safe)
│   ├── App.vue                 # Root single-page layout and state orchestration
│   └── main.js                 # App entry point
├── .env.example                # Environment variable template
├── tailwind.config.js          # darkMode: 'class', GitHub color tokens, custom fonts
├── vite.config.js              # Vite config with /api dev proxy
└── index.html                  # HTML shell with theme-color meta tag
```

---

## Theme system

Two themes are supported — **GitHub Light** (default) and **GitHub Dark** — toggled by the button in the header. The selected theme persists in `localStorage`.

Theme switching works by toggling the `.dark` class on `<html>`. All colours are defined as CSS custom properties in `src/assets/themes.css` and referenced by Tailwind via `tailwind.config.js`.

| Token | Light | Dark |
|-------|-------|------|
| `--color-canvas-default` | `#ffffff` | `#0d1117` |
| `--color-canvas-subtle` | `#f6f8fa` | `#161b22` |
| `--color-border-default` | `#d0d7de` | `#30363d` |
| `--color-fg-default` | `#24292f` | `#e6edf3` |
| `--color-fg-muted` | `#57606a` | `#8b949e` |
| `--color-accent-fg` | `#0969da` | `#58a6ff` |

---

## API expectations

| Endpoint | Method | Request body | Success response |
|----------|--------|-------------|-----------------|
| `/extract` | POST | `{ "url": "https://..." }` | `{ "html": "..." }` |
| `/convert` | POST | `{ "html": "..." }` | `{ "markdown": "..." }` |

See the [back-end implementation plan](../plan/feature-backend-fastapi-1.md) for full API details.

---

## Production build

```bash
npm run build
```

Output goes to `frontend/dist/`. Serve the static files from any web server or CDN. Point the server to use the FastAPI back-end URL via the `VITE_API_BASE_URL` environment variable at build time:

```bash
VITE_API_BASE_URL=https://your-api.example.com npm run build
```
