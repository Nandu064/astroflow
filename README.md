# AstroFlow — Space Science Intelligence Platform

> Real-time asteroid tracking, solar event monitoring, and exoplanet discovery — streamed live to your browser via WebSocket.

---

## What Is This?

AstroFlow is a full-stack space science intelligence platform that ingests data from three NASA APIs and a NOAA space weather feed, stores it in PostgreSQL, and streams live server metrics + science data to a real-time dashboard via WebSocket. Every metric on screen updates every second without a page refresh.

**Built to demonstrate:** async Python architecture, real-time WebSocket broadcast systems, GraphQL APIs, ETL pipeline orchestration, and a production-quality Vue 3 dashboard.

---

## Live Dashboard

```
● LIVE  02:10:41 UTC

MISSION CONTROL
REAL-TIME SPACE INTELLIGENCE · LIVE DATA STREAM

┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Near-Earth   │  │ CPU Usage    │  │ Memory       │  │ WS           │
│ Objects      │  │              │  │              │  │ Connections  │
│     4        │  │   1.5%       │  │   8.9%       │  │     3        │
│ approaches   │  │ server load  │  │ RAM util     │  │ active       │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘

┌─────────────────────────────────┐  ┌──────────────────────────────┐
│ CPU & MEMORY · LAST 60 SECONDS  │  │ NEAREST APPROACH  ✓ SAFE     │
│ ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈  │  │ (2018 WX1)                   │
│ ─────────────────────────────── │  │                              │
│ [live waveform chart, 1Hz]      │  │ Distance  Velocity  Diameter │
└─────────────────────────────────┘  │  0.052 AU  10.22 km/s  39 m │
                                     │  [animated orbit canvas]     │
                                     └──────────────────────────────┘
┌──────────────────────────────┐  ┌──────────────────────────────────┐
│ ETL PIPELINE STATUS          │  │ LIVE EVENT STREAM                │
│ ● Exoplanet Archive    IDLE  │  │ [timestamped alerts]             │
│ ● NOAA Space Weather   IDLE  │  │                                  │
│ ✕ NASA NEO Feed       FAILED │  │                                  │
│ ✕ Solar Flare Events  FAILED │  │                                  │
└──────────────────────────────┘  └──────────────────────────────────┘
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser (Vue 3 + Vuetify)                                      │
│  ┌───────────┐  ┌────────────────┐  ┌──────────────────────┐   │
│  │ Dashboard │  │ GraphQL Views  │  │ Pinia Realtime Store │   │
│  │ (charts,  │  │ (Asteroids,    │  │ WS → shallowRef →    │   │
│  │  orbit)   │  │  Exoplanets,   │  │ Chart.js 1Hz update  │   │
│  └───────────┘  │  Solar Events) │  └──────────────────────┘   │
│                 └────────────────┘                               │
└──────────────────┬──────────────────────────────┬───────────────┘
        WebSocket /ws                     GraphQL /graphql
                  │                               │
┌─────────────────▼───────────────────────────────▼───────────────┐
│  FastAPI (uvicorn, uvloop, single-process)                       │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │ WebSocket Broadcast │    │ Strawberry GraphQL              │ │
│  │ ┌─────────────────┐ │    │ (Asteroid, SolarEvent,          │ │
│  │ │ _cache_loop     │ │    │  Exoplanet queries)             │ │
│  │ │ DB → memory     │ │    └─────────────────────────────────┘ │
│  │ │ every 5s        │ │    ┌─────────────────────────────────┐ │
│  │ │                 │ │    │ APScheduler (AsyncIOScheduler)  │ │
│  │ │ _broadcast_loop │ │    │ NASA NEO · Solar Flares         │ │
│  │ │ cache + psutil  │ │    │ NOAA Weather · Exoplanets       │ │
│  │ │ → all WS 1Hz    │ │    └─────────────────────────────────┘ │
│  │ └─────────────────┘ │                                        │
│  └─────────────────────┘                                        │
└──────────────────────────────────────┬──────────────────────────┘
                                       │ asyncpg
                              ┌────────▼────────┐
                              │  PostgreSQL 15   │
                              │  asteroids       │
                              │  solar_events    │
                              │  exoplanets      │
                              │  etl_jobs        │
                              └──────────────────┘
```

---

## Tech Stack

### Backend
| Layer | Technology | Reason |
|---|---|---|
| Web framework | **FastAPI** (Python 3.11) | Async-native, built-in WebSocket, OpenAPI auto-docs |
| GraphQL | **Strawberry** | Code-first, type-safe, native async, works natively with FastAPI |
| WebSocket engine | Custom asyncio tasks | Two cooperative tasks: 5s DB cache refresh + 1s broadcast |
| ORM | **SQLAlchemy 2.0 async** + asyncpg | Non-blocking DB, connection pool (10 + 20 overflow) |
| Database | **PostgreSQL 15** | ACID, MVCC concurrent reads never block ETL writes |
| Cache | **Redis** | Session-ready for future rate-limit and pub/sub work |
| ETL scheduler | **APScheduler AsyncIOScheduler** | 4 cron jobs in the same event loop, no threads needed |
| HTTP client | **aiohttp** | Async NASA/NOAA API calls |
| System metrics | **psutil** | CPU %, memory %, uptime |
| Runtime | **uvloop** | libuv event loop backend, 2–4× faster than stdlib asyncio |

### Frontend
| Layer | Technology | Reason |
|---|---|---|
| Framework | **Vue 3** (Composition API) | `<script setup>`, `shallowRef` for Chart.js safety, reactivity |
| UI system | **Vuetify 3** | Material Design components, dark theme, responsive grid |
| State | **Pinia** | Modular stores; realtime store manages WS + demo fallback |
| Charts | **Chart.js** + vue-chartjs | Canvas-based, handles 1Hz streaming without DOM thrashing |
| GraphQL client | **Apollo Client** + `@vue/apollo-composable` | Reactive queries, cache normalisation |
| Build | **Vite** + vite-plugin-vuetify | HMR, WS proxy, tree-shaking |

---

## Data Sources

| ETL Job | API | Schedule | Records (approx) |
|---|---|---|---|
| **NASA NEO Feed** | `api.nasa.gov/neo/rest/v1/feed` | Every 6 hours | ~40 per week |
| **Solar Flare Events** | `api.nasa.gov/DONKI/FLR` | Every 30 min | ~10 per month |
| **NOAA Space Weather** | `services.swpc.noaa.gov` | Every 15 min | Real-time indices |
| **Exoplanet Archive** | NASA TAP/sync (IPAC) | Every 24 hours | 6,291 confirmed planets |

---

## Running Locally

### Prerequisites
- Docker + Docker Compose
- Node 18+ (for the frontend dev server)
- A free NASA API key from [api.nasa.gov](https://api.nasa.gov) _(optional — `DEMO_KEY` works but is rate-limited to 30 req/hour)_

### Start the backend stack
```bash
git clone https://github.com/you/astroflow.git
cd astroflow

# Optional: add your NASA key
echo "NASA_API_KEY=your_key_here" > .env

docker compose up --build
```

Backend: `http://localhost:8000` · Postgres: `5432` · Redis: `6379`

### Start the frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

Vite proxies `/graphql`, `/health`, and `/ws` to `localhost:8000`.

### Key Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Service info |
| `GET /health` | System health (CPU, memory, uptime, connections) |
| `GET /health/etl` | ETL job status with last-run times and record counts |
| `POST /graphql` | GraphQL — query asteroids, exoplanets, solar events |
| `GET /graphql` | GraphiQL interactive IDE |
| `WS /ws` | Real-time broadcast stream (JSON, 1 Hz) |

### WebSocket Payload Shape
```json
{
  "ts": "2026-05-26T02:10:41+00:00",
  "metrics": { "cpu": 1.5, "mem": 8.9, "mem_used_gb": 0.71, "connections": 3, "uptime_s": 120 },
  "neo": {
    "name": "(2018 WX1)", "dist_au": 0.0517, "vel_km_s": 10.22,
    "diam_min_m": 39.5, "diam_max_m": 88.3, "hazardous": false
  },
  "etl": [
    { "name": "Exoplanet Archive", "status": "idle", "duration_s": 8.5,
      "records": 6291, "success_rate": 100.0, "error": null }
  ]
}
```

---

## Engineering Challenges & Resolutions

Everything below actually happened during development. Included here because the debugging process is more instructive than the happy path.

---

### Challenge 1 — Docker Build Failure: `psutil` won't compile on Apple Silicon

**Symptom:** `fatal error: stdlib.h: No such file or directory` during `pip install psutil`.

**Root cause:** The Python Docker image for `linux/aarch64` (Apple Silicon via Docker Desktop) ships without C development headers. `psutil` compiles a C extension and needs them.

**Fix:**
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl python3-dev \
    && rm -rf /var/lib/apt/lists/*
```

**Lesson:** Always include `python3-dev` when your dependencies build native extensions on Debian-based images.

---

### Challenge 2 — `TypeError: can't subtract offset-naive and offset-aware datetimes`

**Symptom:** `/health/etl` crashed with a timezone arithmetic error.

**Root cause:** SQLAlchemy model defaults used `default=datetime.utcnow` — deprecated in Python 3.11 and returns a timezone-naive `datetime`. The column was declared `DateTime(timezone=True)`, so the database stored timezone-aware values. Subtracting the two types raises a `TypeError`.

**Fix:** Replaced every instance across all model and service files:
```python
# Before (broken)
default=datetime.utcnow

# After (correct)
default=lambda: datetime.now(timezone.utc)
```

**Lesson:** `datetime.utcnow()` is deprecated since Python 3.12. Always use `datetime.now(timezone.utc)` for timezone-aware code.

---

### Challenge 3 — `Object.entries()[0] is not iterable` (Apollo Symbol key)

**Symptom:** Vue app crashed immediately on boot before rendering.

**Root cause:** `DefaultApolloClient` is a JavaScript `Symbol`. `Object.entries()` only returns string-keyed properties — it silently skips Symbol keys. The Apollo client was never actually provided to the component tree.

**Fix:**
```javascript
// Before (broken — Symbol key silently dropped)
Object.entries(provide).forEach(([key, val]) => app.provide(key, val))

// After (correct — Symbol key registered directly)
import { DefaultApolloClient } from '@vue/apollo-composable'
app.provide(DefaultApolloClient, apolloClient)
```

**Lesson:** JavaScript's `Object.entries()` / `Object.keys()` are not Symbol-aware. When a library uses a Symbol as a provide/inject key, you must handle it explicitly.

---

### Challenge 4 — `Cannot read properties of undefined (reading '56')` (JS ASI)

**Symptom:** Dashboard orbit canvas crashed immediately on render.

**Root cause:** JavaScript's Automatic Semicolon Insertion (ASI). Two statements on adjacent lines:
```javascript
ctx.fill()
[20, 38, 56].forEach(r => { ... })
```
ASI does **not** insert a semicolon before `[`. The parser reads the second line as array subscript access on the return value of `ctx.fill()`, which is `undefined`. `undefined[56]` — crash.

**Fix:**
```javascript
ctx.fill()
;[20, 38, 56].forEach(r => { ... })   // leading ; prevents ASI ambiguity
```

**Lesson:** Any line starting with `[`, `(`, `` ` ``, `+`, or `-` can be accidentally joined to the line above by the parser. Use a leading semicolon on such lines when following an expression statement.

---

### Challenge 5 — WebSocket broadcast loop crashes silently (UnboundLocalError)

**Symptom:** Backend logs showed `[BL] pre-sleep tick=1` but **never** `[BL] post-sleep tick=1`. The dashboard stayed in DEMO mode. `asyncio.sleep(1)` appeared to freeze indefinitely. Testing asyncio.sleep in isolation proved it worked fine inside the container.

**Root cause:** Python's function-scope variable rule combined with asyncio's silent task exception handling.

Inside `_broadcast_loop`, there was:
```python
if dead:
    _clients -= dead   # ← augmented assignment anywhere in the function
                        #   makes _clients LOCAL throughout the entire function
```

Python's compiler sees `_clients -= dead` and marks `_clients` as a local variable for the **entire** function body — even above the assignment. The `len(_clients)` call printed right after `asyncio.sleep(1)` read an unassigned local, raising `UnboundLocalError`.

The key: `UnboundLocalError` inherits from `Exception`. The `try/except Exception` block in the while loop **should** have caught it — but the `len(_clients)` call was *outside* the try block. The exception propagated out of the coroutine. Asyncio caught it at the task boundary, stored it in `Task.exception()`, and marked the task done — **silently**. No log, no traceback, no reraise. The task was dead.

This is why it looked like `asyncio.sleep` was frozen: the sleep completed normally on the very first tick, but the crash on the very next line made it appear as if no tick had ever finished.

**Fix:**
```python
# Before (rebinds _clients as local — crashes with UnboundLocalError)
_clients -= dead

# After (mutates the existing set in place — _clients stays global)
_clients.difference_update(dead)
```

**Lesson 1:** In Python, augmented assignment (`-=`, `+=`, `|=`, etc.) anywhere in a function makes the variable local everywhere in that function — even above the first write.

**Lesson 2:** Asyncio tasks swallow exceptions silently. During debugging, always wrap the entire task coroutine body in `try/except BaseException` and log or re-raise. `CancelledError` (raised on cancellation) inherits from `BaseException`, not `Exception` — so a bare `except Exception` won't catch it either.

---

### Challenge 6 — `RangeError: Maximum call stack size exceeded` (Vue reactive + Chart.js)

**Symptom:** After the backend was fixed and WS data was flowing, the frontend still showed DEMO mode. Browser console was flooded with stack overflow errors deep inside Vue's reactive proxy and Chart.js.

**Root cause:** Vue 3's `ref([...])` wraps arrays with a deep `Proxy`. Chart.js internally annotates dataset arrays with `_meta` properties during rendering. When Chart.js mutated a reactive array, Vue's setter fired, triggering `chartData` computed re-evaluation, which built a new Chart.js config referencing the same reactive array, which Chart.js then annotated again — infinite mutual recursion.

**Fix:** Two changes:

```javascript
// stores/realtime.js — use shallowRef (deep array mutations invisible to Vue)
import { shallowRef } from 'vue'
const cpuHistory = shallowRef(Array(60).fill(null))

// Replace instead of mutate (shallowRef only reacts to .value replacement)
function _pushChart(cpu, mem) {
  cpuHistory.value = [...cpuHistory.value.slice(1), cpu ?? null]
  memHistory.value = [...memHistory.value.slice(1), mem ?? null]
}
```

**Lesson:** Never pass deeply-reactive Vue arrays to libraries that annotate them internally (Chart.js, D3, etc.). Use `shallowRef` + immutable updates for any data that crosses into third-party renderers.

---

### Challenge 7 — Uvicorn `--reload` killing the broadcast task on every startup

**Root cause:** `--reload` uses WatchFiles to restart the worker whenever any `.py` file changes. Python writes `__pycache__/*.pyc` files during import. These writes trigger WatchFiles, which restarts the process — repeatedly and immediately after startup.

**Fix:** Remove `--reload`. For production-like dev, use file watching at the docker-compose level or restart containers manually.

---

### Challenge 8 — `--workers 1` corrupts asyncio event loop timers

**Root cause:** Uvicorn's `--workers N` uses `os.fork()` (via `multiprocessing`). The forked child inherits the parent's open file descriptors, including the epoll/kqueue FD that uvloop uses for its timer heap. In the child, these FDs point to the **parent's** kernel event structures. Timer callbacks are queued but the FD is stale — the child's event loop never gets notified. `asyncio.sleep(1)` would be scheduled and then never wake up.

**Fix:** Remove `--workers` entirely. A single-process async server already handles concurrent requests through cooperative multitasking.

---

### Challenge 9 — `start_broadcast()` blocking application startup

**Symptom:** "Application startup complete." never appeared in logs. The backend appeared to hang during startup.

**Root cause:** The original `start_broadcast()` called `await _refresh_cache()` before creating the background tasks. At startup, all four ETL jobs launched simultaneously via `asyncio.create_task`. The Exoplanet ETL holds a DB connection for ~9 seconds inserting 6,291 rows. Under connection pool contention, `_refresh_cache()`'s `SELECT` stalled waiting for a connection — blocking the entire startup coroutine.

**Fix:** Remove `await _refresh_cache()` from `start_broadcast()`. Let `_cache_loop` handle the first refresh asynchronously in the background.

---

## Key Design Decisions

### Why two asyncio tasks (cache + broadcast) instead of one?

One task querying the DB on every 1-second tick = 60 DB queries per minute, competing with 4 ETL jobs. The split:
- `_cache_loop` — refreshes DB data into module-level dicts every **5 seconds**
- `_broadcast_loop` — reads from cache + `psutil` every **1 second**, zero DB calls

The broadcast loop is now O(1) computation + O(clients) network sends.

### Why `asyncio.create_task` instead of threads?

The broadcaster lives inside uvicorn's event loop. `create_task` schedules coroutines cooperatively. Threads would require locks around `_clients` and add OS scheduling overhead. For I/O-bound fanout (send to N clients), cooperative async is the right primitive.

### Why not Server-Sent Events instead of WebSocket?

SSE is HTTP-based and unidirectional (server → client only). WebSocket is a true persistent bidirectional connection. For a control dashboard where future versions will send commands back (e.g. "trigger ETL now"), WebSocket is the correct foundation.

### Why `shallowRef` for chart history?

Vue 3 deep-proxies `ref` arrays so even `array[i] = x` triggers reactivity. Chart.js writes `_meta` onto dataset arrays during render. Those writes trigger Vue, which re-renders, which makes Chart.js write again — infinite loop. `shallowRef` exposes only `.value` assignment to reactivity; array internals are invisible to Vue.

---

## Project Structure

```
cosmos/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py          # REST health + ETL status endpoints
│   │   │   └── websocket.py       # WS accept/relay endpoint
│   │   ├── etl/
│   │   │   ├── base.py            # ETLJob record helpers (mark_running/done/failed)
│   │   │   ├── nasa_neo.py        # NASA NeoWs ingestion
│   │   │   ├── solar_flares.py    # NASA DONKI solar flare ingestion
│   │   │   ├── noaa_weather.py    # NOAA space weather ingestion
│   │   │   ├── exoplanets.py      # NASA Exoplanet Archive TAP ingestion
│   │   │   └── scheduler.py       # APScheduler setup + job wiring
│   │   ├── graphql/
│   │   │   └── schema.py          # Strawberry schema (types + resolvers)
│   │   ├── models/
│   │   │   ├── asteroid.py
│   │   │   ├── solar_event.py
│   │   │   ├── exoplanet.py
│   │   │   └── etl_job.py
│   │   ├── services/
│   │   │   └── broadcaster.py     # WebSocket broadcast engine (2 tasks)
│   │   ├── config.py              # Pydantic Settings (env vars)
│   │   ├── database.py            # SQLAlchemy async engine + Redis client
│   │   └── main.py                # FastAPI app + startup/shutdown hooks
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   │   └── LiveStreamChart.vue    # Chart.js 1Hz line chart
│   │   │   └── common/
│   │   │       └── MetricCard.vue         # Animated metric card
│   │   ├── stores/
│   │   │   └── realtime.js                # Pinia WS store + demo fallback
│   │   ├── views/
│   │   │   ├── DashboardView.vue          # Mission Control (main)
│   │   │   ├── AsteroidsView.vue          # NEO table + GraphQL
│   │   │   ├── SolarView.vue              # Solar events + GraphQL
│   │   │   ├── ExoplanetsView.vue         # Exoplanet catalog + GraphQL
│   │   │   └── HealthView.vue             # Server health view
│   │   ├── plugins/apollo.js              # Apollo Client setup
│   │   └── main.js                        # App bootstrap + providers
│   └── vite.config.js                     # Vite + WS proxy config
└── docker-compose.yml
```

---

## What's Next

- [ ] NASA API key — unblocks NEO and Solar Flare ETLs (currently 429 on DEMO_KEY)
- [ ] Exoplanet ETL — replace 6,291 individual SELECTs with a single bulk `INSERT ... ON CONFLICT DO UPDATE` (100× faster)
- [ ] Redis pub/sub — enable horizontal scaling: multiple uvicorn workers share broadcast channel
- [ ] Alert engine — emit `alert` WS events when asteroid < 0.05 AU or solar flare is X-class+
- [ ] E2E tests with Playwright
- [ ] CI/CD with GitHub Actions

---

*Built with Python 3.11 · FastAPI · Strawberry GraphQL · SQLAlchemy 2.0 · PostgreSQL · Vue 3 · Vuetify · Chart.js*
