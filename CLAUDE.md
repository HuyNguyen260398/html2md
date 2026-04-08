# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

html-2-md is a web app that fetches a URL's HTML and converts it to clean Markdown. The user flow is: enter URL → extract raw HTML → convert to Markdown → download `.md` file.

## Development commands

### Backend (FastAPI)

```bash
cd backend
uv sync                  # install dependencies
cp .env.example .env     # first-time setup
fastapi dev              # starts at http://localhost:8000
```

Interactive API docs: `http://localhost:8000/docs`

### Frontend (Vue 3 + Vite)

```bash
cd frontend
npm install              # install dependencies
cp .env.example .env     # first-time setup
npm run dev              # starts at http://localhost:5173
npm run build            # production build
npm run test             # run tests with vitest
```

## Architecture

### Backend (`backend/app/`)

- `main.py` — FastAPI app setup: CORS middleware, router registration, global exception handlers
- `config.py` — `Settings` via pydantic-settings; reads from `backend/.env`
- `models.py` — Pydantic request/response models. All API responses use the generic `ApiResponse[T]` wrapper: `{ data: T | null, error: string | null }`
- `exceptions.py` — `ExtractError` and `ConvertError` custom exceptions with `status_code`; caught by handlers in `main.py`
- `routers/extract.py` — `POST /extract`: delegates to `fetcher.fetch_html()`
- `routers/convert.py` — `POST /convert`: delegates to `converter`
- `services/fetcher.py` — SSRF protection (resolves hostname, blocks private IPs), streams response with 10 MB size limit and 10s timeout, returns `(html, title)`
- `services/converter.py` — HTML → Markdown via `html2text`

### Frontend (`frontend/src/`)

- `App.vue` — root component; owns all state (`rawHtml`, `markdownText`) and orchestrates the extract → convert → download flow
- `composables/useApi.js` — axios wrapper; exposes `extractContent(url)` and `convertToMarkdown(html)` with shared `loading`/`error` refs. API base URL comes from `VITE_API_BASE_URL`
- `composables/useTheme.js` — GitHub light/dark theme toggle; persists to localStorage
- `components/` — `AppHeader`, `UrlInput`, `ContentPanel` (displays raw HTML or Markdown), `ActionBar`, `LoadingSpinner`
- `assets/themes.css` — CSS custom properties for GitHub-style theme tokens used throughout via inline `style` attributes

### Error handling convention

Errors bubble up as `ExtractError`/`ConvertError` in the backend and are serialized as `{ data: null, error: "..." }`. The frontend reads `err.response?.data?.detail` falling back to `err.message`.

## Environment variables

| Variable | Default | Where |
|---|---|---|
| `ALLOWED_ORIGINS` | `http://localhost:5173` | `backend/.env` |
| `VITE_API_BASE_URL` | `http://localhost:8000` | `frontend/.env` |
