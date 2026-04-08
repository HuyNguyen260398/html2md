# Project Architecture Blueprint: html-2-md

> Generated: 2026-04-07
> Branch: feature/backend-dev

---

## Table of Contents

1. [Architectural Overview](#1-architectural-overview)
2. [Architecture Visualization](#2-architecture-visualization)
3. [Core Architectural Components](#3-core-architectural-components)
4. [Architectural Layers and Dependencies](#4-architectural-layers-and-dependencies)
5. [Data Architecture](#5-data-architecture)
6. [Cross-Cutting Concerns](#6-cross-cutting-concerns)
7. [Service Communication Patterns](#7-service-communication-patterns)
8. [Technology-Specific Patterns](#8-technology-specific-patterns)
9. [Testing Architecture](#9-testing-architecture)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Extension and Evolution Patterns](#11-extension-and-evolution-patterns)
12. [Architectural Decision Records](#12-architectural-decision-records)
13. [Blueprint for New Development](#13-blueprint-for-new-development)

---

## 1. Architectural Overview

### Application Summary

**html-2-md** is a web application that accepts a URL, fetches its HTML content from the web, and converts it to clean Markdown. It is structured as a decoupled, two-tier application:

- **Frontend**: Vue 3 SPA (Single Page Application) running in the browser
- **Backend**: FastAPI REST API serving as the processing engine

### Guiding Architectural Principles

| Principle | How It Is Applied |
|-----------|-------------------|
| **Separation of Concerns** | Frontend owns UI state; Backend owns fetch + conversion logic |
| **Security by Design** | SSRF protection, content-type filtering, size limits, URL validation at both tiers |
| **Composability** | Vue composables (`useApi`, `useTheme`) encapsulate reusable logic |
| **Thin Controllers** | FastAPI routers delegate immediately to service functions |
| **Explicit Contracts** | All API shapes defined via Pydantic models; no untyped dicts in responses |
| **Environment-First Config** | All runtime parameters driven by `.env` / environment variables |

### Architectural Pattern

The system follows a **Layered + Service-Oriented** pattern on the backend and a **Composable Component** pattern on the frontend:

```
Frontend (Composable Component Pattern)
└── Presentation Layer   → Vue components (AppHeader, UrlInput, ContentPanel, ActionBar)
└── State Layer          → App.vue (reactive refs, event handlers)
└── Service Layer        → composables/useApi.js (axios abstraction)

Backend (Layered Service Pattern)
└── API Layer            → FastAPI routers (/extract, /convert)
└── Service Layer        → services/fetcher.py, services/converter.py
└── Config/Model Layer   → config.py, models.py, exceptions.py
```

---

## 2. Architecture Visualization

### C4 Level 1 — System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                         html-2-md System                        │
│                                                                 │
│   ┌─────────────┐          ┌───────────────┐                   │
│   │   Browser   │◄────────►│  Vue 3 SPA    │                   │
│   │    User     │  HTTPS   │  (Frontend)   │                   │
│   └─────────────┘          └───────┬───────┘                   │
│                                    │ HTTP/REST                  │
│                            ┌───────▼───────┐                   │
│                            │  FastAPI API  │                   │
│                            │  (Backend)    │                   │
│                            └───────┬───────┘                   │
│                                    │ HTTPS                      │
│                            ┌───────▼───────┐                   │
│                            │  External     │                   │
│                            │  Websites     │                   │
│                            └───────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### C4 Level 2 — Container Diagram

```
┌─────────── Frontend (Vue 3 + Vite, port 5173) ─────────────────┐
│  index.html → main.js → App.vue                                 │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  AppHeader   │  │  UrlInput    │  │   ContentPanel (×2)  │  │
│  │  (theme tog) │  │  (validate)  │  │   HTML | Markdown    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│  ┌──────────────┐  ┌───────────────────────────────────────┐   │
│  │  ActionBar   │  │  useApi.js (axios)  useTheme.js       │   │
│  │  (buttons)   │  │  composables                          │   │
│  └──────────────┘  └───────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────┘
                     REST (JSON) │
┌─────────── Backend (FastAPI, port 8000) ───────────────────────┐
│                                                                  │
│  ┌───────────────────┐        ┌─────────────────────────────┐  │
│  │  POST /extract    │        │  POST /convert              │  │
│  │  extract.py       │        │  convert.py                 │  │
│  └────────┬──────────┘        └──────────┬──────────────────┘  │
│           │                              │                       │
│  ┌────────▼──────────┐        ┌──────────▼──────────────────┐  │
│  │  fetcher.py       │        │  converter.py               │  │
│  │  (httpx + SSRF)   │        │  (BS4 + html2text)          │  │
│  └───────────────────┘        └─────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  models.py  │  config.py  │  exceptions.py              │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────┘
                          HTTPS  │
                     ┌───────────▼──────────┐
                     │  External Websites   │
                     └──────────────────────┘
```

### Data Flow Sequence

```
User
 │
 ├─ enters URL in UrlInput.vue
 │   └─ validates: must be http:// or https://
 │
 ├─ clicks Extract → App.vue.extractContent()
 │   └─ useApi.extractContent(url) → POST /extract { url }
 │       └─ fetcher.fetch_html()
 │           ├─ SSRF check (DNS + IP range block)
 │           ├─ httpx GET with 10s timeout, 10 MB limit
 │           ├─ Content-Type check (text/html or text/plain)
 │           └─ returns (html, title)
 │       └─ ContentPanel renders raw HTML
 │
 ├─ clicks Convert → App.vue.convertToMarkdown()
 │   └─ useApi.convertToMarkdown(html) → POST /convert { html }
 │       └─ converter.convert_html_to_markdown()
 │           ├─ _clean_html() — removes scripts, styles, iframes (BeautifulSoup)
 │           ├─ html2text.HTML2Text conversion
 │           └─ _normalise_markdown() — collapse blank lines
 │       └─ ContentPanel renders Markdown
 │
 └─ clicks Download → App.vue creates Blob → triggers file download
```

---

## 3. Core Architectural Components

### 3.1 Frontend — App.vue (State Orchestrator)

**Purpose**: Central state hub. Owns all reactive data and top-level event handlers. Does not contain business logic — delegates to composables and child components via props/emits.

**Responsibilities**:
- Holds `rawHtml`, `markdownText`, `converting`, `apiError` as reactive refs
- Calls `useApi()` composable for all network operations
- Provides page-load animation cleanup (removes `#page-loader` on `onMounted`)
- Implements file download via `URL.createObjectURL(blob)`

**Key Interfaces**:
```
Props passed down:    rawHtml, markdownText, loading states, error states
Events listened to:   @extract, @convert, @download from child components
```

---

### 3.2 Frontend — Component Hierarchy

```
App.vue
├── AppHeader.vue       emits: toggle-theme
├── UrlInput.vue        emits: extract(url), props: loading, error
├── ContentPanel.vue    props: content, language, title (×2 instances)
├── ActionBar.vue       emits: convert, download, props: has-html, has-markdown, loading
└── LoadingSpinner.vue  props: size (sm|md|lg)
```

Each component is **purely presentational** except App.vue. No component reaches into the API directly.

---

### 3.3 Frontend — useApi.js Composable

**Purpose**: Abstracts all HTTP communication. Components never import axios directly.

**Pattern**: Composable factory returning reactive `loading`, `error` refs and async methods.

```javascript
// Usage pattern in App.vue
const { loading, error, extractContent, convertToMarkdown } = useApi()

// Endpoints called:
POST /extract    { url: string }   → { data: { html, title, url } }
POST /convert    { html: string }  → { data: { markdown: string } }
```

**Base URL**: Resolved from `VITE_API_BASE_URL` env var (fallback: `http://localhost:8000`)

---

### 3.4 Frontend — useTheme.js Composable

**Purpose**: Manages dark/light theme state with system preference detection and localStorage persistence.

**Mechanism**:
1. On init: reads `localStorage['theme']`, falls back to `prefers-color-scheme`
2. Toggle: adds/removes `.dark` on `document.documentElement`
3. Side effect: updates `<meta name="theme-color">` for PWA browser chrome

---

### 3.5 Backend — FastAPI Routers (extract.py, convert.py)

**Purpose**: Thin HTTP adapters. Parse/validate request bodies via Pydantic, call service functions, wrap results in `ApiResponse`.

**Pattern**: Zero business logic in routers. Each router has exactly one endpoint that calls exactly one service function.

```python
# Canonical router pattern
@router.post("/")
async def extract(body: ExtractRequest, ...) -> ApiResponse[ExtractResponse]:
    result = await service_function(body.field, settings)
    return ApiResponse(data=ResponseModel(...), error=None)
```

---

### 3.6 Backend — fetcher.py Service

**Purpose**: Secure HTTP fetcher with SSRF protection.

**Security layers**:
1. `AnyHttpUrl` Pydantic type — rejects non-HTTP(S) at model level
2. `_resolve_and_validate_host()` — DNS resolves hostname, blocks private IPs (RFC-1918, loopback, link-local, multicast, reserved)
3. `Content-Length` header check — rejects over-limit before streaming
4. Streaming read with running counter — enforces 10 MB even without `Content-Length`
5. `Content-Type` check — only `text/html` and `text/plain` accepted
6. 10-second timeout, max 5 redirects

---

### 3.7 Backend — converter.py Service

**Purpose**: Clean and convert HTML to Markdown.

**Pipeline**:
```
raw HTML
  → _clean_html()         # BeautifulSoup: remove script/style/noscript/iframe + HTML comments
  → html2text.convert()   # Converts to Markdown (no line wrapping, links preserved)
  → _normalise_markdown() # Strip outer whitespace, collapse 3+ blank lines → 2
  → clean Markdown string
```

---

### 3.8 Backend — models.py

**Purpose**: Single source of truth for all API request/response shapes.

```python
ApiResponse[T]     # Generic envelope: { data: T | null, error: string | null }
ExtractRequest     # { url: AnyHttpUrl }
ExtractResponse    # { html: str, title: str | None, url: str }
ConvertRequest     # { html: str (min_length=1) }
ConvertResponse    # { markdown: str }
HealthResponse     # { status: str }
```

All responses use `ApiResponse[T]` — both success and error cases use the same envelope. Success sets `data`, error sets `error` (never both).

---

### 3.9 Backend — config.py

**Purpose**: Typed, environment-driven configuration via pydantic-settings.

```python
class Settings(BaseSettings):
    allowed_origins: list[str]      # default: ["http://localhost:5173"]
    max_response_size_mb: int       # default: 10
    request_timeout_seconds: int    # default: 10
```

Injected into routers via FastAPI's `Annotated` dependency injection (`SettingsDep`).

---

### 3.10 Backend — exceptions.py

**Purpose**: Domain-specific exception types with HTTP status codes embedded.

```python
ExtractError(message, status_code=502)  # upstream fetch failures
ConvertError(message, status_code=500)  # conversion failures
```

Exception handlers in `main.py` catch these and produce `ApiResponse(error=message)` with the correct HTTP status.

---

## 4. Architectural Layers and Dependencies

### Backend Layer Rules

```
┌─────────────────────────────────────┐
│  HTTP Layer (routers/)              │  ← Can import: services, models, config, exceptions
│  extract.py, convert.py             │
├─────────────────────────────────────┤
│  Service Layer (services/)          │  ← Can import: models, config, exceptions
│  fetcher.py, converter.py           │     Cannot import: routers
├─────────────────────────────────────┤
│  Foundation Layer                   │  ← Cannot import: routers or services
│  models.py, config.py, exceptions.py│
└─────────────────────────────────────┘
```

**Dependency rule**: Each layer imports only from its own layer or layers below it. No upward imports.

### Frontend Layer Rules

```
┌─────────────────────────────────────┐
│  View Layer                         │  ← Can import: composables, child components
│  App.vue, components/               │
├─────────────────────────────────────┤
│  Composable Layer                   │  ← Can import: axios, browser APIs
│  composables/useApi.js              │     Cannot import: Vue components
│  composables/useTheme.js            │
├─────────────────────────────────────┤
│  Asset Layer                        │  ← No imports
│  assets/themes.css, tailwind.css    │
└─────────────────────────────────────┘
```

---

## 5. Data Architecture

### API Response Envelope

Every API response (success or error) uses the same `ApiResponse[T]` wrapper:

```json
// Success
{ "data": { "html": "...", "title": "...", "url": "..." }, "error": null }

// Error
{ "data": null, "error": "Failed to fetch: connection refused" }
```

This ensures the frontend can always destructure `{ data, error }` without branching on status codes for error types.

### Frontend State Model

State lives in `App.vue` as flat reactive refs (no Vuex/Pinia store):

| Ref | Type | Populated by |
|-----|------|-------------|
| `rawHtml` | `string` | `/extract` response |
| `markdownText` | `string` | `/convert` response |
| `converting` | `boolean` | `useApi().loading` |
| `apiError` | `string \| null` | `useApi().error` |

### Data Transformations

```
URL (string)
  → Pydantic AnyHttpUrl (validated)
  → httpx response bytes → decoded string (raw HTML)
  → BeautifulSoup DOM → cleaned HTML string
  → html2text → raw Markdown string
  → normalised Markdown string
  → Blob (binary) → downloadable .md file
```

---

## 6. Cross-Cutting Concerns

### 6.1 Security

| Concern | Implementation | Location |
|---------|---------------|----------|
| SSRF prevention | DNS resolution + IP range block | `fetcher.py:_resolve_and_validate_host()` |
| URL scheme enforcement | `AnyHttpUrl` Pydantic type | `models.py:ExtractRequest` |
| Response size limit | Content-Length check + streaming counter | `fetcher.py:fetch_html()` |
| Request timeout | httpx timeout config | `fetcher.py:fetch_html()` |
| Content-Type filtering | Header inspection | `fetcher.py:fetch_html()` |
| CORS | FastAPI `CORSMiddleware` | `main.py` |
| XSS protection | DOMPurify (dependency installed) | Available in frontend — not yet wired |
| Input validation (frontend) | URL pattern check (http/https regex) | `UrlInput.vue` |
| Input validation (backend) | Pydantic model validation | `models.py` |

### 6.2 Error Handling

**Backend**: Three-tier error handling:
1. **Pydantic validation errors** (422) — caught by `RequestValidationError` handler in `main.py`
2. **Domain errors** (`ExtractError`, `ConvertError`) — caught by custom handlers, returned as `ApiResponse(error=...)`
3. **Unexpected errors** (500) — caught by generic `Exception` handler, returns sanitized message (no stack trace)

**Frontend**: Errors from `useApi()` are surfaced as the `error` ref, displayed as a dismissible banner in `App.vue`. No error bubbles unhandled to the browser console from user actions.

### 6.3 Configuration Management

```
Backend:  .env file → pydantic-settings Settings class → injected via FastAPI DI (SettingsDep)
Frontend: .env file → Vite VITE_* prefix → import.meta.env.VITE_API_BASE_URL at build time
```

Secrets never committed — `.env.example` files document required variables in both tiers.

### 6.4 Theming

Dark/light mode uses **CSS custom properties** (design tokens) defined in `themes.css`, toggled by adding/removing `.dark` on `<html>`. Tailwind's `darkMode: 'class'` config enables `dark:` utility variants. No CSS-in-JS, no runtime style injection.

```css
:root           { --color-canvas-default: #ffffff; ... }
.dark           { --color-canvas-default: #0d1117; ... }
```

Preference persisted in `localStorage`, applied before first paint in `index.html` inline script to prevent theme flash.

---

## 7. Service Communication Patterns

### API Contract

| Endpoint | Method | Request Body | Success Response |
|----------|--------|-------------|-----------------|
| `/health` | GET | — | `ApiResponse<{ status: "ok" }>` |
| `/extract` | POST | `{ url: string }` | `ApiResponse<{ html, title, url }>` |
| `/convert` | POST | `{ html: string }` | `ApiResponse<{ markdown: string }>` |

All requests and responses are `application/json`.

### Communication Pattern: Synchronous REST

The frontend calls the backend synchronously (request/await response). No WebSockets, no SSE, no polling. The convert endpoint is CPU-bound and completes fast enough that synchronous calls are appropriate.

### Vite Dev Proxy

In development, Vite rewrites `/api/*` → `http://localhost:8000/*`. This eliminates CORS issues during development. In production, the frontend expects `VITE_API_BASE_URL` to point to the deployed backend.

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

**Note**: `useApi.js` currently uses the base URL directly (not the `/api` proxy path). If the proxy is to be used in production, `useApi.js` should route through `/api`.

---

## 8. Technology-Specific Patterns

### 8.1 Vue 3 Patterns

**Composition API throughout** — no Options API. All logic in `setup()` via `<script setup>`.

**Composable convention**:
- File: `composables/use{Feature}.js`
- Returns reactive refs and methods
- No global store (Pinia/Vuex) — state is local to `App.vue` and passed down as props

**Component communication**: strictly props-down, emits-up. No `provide`/`inject` or event bus.

**No Vue Router** — single-page, single-route app. No routing needed.

### 8.2 Vite / Build Patterns

- `import.meta.env.VITE_*` for compile-time environment variables
- `jsdom` test environment for Vitest (no real browser needed)
- No SSR — purely client-side rendering

### 8.3 FastAPI Patterns

**Annotated dependency injection**:
```python
SettingsDep = Annotated[Settings, Depends(get_settings)]
```

**Generic response model**: `ApiResponse[T]` as return type annotation — FastAPI serializes via Pydantic automatically.

**Router registration**: Separate router files, included in `main.py` with `app.include_router()`.

**Async vs sync**: `fetcher.py` is `async def` (I/O-bound: HTTP). `converter.py` is `def` (CPU-bound: parsing). FastAPI runs sync handlers in a thread pool automatically.

### 8.4 Python Dependency Management

Uses **uv** (not pip or poetry) for reproducible installs. `uv.lock` pins all transitive dependencies. `pyproject.toml` is the single config file for project metadata, dependencies, and tool configuration.

---

## 9. Testing Architecture

### Frontend Tests

- **Runner**: Vitest (configured via `vite.config.js`)
- **Environment**: jsdom (DOM APIs available)
- **Location**: co-located `__tests__/` directory alongside source files
- **Current coverage**: `useApi.js` composable (bootstrap state, export shape)

**Testing pattern**:
```javascript
vi.mock('axios')   // mock at module boundary, not at composable internals
const { loading, error, extractContent } = useApi()
expect(loading.value).toBe(false)
```

**Gaps**: No component tests yet. No E2E tests. DOMPurify integration untested.

### Backend Tests

No test files exist yet. Recommended test boundaries:

| Test Type | Target | Priority |
|-----------|--------|----------|
| Unit | `converter.py` — HTML cleaning and MD output | High |
| Unit | `fetcher.py` — `_is_private_ip()`, `_resolve_and_validate_host()` | High |
| Integration | `POST /extract` with mocked httpx | Medium |
| Integration | `POST /convert` with real html2text | Medium |
| Security | SSRF: private IP ranges blocked | High |

---

## 10. Deployment Architecture

### Development Topology

```
Terminal 1: cd backend && uvicorn app.main:app --reload   → http://localhost:8000
Terminal 2: cd frontend && npm run dev                     → http://localhost:5173
```

### Environment Configuration

| Variable | Tier | Default | Purpose |
|----------|------|---------|---------|
| `ALLOWED_ORIGINS` | Backend | `["http://localhost:5173"]` | CORS allowed origins |
| `MAX_RESPONSE_SIZE_MB` | Backend | `10` | Max upstream response size |
| `REQUEST_TIMEOUT_SECONDS` | Backend | `10` | httpx request timeout |
| `VITE_API_BASE_URL` | Frontend | `http://localhost:8000` | Backend base URL |

### CI/CD (GitHub Actions)

**Workflow**: `.github/workflows/frontend.yml`

```
trigger: push to main/feature/*, PRs
path filter: frontend/** only

jobs:
  install  → npm ci (cached node_modules)
  build    → npm run build
  test     → npm test (vitest run)
```

No backend CI pipeline exists yet.

### Production Considerations

- Frontend: static files (`dist/`) can be served from any CDN or static host
- Backend: ASGI server (uvicorn/gunicorn) behind a reverse proxy (nginx)
- `ALLOWED_ORIGINS` must include the production frontend domain
- `VITE_API_BASE_URL` must point to the production backend URL

---

## 11. Extension and Evolution Patterns

### Adding a New API Endpoint

1. Define request/response models in `backend/app/models.py`
2. Create `backend/app/routers/{feature}.py` with an `APIRouter`
3. Create `backend/app/services/{feature}.py` with the business logic
4. Register the router in `backend/app/main.py` with `app.include_router()`
5. Add the corresponding call in `frontend/src/composables/useApi.js`

**Do not**: put business logic in routers, or call httpx/bs4 directly from routers.

### Adding a New Vue Component

1. Create `frontend/src/components/{ComponentName}.vue` using `<script setup>`
2. Accept data via `defineProps()`, emit events via `defineEmits()`
3. Never import `axios` or call API directly — use `useApi()` from `App.vue`
4. If logic is reusable across components, extract to `composables/use{Feature}.js`

### Adding a New Configuration Setting

1. Add field to `Settings` class in `backend/app/config.py` with a default
2. Add to `.env.example` with a comment explaining the value
3. Inject via `SettingsDep` in the router that needs it

### Extending the Conversion Pipeline

The converter is a simple linear pipeline (`_clean_html → html2text → _normalise`). To add a step:

1. Add a new private function `_step_name(input: str) -> str` in `converter.py`
2. Insert it into the `convert_html_to_markdown()` pipeline at the appropriate position
3. The pipeline is synchronous and stateless — each function takes a string and returns a string

---

## 12. Architectural Decision Records

### ADR-001: No Global State Manager (No Pinia/Vuex)

**Context**: Vue 3 apps often use Pinia for state management.

**Decision**: All state lives in `App.vue` as local refs, passed to children via props.

**Rationale**: The application has a single linear user flow (extract → convert → download) with no shared state between sibling subtrees. A global store would add indirection without benefit.

**Consequence**: If the app grows to multiple routes or complex cross-component state, migrate to Pinia.

---

### ADR-002: Generic `ApiResponse[T]` Envelope

**Context**: REST APIs can return different shapes for success vs error.

**Decision**: All endpoints return `ApiResponse[T]` with `data` and `error` fields.

**Rationale**: Frontend can always destructure the same shape regardless of success/failure. Avoids branching on HTTP status codes for application-level errors.

**Consequence**: HTTP status codes are still used (422, 502, 500) but the response body is always consistent.

---

### ADR-003: SSRF Protection in Fetcher

**Context**: The `/extract` endpoint fetches arbitrary user-supplied URLs.

**Decision**: Resolve DNS before making the request and block private/reserved IP ranges.

**Rationale**: Without this, the backend could be used to probe internal network services.

**Consequence**: Legitimate private-network URLs (intranet sites) cannot be fetched. This is intentional.

---

### ADR-004: Decoupled Frontend and Backend

**Context**: Could have been a server-rendered app (e.g., FastAPI + Jinja2).

**Decision**: Completely separate Vue SPA and FastAPI API, communicating only over REST.

**Rationale**: Clear separation of concerns, independent deployability, and the ability to serve the frontend from a CDN.

**Consequence**: Requires CORS configuration and two separate processes in development.

---

### ADR-005: html2text + BeautifulSoup over a Single Library

**Context**: Several Python HTML-to-Markdown libraries exist.

**Decision**: Pre-clean HTML with BeautifulSoup (remove noise elements), then convert with html2text.

**Rationale**: html2text alone does not strip script/style tags; BS4 alone does not produce Markdown. Combining them gives clean input to the converter.

**Consequence**: Two-step pipeline. If a single library covers both needs well, consolidation is possible.

---

## 13. Blueprint for New Development

### Starting a New Feature — Checklist

**Backend feature (new endpoint)**:
- [ ] Add models to `models.py`
- [ ] Add service function(s) to `services/`
- [ ] Add router in `routers/` — thin, delegates to service
- [ ] Register router in `main.py`
- [ ] Add exception type to `exceptions.py` if needed
- [ ] Update `.env.example` if new config is added

**Frontend feature (new UI capability)**:
- [ ] If new API call: add method to `composables/useApi.js`
- [ ] If new reusable logic: create `composables/use{Feature}.js`
- [ ] Create component in `components/` — props-down, emits-up
- [ ] Wire into `App.vue` state if it needs application-level data

### Common Pitfalls to Avoid

| Pitfall | Correct Approach |
|---------|-----------------|
| Business logic in FastAPI routers | Move to `services/` |
| Direct axios usage in Vue components | Use `useApi()` composable |
| Skipping SSRF validation for new fetch operations | Always use `fetch_html()` or replicate its validation |
| Returning raw exception messages to frontend | Catch in `main.py` handlers, return sanitized message |
| Hardcoding origins in CORS config | Read from `Settings.allowed_origins` |
| Storing secrets in `.env` and committing | Use `.env.example` for templates; `.env` is gitignored |
| Adding `data` and `error` both non-null | Exactly one should be non-null in every `ApiResponse` |

### File Naming Conventions

| Location | Convention | Example |
|----------|-----------|---------|
| Vue components | PascalCase | `ContentPanel.vue` |
| Composables | camelCase with `use` prefix | `useApi.js` |
| Backend routers | snake_case, noun | `extract.py` |
| Backend services | snake_case, noun | `fetcher.py`, `converter.py` |
| Pydantic models | PascalCase | `ExtractRequest`, `ApiResponse` |

---

## Appendix: Project File Map

```
html-2-md/
├── frontend/
│   ├── src/
│   │   ├── main.js                  # Vue app entry
│   │   ├── App.vue                  # State orchestrator
│   │   ├── components/
│   │   │   ├── AppHeader.vue        # Header + theme toggle
│   │   │   ├── UrlInput.vue         # URL field + extract button
│   │   │   ├── ContentPanel.vue     # Code display (html/markdown)
│   │   │   ├── ActionBar.vue        # Convert + Download buttons
│   │   │   └── LoadingSpinner.vue   # Animated spinner
│   │   ├── composables/
│   │   │   ├── useApi.js            # Axios wrapper
│   │   │   └── useTheme.js          # Dark/light mode
│   │   └── assets/
│   │       ├── themes.css           # CSS custom properties (light/dark tokens)
│   │       └── tailwind.css         # Tailwind directives
│   ├── index.html                   # Entry HTML + page loader + theme flash prevention
│   ├── vite.config.js               # Build + dev proxy + test config
│   ├── tailwind.config.js           # darkMode: class + color tokens
│   └── package.json                 # Dependencies
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, middleware, exception handlers
│   │   ├── config.py                # Settings via pydantic-settings
│   │   ├── models.py                # Request/response Pydantic models
│   │   ├── exceptions.py            # ExtractError, ConvertError
│   │   ├── routers/
│   │   │   ├── extract.py           # POST /extract
│   │   │   └── convert.py           # POST /convert
│   │   └── services/
│   │       ├── fetcher.py           # SSRF-safe HTTP fetch
│   │       └── converter.py         # HTML → Markdown pipeline
│   ├── pyproject.toml               # Python project + deps (uv)
│   └── .env.example                 # Required env vars template
│
└── .github/
    └── workflows/
        └── frontend.yml             # CI: install, build, test (frontend only)
```

---

*This blueprint reflects the architecture as of 2026-04-07. Update this document when routers, services, component boundaries, or data models change significantly.*
