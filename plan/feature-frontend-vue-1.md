---
goal: Build the Vue.js 3 front-end for the html-2-md web application
version: 1.0
date_created: 2026-03-20
last_updated: 2026-03-20
owner: html-2-md Team
status: 'Planned'
tags: [feature, frontend, vue, ui-ux]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan describes the complete implementation of the Vue.js 3 front-end for **html-2-md** — a web application that extracts raw content from any URL, converts it to human- and AI-readable Markdown, and lets the user download the result. The UI follows a GitHub-flavored dark/light theme with a programmatic developer-tool aesthetic inspired by [skillsmp.com](https://skillsmp.com/).

---

## 1. Requirements & Constraints

- **REQ-001**: Single-page application built with Vue 3 (Composition API, `<script setup>`) and Vite.
- **REQ-002**: Tailwind CSS for utility-first styling; custom CSS tokens for GitHub color themes.
- **REQ-003**: Two color themes — **GitHub Light** and **GitHub Dark** — toggled by a button in the header. Theme persists via `localStorage`.
- **REQ-004**: Fully responsive layout from 375 px mobile to 1440 px desktop.
- **REQ-005**: Single page with these sections in order: Header → URL input + Extract button → Panel 1 (raw HTML preview) → Convert button → Panel 2 (Markdown preview) → Download button.
- **REQ-006**: Panels are scrollable code-blocks with line numbers; min-height 300 px, max-height 60 vh.
- **REQ-007**: All async operations show a loading spinner and disable the triggering button.
- **REQ-008**: All interactive elements meet WCAG AA contrast (4.5:1) and have visible focus rings.
- **REQ-009**: Touch targets ≥ 44 × 44 px; 8 px+ spacing between interactive elements.
- **REQ-010**: Communicate with the FastAPI back-end via Axios (base URL from `VITE_API_BASE_URL` env variable).
- **SEC-001**: Always validate that the URL field is non-empty and a valid URL format before making API calls; never send raw user input unchecked.
- **SEC-002**: Render Markdown preview as plain text / safe HTML only (use `dompurify` if `v-html` is needed).
- **CON-001**: No SSR or backend rendering — pure SPA served as static files.
- **CON-002**: No routing library needed — single page only.
- **GUD-001**: Use `motion-preference: reduced-motion` safe animations (150–300 ms transitions, `transform`/`opacity` only).
- **GUD-002**: Programmatic font stack: `ui-monospace, SFMono-Regular, Menlo, Consolas, "Courier New", monospace` for code panels; Inter or system-ui for UI text.
- **PAT-001**: Component-per-concern: Header, UrlInput, RawPanel, MarkdownPanel, ActionButtons.

---

## 2. Implementation Steps

### Phase 1 — Project Scaffold

- GOAL-001: Initialise a Vite + Vue 3 project and configure dependencies.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Run `npm create vite@latest frontend -- --template vue` in the workspace root to scaffold the project | | |
| TASK-002 | Install production dependencies: `axios`, `dompurify` | | |
| TASK-003 | Install dev dependencies: `tailwindcss`, `postcss`, `autoprefixer`, `@tailwindcss/typography` | | |
| TASK-004 | Run `npx tailwindcss init -p` to generate `tailwind.config.js` and `postcss.config.js` | | |
| TASK-005 | Configure `tailwind.config.js`: set `darkMode: 'class'`, add `content` globs for `./src/**/*.{vue,js}` | | |
| TASK-006 | Create `frontend/.env.example` with `VITE_API_BASE_URL=http://localhost:8000` | | |
| TASK-007 | Create `frontend/.env` (git-ignored) with the same default value | | |

### Phase 2 — GitHub Color Tokens

- GOAL-002: Define semantic CSS custom properties for GitHub Light and Dark themes.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-008 | Create `src/assets/themes.css` with `:root` (light) and `.dark` (dark) CSS variable blocks matching GitHub's palette: `--color-canvas-default`, `--color-canvas-subtle`, `--color-border-default`, `--color-fg-default`, `--color-fg-muted`, `--color-accent-fg`, `--color-accent-emphasis`, `--color-btn-bg`, `--color-btn-border`, `--color-btn-hover-bg` | | |
| TASK-009 | Import `themes.css` in `src/main.js` | | |
| TASK-010 | Extend `tailwind.config.js` colors to map to the CSS variables (e.g. `canvas: 'var(--color-canvas-default)'`) so Tailwind classes can reference them | | |

**GitHub Light values:**

| Token | Value |
|-------|-------|
| `--color-canvas-default` | `#ffffff` |
| `--color-canvas-subtle` | `#f6f8fa` |
| `--color-border-default` | `#d0d7de` |
| `--color-fg-default` | `#24292f` |
| `--color-fg-muted` | `#57606a` |
| `--color-accent-fg` | `#0969da` |
| `--color-accent-emphasis` | `#0969da` |

**GitHub Dark values:**

| Token | Value |
|-------|-------|
| `--color-canvas-default` | `#0d1117` |
| `--color-canvas-subtle` | `#161b22` |
| `--color-border-default` | `#30363d` |
| `--color-fg-default` | `#e6edf3` |
| `--color-fg-muted` | `#8b949e` |
| `--color-accent-fg` | `#58a6ff` |
| `--color-accent-emphasis` | `#1f6feb` |

### Phase 3 — Composables

- GOAL-003: Create reusable composables for theme management and API calls.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-011 | Create `src/composables/useTheme.js`: reads `localStorage.getItem('theme')`, defaults to `'light'`, toggles `.dark` class on `<html>`, exposes `isDark` (ref) and `toggleTheme()` | | |
| TASK-012 | Create `src/composables/useApi.js`: wraps Axios with `baseURL: import.meta.env.VITE_API_BASE_URL`, exports `extractContent(url)` → POST `/extract` and `convertToMarkdown(html)` → POST `/convert`. Returns `{ data, error, loading }` reactive state. | | |

### Phase 4 — Components

- GOAL-004: Build the five UI components.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-013 | Create `src/components/AppHeader.vue`: shows the app logo/title ("html-2-md"), a subtitle, and the light/dark toggle button (sun/moon SVG icon, `aria-label="Toggle theme"`). Uses `useTheme` composable. | | |
| TASK-014 | Create `src/components/UrlInput.vue`: labelled text input (`type="url"`, `autocomplete="url"`, `placeholder="https://example.com"`), inline validation (show error below on blur if invalid URL), and an "Extract" primary button. Emits `extract(url)`. | | |
| TASK-015 | Create `src/components/ContentPanel.vue`: generic scrollable code panel (prop: `label`, `content`, `language`). Renders content inside a `<pre><code>` block with monospace font, line-wrap, and scrollbar. Shows an empty-state placeholder when `content` is falsy. | | |
| TASK-016 | Create `src/components/ActionBar.vue`: contains "Convert" and "Download" buttons. "Convert" disabled when no raw content; "Download" disabled when no markdown content. Emits `convert` and `download`. Buttons show spinner (`animate-spin`) while loading. | | |
| TASK-017 | Create `src/components/LoadingSpinner.vue`: inline SVG spinner, accepts `size` prop (default `'sm'`). | | |

### Phase 5 — Root App

- GOAL-005: Wire all components into `App.vue`, implement the main page layout.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-018 | Replace default `src/App.vue` with the single-page layout: `AppHeader` at top, then a centred max-w-5xl container with: `UrlInput` → (on `extract` event) call `useApi.extractContent()`, store result in `rawHtml` ref → `ContentPanel` showing `rawHtml` → `ActionBar` → (on `convert` event) call `useApi.convertToMarkdown(rawHtml)`, store result in `markdownText` ref → second `ContentPanel` showing `markdownText` | | |
| TASK-019 | Implement the "Download" handler in `App.vue`: create a Blob from `markdownText` with `text/markdown` MIME type, trigger `<a download="output.md">` click programmatically | | |
| TASK-020 | Apply responsive grid: on mobile the two panels stack vertically; on `lg` breakpoint they sit side-by-side (CSS Grid, `grid-cols-1 lg:grid-cols-2`) with the `ActionBar` spanning full width between the two panels | | |
| TASK-021 | Add global `<meta name="theme-color">` update in `useTheme.js` to match the canvas color for PWA-style browser chrome | | |

### Phase 6 — Styling Polish

- GOAL-006: Apply final visual polish matching the GitHub programmatic developer-tool aesthetic.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-022 | Style all buttons with GitHub pill/rounded style: `rounded-md`, `border`, `font-medium`, accent background for primary, subtle background for secondary. Apply `transition-colors duration-150` on hover | | |
| TASK-023 | Style panels with `border border-[--color-border-default] rounded-md bg-[--color-canvas-subtle]` and inner `overflow-y-auto` | | |
| TASK-024 | Add a sticky header with `backdrop-blur-sm` and `border-b` separator | | |
| TASK-025 | Ensure dark-mode panel text uses `--color-fg-default` (high contrast) and muted labels use `--color-fg-muted` | | |
| TASK-026 | Add `prefers-reduced-motion` safe keyframe for the loading spinner (`@media (prefers-reduced-motion: reduce)`) | | |

### Phase 7 — Build Configuration

- GOAL-007: Finalise build tooling and project configuration.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-027 | Update `package.json` scripts: `"dev": "vite"`, `"build": "vite build"`, `"preview": "vite preview"` | | |
| TASK-028 | Configure Vite `vite.config.js` with `server.proxy` for `/api` → `http://localhost:8000` to avoid CORS during development | | |
| TASK-029 | Add `frontend/` to the root `.gitignore` build output exclusions (`dist/`, `node_modules/`) | | |

---

## 3. Alternatives

- **ALT-001**: Nuxt.js instead of Vite + Vue — rejected; SSR is unnecessary for a simple single-page tool and adds complexity.
- **ALT-002**: shadcn-vue component library — considered; not used to keep the GitHub-specific theming without conflicts from a third-party design system.
- **ALT-003**: CSS Modules instead of Tailwind — rejected; Tailwind with CSS variables gives faster iteration while keeping the custom token system.
- **ALT-004**: Pinia for state management — not needed; the data flow is simple enough for composable refs without a global store.

---

## 4. Dependencies

| ID | Name | Version (min) | Purpose |
|----|------|--------------|---------|
| **DEP-001** | vue | 3.4+ | UI framework |
| **DEP-002** | vite | 5.0+ | Build tool & dev server |
| **DEP-003** | tailwindcss | 3.4+ | Utility-first CSS |
| **DEP-004** | axios | 1.7+ | HTTP client for API calls |
| **DEP-005** | dompurify | 3.1+ | Sanitise HTML before `v-html` rendering |
| **DEP-006** | @tailwindcss/typography | 0.5+ | Prose styling for Markdown preview |

---

## 5. Files

| ID | Path | Description |
|----|------|-------------|
| **FILE-001** | `frontend/` | Vue project root |
| **FILE-002** | `frontend/src/main.js` | App entry point |
| **FILE-003** | `frontend/src/App.vue` | Root single-page component |
| **FILE-004** | `frontend/src/assets/themes.css` | GitHub Light/Dark CSS token definitions |
| **FILE-005** | `frontend/src/composables/useTheme.js` | Dark/light mode toggle composable |
| **FILE-006** | `frontend/src/composables/useApi.js` | Axios-based API composable |
| **FILE-007** | `frontend/src/components/AppHeader.vue` | Header with theme toggle |
| **FILE-008** | `frontend/src/components/UrlInput.vue` | URL input with validation |
| **FILE-009** | `frontend/src/components/ContentPanel.vue` | Scrollable raw/markdown preview panel |
| **FILE-010** | `frontend/src/components/ActionBar.vue` | Convert & Download buttons |
| **FILE-011** | `frontend/src/components/LoadingSpinner.vue` | Reusable spinner |
| **FILE-012** | `frontend/.env.example` | Environment variable template |
| **FILE-013** | `frontend/vite.config.js` | Vite configuration |
| **FILE-014** | `frontend/tailwind.config.js` | Tailwind configuration with dark mode + custom tokens |

---

## 6. Testing

| ID | Description |
|----|-------------|
| **TEST-001** | URL validation: submitting an empty string or invalid URL shows an inline error and does NOT fire the API call |
| **TEST-002** | Theme toggle: clicking the toggle button adds/removes `.dark` class on `<html>` and persists in `localStorage` |
| **TEST-003** | Extract flow: entering a valid URL and clicking Extract shows loading state, then populates Panel 1 with raw HTML |
| **TEST-004** | Convert flow: clicking Convert sends Panel 1 content to API and populates Panel 2 with Markdown |
| **TEST-005** | Download: clicking Download triggers a file download of `output.md` with the correct Markdown content |
| **TEST-006** | Responsive: at 375 px viewport the two panels stack vertically with no horizontal overflow |
| **TEST-007** | Accessibility: all buttons are keyboard-reachable, have visible focus rings, and meet 4.5:1 contrast in both themes |
| **TEST-008** | Empty state: panels show placeholder text when content is empty |

---

## 7. Risks & Assumptions

- **RISK-001**: Some websites block crawler requests (CORS, robots.txt, anti-bot). The UI should surface the error message from the API clearly.
- **RISK-002**: Very large HTML pages may cause Panel 1 to be slow to render. Consider virtualized text display if performance degrades.
- **ASSUMPTION-001**: The FastAPI back-end runs on `http://localhost:8000` during development and is accessible from the browser via the Vite proxy.
- **ASSUMPTION-002**: The user has Node.js ≥ 20 installed.

---

## 8. Related Specifications / Further Reading

- [Back-end Implementation Plan](./feature-backend-fastapi-1.md)
- [Vue 3 Composition API docs](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Tailwind CSS Dark Mode](https://tailwindcss.com/docs/dark-mode)
- [GitHub Primer Color System](https://primer.style/primitives/colors)
