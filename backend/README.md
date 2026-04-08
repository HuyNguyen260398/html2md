# html-2-md — Backend API

A stateless **FastAPI** service that accepts a public URL, fetches the raw HTML, and returns clean Markdown. Used by the Vue.js front-end but can be called directly as a REST API.

## Architecture overview

```
POST /extract   →  fetch URL (httpx) → return HTML + title
POST /convert   →  clean HTML (BS4)  → convert to Markdown (html2text)
GET  /health    →  liveness check
```

All responses follow a consistent envelope:

```json
{ "data": <payload>, "error": null }
```

On errors the envelope becomes:

```json
{ "data": null, "error": "<human-readable message>" }
```

## Project structure

```
backend/
├── pyproject.toml          # Project metadata & dependencies (uv)
├── .env                    # Local environment variables (git-ignored)
├── .env.example            # Environment variable template
├── .python-version         # Pinned Python version (3.12)
└── app/
    ├── main.py             # FastAPI app, CORS middleware, exception handlers
    ├── config.py           # Pydantic Settings (reads from .env)
    ├── models.py           # Request / response Pydantic models
    ├── exceptions.py       # ExtractError, ConvertError
    ├── routers/
    │   ├── extract.py      # POST /extract/
    │   └── convert.py      # POST /convert/
    └── services/
        ├── fetcher.py      # Async HTTP fetch with SSRF protection
        └── converter.py    # HTML → Markdown conversion
```

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

## Getting started

### 1. Install dependencies

```bash
cd backend
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` as needed:

```env
# Comma-separated list of allowed CORS origins (must be valid JSON array)
ALLOWED_ORIGINS=["http://localhost:5173"]
```

### 3. Run the development server

```bash
uv run fastapi dev
```

The API is available at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

### 4. Run in production

```bash
uv run fastapi run
```

## API reference

### `GET /health`

Liveness check.

```json
{ "data": { "status": "ok" }, "error": null }
```

---

### `POST /extract/`

Fetch HTML from a public URL.

**Request**

```json
{ "url": "https://example.com" }
```

**Response**

```json
{
  "data": {
    "url": "https://example.com",
    "title": "Example Domain",
    "html": "<!doctype html>..."
  },
  "error": null
}
```

---

### `POST /convert/`

Convert an HTML string to Markdown.

**Request**

```json
{ "html": "<h1>Hello</h1><p>World</p>" }
```

**Response**

```json
{
  "data": { "markdown": "# Hello\n\nWorld" },
  "error": null
}
```

## Security

| Control | Detail |
|---|---|
| SSRF prevention | Hostname resolved via `socket.getaddrinfo`; requests to RFC-1918, loopback, link-local, multicast, and reserved ranges are rejected with `422` |
| URL scheme validation | Pydantic `AnyHttpUrl` rejects `file://`, `ftp://`, and other non-HTTP(S) schemes at request-validation time |
| Request timeout | All outbound HTTP requests have a strict 10-second timeout |
| Response size limit | Bodies larger than 10 MB are rejected before being fully downloaded |
| Content-type filter | Only `text/html` and `text/plain` responses are accepted |
| Error sanitisation | Stack traces are never included in API error responses |

## Configuration reference

| Variable | Default | Description |
|---|---|---|
| `ALLOWED_ORIGINS` | `["http://localhost:5173"]` | JSON array of allowed CORS origins |
| `MAX_RESPONSE_SIZE_MB` | `10` | Maximum response body size in MB |
| `REQUEST_TIMEOUT_SECONDS` | `10` | Outbound HTTP request timeout in seconds |

## Known limitations

- **JavaScript-rendered pages** — only the server-side HTML shell is returned. SPAs that rely on client-side rendering will produce minimal Markdown output.
- **Bot-protected sites** — servers returning `403`/`429` will surface as user-friendly errors rather than content.
