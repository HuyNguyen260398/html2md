# html-2-md

A web application that fetches the content of any website, converts it to clean human- and AI-readable Markdown, and lets you download the result.

Built with **Vue 3** on the front-end and **FastAPI** on the back-end. Designed with a GitHub-flavored light/dark theme.

---

## Features

- **Extract** — Enter any public URL and fetch its raw HTML content
- **Preview** — Inspect the raw HTML before conversion
- **Convert** — Transform the HTML into clean, structured Markdown
- **Download** — Save the resulting `.md` file with one click
- **Theme toggle** — Switch between GitHub Light and GitHub Dark at any time; preference is persisted across sessions
- **Responsive layout** — Works on mobile and desktop

> [!NOTE]
> Pages that rely heavily on JavaScript to render content (Single Page Applications) may return an empty HTML shell, as the extractor fetches static HTML only.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Front-end | Vue 3 (Composition API), Vite, Tailwind CSS |
| Back-end | FastAPI, Python 3.12 |
| HTTP client | httpx |
| HTML parsing | BeautifulSoup4 + lxml |
| Markdown conversion | html2text |

---

## Project Structure

```
html-2-md/
├── frontend/          # Vue 3 SPA
│   ├── src/
│   │   ├── assets/    # Global CSS (theme tokens)
│   │   ├── components/
│   │   ├── composables/
│   │   └── App.vue
│   └── vite.config.js
├── backend/           # FastAPI service
│   ├── app/
│   │   ├── routers/   # extract.py, convert.py
│   │   ├── services/  # fetcher.py, converter.py
│   │   ├── models.py
│   │   ├── config.py
│   │   └── main.py
│   └── pyproject.toml
└── plan/              # Implementation plans
```

---

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.12+
- `uv` (recommended) or `pip`

### Back-end

```bash
cd backend

# Install dependencies (using uv)
uv sync

# Copy environment variables
cp .env.example .env

# Start the development server
fastapi dev
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Front-end

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start the development server
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/extract` | Fetch raw HTML from a URL |
| `POST` | `/convert` | Convert HTML to Markdown |

### POST `/extract`

```json
// Request
{ "url": "https://example.com" }

// Response
{
  "data": { "html": "<!DOCTYPE html>...", "title": "Example", "url": "https://example.com" },
  "error": null
}
```

### POST `/convert`

```json
// Request
{ "html": "<!DOCTYPE html>..." }

// Response
{
  "data": { "markdown": "# Example\n\nThis is the body..." },
  "error": null
}
```

---

## Security

The back-end enforces several protections to prevent abuse:

- **SSRF protection** — Requests to private IP ranges (RFC-1918, loopback, link-local) are blocked
- **URL scheme validation** — Only `http://` and `https://` URLs are accepted
- **Response size limit** — Responses larger than 10 MB are rejected
- **Timeout** — Outbound requests are capped at 10 seconds
- **Error sanitisation** — Stack traces are never exposed in API responses

---

## Environment Variables

### Back-end (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS-allowed origins (comma-separated) |

### Front-end (`frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Back-end API base URL |

---

## Implementation Plans

Detailed, phase-by-phase implementation plans are available in the [`plan/`](./plan/) directory:

- [`plan/feature-frontend-vue-1.md`](./plan/feature-frontend-vue-1.md) — Front-end development plan
- [`plan/feature-backend-fastapi-1.md`](./plan/feature-backend-fastapi-1.md) — Back-end development plan
