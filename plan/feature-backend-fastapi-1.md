---
goal: Build the FastAPI back-end for the html-2-md web application
version: 1.0
date_created: 2026-03-20
last_updated: 2026-03-20
owner: html-2-md Team
status: 'Planned'
tags: [feature, backend, fastapi, python]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan describes the complete implementation of the **html-2-md** FastAPI back-end — a Python API that accepts a URL, fetches the raw HTML content, converts it to clean Markdown, and returns the result for display and download by the Vue.js front-end.

---

## 1. Requirements & Constraints

- **REQ-001**: Python 3.12+ with `uv` for package management (preferred) or `pip` + `venv`.
- **REQ-002**: FastAPI with Pydantic v2 for request/response validation.
- **REQ-003**: `httpx` for async-compatible HTTP requests to external URLs.
- **REQ-004**: `beautifulsoup4` + `html2text` for HTML parsing and Markdown conversion.
- **REQ-005**: CORS middleware configured to allow the Vue.js dev server (`http://localhost:5173`) and production origin.
- **REQ-006**: Three endpoints: `POST /extract`, `POST /convert`, `GET /health`.
- **REQ-007**: Pyproject.toml (`[tool.fastapi]`) entrypoint for `fastapi dev` / `fastapi run` CLI.
- **REQ-008**: All endpoints return JSON with consistent envelope structure `{ "data": ..., "error": null }`.
- **SEC-001**: Validate URLs server-side using `pydantic`'s `AnyHttpUrl` type — reject non-HTTP(S) schemes (e.g. `file://`, `ftp://`) to prevent SSRF.
- **SEC-002**: Set a strict 10-second timeout on all outbound HTTP requests to prevent slow-loris / hanging threads.
- **SEC-003**: Block requests to private/loopback IP ranges (127.x, 10.x, 192.168.x, 172.16–31.x, ::1) to prevent SSRF.
- **SEC-004**: Limit maximum response body size to 10 MB to prevent memory exhaustion.
- **SEC-005**: Do not expose stack traces in production — use FastAPI exception handlers that return sanitised error messages.
- **CON-001**: No authentication required for MVP — the API is expected to run locally or behind an access-controlled deployment.
- **CON-002**: No database required — the API is stateless.
- **GUD-001**: Use `async` path operations only for I/O-bound calls (`httpx`); use regular `def` for CPU-bound transformation steps.
- **GUD-002**: Use `Annotated` for all dependency and parameter declarations (FastAPI best practice).
- **PAT-001**: Router-per-feature pattern: `routers/extract.py`, `routers/convert.py`.

---

## 2. Implementation Steps

### Phase 1 — Project Scaffold

- GOAL-001: Initialise the Python project structure and install dependencies.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create `backend/` directory in the workspace root | | |
| TASK-002 | Create `backend/pyproject.toml` with project metadata, dependencies (`fastapi[standard]`, `httpx`, `beautifulsoup4`, `html2text`, `lxml`), and `[tool.fastapi] entrypoint = "app.main:app"` | | |
| TASK-003 | Create `backend/.python-version` file with content `3.12` | | |
| TASK-004 | Create `backend/.env.example` with `ALLOWED_ORIGINS=http://localhost:5173` | | |
| TASK-005 | Create `backend/.env` (git-ignored) with the same defaults | | |

### Phase 2 — Project Structure

- GOAL-002: Create the Python package layout.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-006 | Create `backend/app/__init__.py` (empty) | | |
| TASK-007 | Create `backend/app/main.py` — FastAPI app instance, CORS middleware, include routers, health endpoint | | |
| TASK-008 | Create `backend/app/config.py` — Pydantic `Settings` class reading from `.env`; fields: `allowed_origins: list[str]`, `max_response_size_mb: int = 10`, `request_timeout_seconds: int = 10` | | |
| TASK-009 | Create `backend/app/routers/__init__.py` (empty) | | |
| TASK-010 | Create `backend/app/routers/extract.py` — `/extract` route | | |
| TASK-011 | Create `backend/app/routers/convert.py` — `/convert` route | | |
| TASK-012 | Create `backend/app/services/__init__.py` (empty) | | |
| TASK-013 | Create `backend/app/services/fetcher.py` — HTTP fetch service | | |
| TASK-014 | Create `backend/app/services/converter.py` — HTML-to-Markdown conversion service | | |
| TASK-015 | Create `backend/app/models.py` — All Pydantic request/response models | | |
| TASK-016 | Create `backend/app/exceptions.py` — Custom exception classes and FastAPI exception handlers | | |

### Phase 3 — Configuration & Middleware

- GOAL-003: Configure the FastAPI application with CORS and settings.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-017 | In `app/main.py`: instantiate `FastAPI(title="html-2-md API", version="1.0.0")` | | |
| TASK-018 | Add `CORSMiddleware` with origins from `Settings.allowed_origins`, `allow_methods=["GET","POST"]`, `allow_headers=["Content-Type"]` | | |
| TASK-019 | Register exception handlers for `ExtractError`, `ConvertError`, and generic `Exception` — all return `{"data": null, "error": "<message>"}` with appropriate HTTP status codes | | |
| TASK-020 | Add `GET /health` endpoint returning `{"data": {"status": "ok"}, "error": null}` with return type `HealthResponse` | | |

### Phase 4 — Pydantic Models

- GOAL-004: Define all request/response Pydantic models.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-021 | In `app/models.py`: define `ExtractRequest` with field `url: AnyHttpUrl` | | |
| TASK-022 | In `app/models.py`: define `ExtractResponse` with fields `html: str`, `title: str \| None`, `url: str` | | |
| TASK-023 | In `app/models.py`: define `ConvertRequest` with field `html: str` and validator `min_length=1` | | |
| TASK-024 | In `app/models.py`: define `ConvertResponse` with field `markdown: str` | | |
| TASK-025 | In `app/models.py`: define `HealthResponse` with field `status: str` | | |
| TASK-026 | In `app/models.py`: define generic `ApiResponse[T]` wrapper with fields `data: T \| None` and `error: str \| None` | | |

### Phase 5 — Fetcher Service

- GOAL-005: Implement the URL-fetching service with SSRF protection.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-027 | In `app/services/fetcher.py`: implement `_is_private_ip(ip: str) -> bool` using `ipaddress` stdlib module to block RFC-1918, loopback, link-local, and multicast ranges | | |
| TASK-028 | In `app/services/fetcher.py`: implement `_resolve_and_validate_host(url: str) -> None` that resolves the hostname to IP(s) using `socket.getaddrinfo` and calls `_is_private_ip` on each — raises `ExtractError` if any are private | | |
| TASK-029 | In `app/services/fetcher.py`: implement `async def fetch_html(url: str, settings: Settings) -> tuple[str, str]` that: (1) calls `_resolve_and_validate_host`, (2) uses `httpx.AsyncClient` with `timeout=settings.request_timeout_seconds`, `follow_redirects=True`, `max_redirects=5`, (3) checks `Content-Length` header and response size against `settings.max_response_size_mb`, (4) returns `(html_content, page_title)` | | |
| TASK-030 | In `fetcher.py`: enforce that only `text/html` and `text/plain` content-types are accepted; raise `ExtractError` with HTTP 422 for other MIME types | | |

### Phase 6 — Converter Service

- GOAL-006: Implement the HTML-to-Markdown conversion service.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-031 | In `app/services/converter.py`: implement `def convert_html_to_markdown(html: str) -> str` using `html2text.HTML2Text` with options: `body_width=0` (no line wrapping), `protect_links=True`, `unicode_snob=True`, `ignore_images=False`, `ignore_links=False`, `bypass_tables=False` | | |
| TASK-032 | Before conversion, pre-process the HTML with BeautifulSoup4 (`lxml` parser): remove `<script>`, `<style>`, `<noscript>`, `<iframe>` tags and HTML comments to produce clean input | | |
| TASK-033 | After conversion, post-process the Markdown: strip leading/trailing blank lines, normalise multiple consecutive blank lines to a maximum of two | | |

### Phase 7 — Routers

- GOAL-007: Implement the API route handlers.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-034 | In `app/routers/extract.py`: define `router = APIRouter(prefix="/extract", tags=["extract"])` | | |
| TASK-035 | In `extract.py`: implement `POST /` endpoint with signature `async def extract(body: ExtractRequest, settings: SettingsDep) -> ApiResponse[ExtractResponse]` — calls `fetch_html`, returns wrapped response | | |
| TASK-036 | In `app/routers/convert.py`: define `router = APIRouter(prefix="/convert", tags=["convert"])` | | |
| TASK-037 | In `convert.py`: implement `POST /` endpoint with signature `def convert(body: ConvertRequest) -> ApiResponse[ConvertResponse]` (use plain `def` since conversion is CPU-bound) — calls `convert_html_to_markdown`, returns wrapped response | | |
| TASK-038 | In `app/main.py`: include both routers with `app.include_router(extract_router)` and `app.include_router(convert_router)` | | |

### Phase 8 — Exception Handling

- GOAL-008: Implement custom exceptions and sanitised error handlers.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-039 | In `app/exceptions.py`: define `class ExtractError(Exception)` with `message: str` and `status_code: int` attributes | | |
| TASK-040 | In `app/exceptions.py`: define `class ConvertError(Exception)` with the same attributes | | |
| TASK-041 | In `app/main.py`: register `@app.exception_handler(ExtractError)` returning `JSONResponse(status_code=error.status_code, content={"data": null, "error": error.message})` | | |
| TASK-042 | In `app/main.py`: register `@app.exception_handler(RequestValidationError)` returning `422` with joined validation messages | | |
| TASK-043 | In `app/main.py`: register `@app.exception_handler(Exception)` returning `500` with a generic "Internal server error" message (no stack trace) | | |

---

## 3. Alternatives

- **ALT-001**: `requests` instead of `httpx` — rejected; `requests` is sync-only and would block the async event loop; `httpx` is the FastAPI-preferred HTTP client.
- **ALT-002**: `markdownify` instead of `html2text` — considered; `html2text` provides better control over output formatting and is more actively maintained for this use case.
- **ALT-003**: `playwright` or `selenium` for JS-rendered pages — excluded from MVP scope; adds heavy runtime dependencies. Can be added in v2 as an optional feature.
- **ALT-004**: Dedicated download endpoint (`GET /download`) — not needed; the front-end constructs the download client-side from the convert response, avoiding unnecessary server state.

---

## 4. Dependencies

| ID | Name | Version (min) | Purpose |
|----|------|--------------|---------|
| **DEP-001** | fastapi[standard] | 0.115+ | Web framework + CLI |
| **DEP-002** | httpx | 0.27+ | Async HTTP client for URL fetching |
| **DEP-003** | beautifulsoup4 | 4.12+ | HTML parsing and tag stripping |
| **DEP-004** | html2text | 2024.1+ | HTML to Markdown conversion |
| **DEP-005** | lxml | 5.2+ | Fast HTML parser for BeautifulSoup |
| **DEP-006** | pydantic-settings | 2.3+ | Settings management via `.env` |

---

## 5. Files

| ID | Path | Description |
|----|------|-------------|
| **FILE-001** | `backend/pyproject.toml` | Project metadata, dependencies, FastAPI entrypoint |
| **FILE-002** | `backend/app/main.py` | FastAPI app, CORS middleware, router registration, exception handlers |
| **FILE-003** | `backend/app/config.py` | Pydantic Settings class |
| **FILE-004** | `backend/app/models.py` | All Pydantic request/response models |
| **FILE-005** | `backend/app/exceptions.py` | Custom exception classes |
| **FILE-006** | `backend/app/routers/extract.py` | POST /extract route |
| **FILE-007** | `backend/app/routers/convert.py` | POST /convert route |
| **FILE-008** | `backend/app/services/fetcher.py` | URL fetch service with SSRF protection |
| **FILE-009** | `backend/app/services/converter.py` | HTML-to-Markdown converter service |
| **FILE-010** | `backend/.env.example` | Environment variable template |

---

## 6. Testing

| ID | Description |
|----|-------------|
| **TEST-001** | Health endpoint returns `200 OK` with `{"data": {"status": "ok"}, "error": null}` |
| **TEST-002** | `POST /extract` with a valid public URL returns `200` with non-empty `html` field |
| **TEST-003** | `POST /extract` with a private IP URL (e.g. `http://192.168.1.1`) returns `422` (SSRF protection) |
| **TEST-004** | `POST /extract` with a non-HTTP scheme (e.g. `file:///etc/passwd`) is rejected by Pydantic validation with `422` |
| **TEST-005** | `POST /extract` with an unreachable URL returns a `502` or `504` error with a user-friendly message |
| **TEST-006** | `POST /convert` with valid HTML returns `200` with a non-empty `markdown` field |
| **TEST-007** | `POST /convert` with empty string body returns `422 Unprocessable Entity` |
| **TEST-008** | `POST /convert` strips `<script>` and `<style>` tags before conversion |
| **TEST-009** | CORS headers are present on responses for the allowed origin |
| **TEST-010** | Stack traces are NOT present in any error response body |

---

## 7. Risks & Assumptions

- **RISK-001**: Websites using JavaScript-rendered content (SPAs) will only return an empty shell HTML. This is a known MVP limitation — document it in the README.
- **RISK-002**: Some websites may return gzip/brotli-encoded responses; `httpx` handles decompression automatically.
- **RISK-003**: Rate-limited or bot-protected sites may return 403/429. The API must surface these as user-friendly errors.
- **ASSUMPTION-001**: Python 3.12 is available in the deployment environment.
- **ASSUMPTION-002**: The service runs behind a reverse proxy in production; direct public internet exposure should be limited.

---

## 8. Related Specifications / Further Reading

- [Front-end Implementation Plan](./feature-frontend-vue-1.md)
- [FastAPI SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [html2text documentation](https://github.com/Alir3z4/html2text)
- [FastAPI official docs](https://fastapi.tiangolo.com)
