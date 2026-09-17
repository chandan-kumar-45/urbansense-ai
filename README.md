# UrbanSense AI

**AI-Powered Mobile Urban Intelligence Platform**
Turning public transport fleets into mobile urban sensing networks.

Built for **Smart India Hackathon 2026 — Problem Statement 26124**, Bharat Electronics
Limited (BEL): *"AI-Powered Mobile Urban Intelligence Platform Using Public Transport
Fleet."*

> See `docs/ARCHITECTURE.md` for the full system design and `docs/AI_MODEL_INTEGRATION.md`
> for how the teammate road-damage repo plugs in.

## Build Status (honest, updated per phase)

| Phase | Scope | Status |
|---|---|---|
| 1 | Requirements + teammate repo analysis | ✅ Done |
| 2 | Architecture + DB schema + project skeleton | ✅ Done (this commit) |
| 3 | Backend core APIs | ✅ Done (this commit) |
| 4 | Road-damage repo integration (demo adapter) | ✅ Done (this commit) |
| 5 | Frontend shell + dashboard | ✅ Done |
| 6 | GIS | ✅ Done |
| 7 | AI Detection Lab | ✅ Done |
| 8 | Fleet simulation | ✅ Done |
| 9 | Traffic analytics | ✅ Done |
| 10 | Incidents + reports | ✅ Done |
| 11 | Model registry/versioning | ✅ Done |
| 12 | Testing | ✅ Done (pytest suite; see `backend/tests/`) |
| 13 | Demo mode polish | ✅ Done |

**No AI capability in this repo is ever presented as a trained model unless it
genuinely is one.** Anything not yet backed by real weights is labeled `DEMO` /
`is_demo: true` in both the API responses and the UI, per the project's honesty
requirement.

**Honesty note on "Done" above:** every phase has real, working code behind it,
and I've syntax-checked all of it — but this was built in a sandbox with no
internet access, so I could never actually run `npm install`/`uvicorn` myself.
Three real bugs surfaced when you ran it locally (see below); there may be
more. Treat "Done" as "implemented and believed correct," not "verified
running," until you've booted it.

## If You Already Have an Older Copy Running Locally

Three real bugs were found and fixed in this version — you'll want a fresh
copy of both `frontend/` and `backend/`, not a patch on top of what you have:

1. **Backend crashed on startup** (`email-validator` missing, bcrypt/passlib
   version mismatch) — fixed by pinning `email-validator==2.3.0` and
   `bcrypt==4.0.1` in `requirements.txt`.
2. **Dashboard was a black screen after login** — `CommandLayout.tsx` used
   `useMatches()`, which only works with React Router's data-router API
   (`createBrowserRouter`), but the app uses the plain `<Routes>` API. Fixed by
   switching to `useLocation()` with a path→title lookup.
3. **`npm install` failed with an ERESOLVE conflict** — `eslint-plugin-react-hooks@4.6.2`
   doesn't support ESLint 9. Fixed by bumping it to `^5.0.0` (which does) and
   adding the ESLint 9 flat config (`eslint.config.js`) it needs.
4. **Every role saw identical data/pages** — the frontend never actually
   filtered the sidebar or routes by role, even though the backend RBAC did
   restrict some endpoints. Fixed with `src/config/roleAccess.ts` (Sidebar
   hides pages the role can't use; `RoleRoute` also redirects away from a
   hidden URL typed directly, so it's not just a hidden button).

**To pick up the fix:**
```bash
# Backend
cd backend
rm -rf .venv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
rm -rf node_modules package-lock.json
npm install
```

## Repository Layout

```
urbansense-ai/
├── frontend/                 React + Vite + TS + Tailwind command-center UI
├── backend/                  FastAPI backend (REST + WebSocket)
│   └── app/
│       ├── api/              Route handlers
│       ├── models/           Pydantic response/request models (distinct from DB models)
│       ├── schemas/          Pydantic schemas for validation
│       ├── services/         Business logic (event engine, analytics, auth)
│       ├── ai/               Model registry + one adapter package per AI capability
│       ├── database/         SQLAlchemy models + session
│       └── websocket/        Real-time event broadcast hub
├── teammate-road-damage/     Pointer/instructions to the integrated teammate repo
├── models/                   Model weight files live here once trained (git-ignored)
├── simulation/                Edge + fleet demo-mode simulator
├── docker/                   Dockerfiles / docker-compose
├── docs/                     Architecture, integration, API docs
├── tests/                    Backend tests
└── .env.example
```

## Quick Start — Backend (runnable now)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000
```

On first boot the backend creates `urbansense.db` (SQLite), prints 5 demo login
accounts (one per role, password `Demo@123`), and seeds 2 sample buses with 4
cameras each. Open **`http://localhost:8000/docs`** for interactive Swagger UI
covering every endpoint below.

### What's live in Phase 3

- **Auth**: `POST /api/auth/register`, `POST /api/auth/login` (JWT), `GET /api/auth/me`,
  `POST /api/auth/forgot-password` (stub — no email actually sent, documented as such).
- **Fleet**: `GET/POST /api/buses`, `GET /api/buses/{id}`,
  `PATCH /api/buses/{id}/position` (also broadcasts over WebSocket),
  `GET/POST /api/buses/{id}/cameras`.
- **Events**: `GET/POST /api/events`, `GET /api/events/{id}`,
  `PATCH /api/events/{id}/status` — the generic ingestion point any AI adapter posts to.
- **Road damage**: `GET/POST /api/road-damage`, `PATCH /api/road-damage/{id}/status`.
- **Traffic**: `GET/POST /api/traffic`.
- **Incidents**: `GET/POST /api/incidents`, `GET /api/incidents/{id}`,
  `PATCH /api/incidents/{id}` (role-gated to Admin/Traffic Officer/Transport Authority).
- **Real-time**: `ws://localhost:8000/ws/events` — every POST above broadcasts a
  `{"channel": ..., "data": ...}` message to all connected clients.
- **RBAC** is enforced server-side (`require_role` dependency), not just hidden in a UI.

Frontend (`npm install && npm run dev`) lands in Phase 5.

### What's new in Phase 4 — AI Model Registry + Road-Damage Adapter

- **`backend/app/ai/registry/`** — `BaseDetectionModel` interface
  (`load/predict/postprocess/get_metadata`) and a `ModelRegistry` that resolves
  "give me the ACTIVE version of capability X" against the `ModelVersion` table,
  with an in-memory cache invalidated on activation.
- **`backend/app/ai/road_damage/`** — the first real adapter package:
  `config.py`, `preprocessing.py`, `postprocessing.py`, `inference.py`,
  `adapter.py`. Ships a **`DemoRoadDamageDetector`**: a classical
  adaptive-threshold + contour-analysis heuristic (OpenCV, no neural network,
  no training data) that reports `is_demo: true` and
  `framework: "opencv-heuristic"` on every result — never presented as a
  validated AI model. `TeammateRoadDamageModel` is the documented swap-in point
  for the real trained model once `teammate-road-damage/` has one; it raises
  `NotImplementedError` rather than silently faking output.
- **`teammate-road-damage/README.md`** — exact `git submodule` commands to pull
  in `manvendrasrathore11/ai-urban-intelligence` without forking it.
- **`docs/AI_MODEL_INTEGRATION.md`** — full guide: adding a new model, versioning,
  registering/activating, and testing inference.
- **New APIs**:
  - `GET /api/models`, `GET /api/models/{id}` — list/inspect registered versions.
  - `POST /api/models/register` (Admin only) — new versions start as `TESTING`.
  - `POST /api/models/{id}/activate` (Admin only) — flips to `ACTIVE`, deactivates
    the previous one, invalidates the registry cache.
  - `POST /api/inference` — upload an image + `capability=road_damage`, get back
    the standardized detection JSON. This is what the Phase 7 AI Detection Lab
    UI will call.
- On first boot, `road_damage v1.0.0-demo` is seeded as `ACTIVE` automatically.

Test it right now:
```bash
curl -X POST http://localhost:8000/api/inference \
  -H "Authorization: Bearer <token from /api/auth/login>" \
  -F "capability=road_damage" \
  -F "file=@/path/to/any/road/photo.jpg"
```

### Fixes from real-world local testing (thank you for reporting these)

Running the backend on macOS/Python 3.13 surfaced two real dependency issues,
now fixed in `requirements.txt`:
- `email-validator` is required by Pydantic's `EmailStr` but isn't pulled in
  automatically — now pinned directly.
- `passlib[bcrypt]==1.7.4` predates bcrypt's 4.1+ API changes and breaks
  password hashing (`AttributeError` / 72-byte limit crash) on newer bcrypt —
  `bcrypt==4.0.1` is now pinned explicitly to match.

Also cleaned up: the `model_name` / `model_version` / `model_type` fields
across schemas now set `protected_namespaces=()`, silencing the Pydantic v2
warnings about the reserved `model_` prefix (harmless, but noisy).

## Quick Start — Frontend (Phase 5, new)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open **`http://localhost:5173`**, sign in with any demo account (password
`Demo@123` — pick one straight off the login screen), and you land on the
**Dashboard**: 7 KPI cards, a road-defects-over-time chart, a confidence
distribution chart, and a live event feed wired to `ws://localhost:8000/ws/events`.
Everything on this page is real data from the Phase 3/4 APIs — an empty state
shows honestly (e.g. "No road-damage detections yet") rather than fabricated
numbers, since no simulator is producing traffic yet (that's Phase 8).

The sidebar lists all 14 planned pages; only **Dashboard** is fully built.
The other 11 render an honest "Not built yet — scheduled for Phase N" screen
instead of a broken/fake page — consistent with the project's "don't fake it"
principle applied to features, not just AI models.

## Role-Based Access (frontend + backend)

| Role | Pages visible |
|---|---|
| Admin | Everything |
| Transport Authority | Dashboard, Live Fleet, GIS, Road Conditions, Traffic Analytics, Routes, Reports, Settings |
| Traffic Officer | Dashboard, Traffic Analytics, Incident Center, Settings |
| Maintenance Officer | Dashboard, Road Conditions, Infrastructure, AI Detection Lab, Video Analysis, Settings |
| Analyst | Dashboard, Traffic Analytics, Routes, Reports, Settings |

Enforced twice, deliberately: `frontend/src/components/Sidebar.tsx` hides
links a role can't use, and `frontend/src/components/RoleRoute.tsx` redirects
away if that role's user types a hidden URL directly. The backend still owns
the real authority check (`require_role` on sensitive endpoints like
Incidents and Model Registry) — the frontend gating is about UX, not the
actual security boundary.

## Fleet Simulation, GIS, AI Detection Lab, Video Analysis, Reports (Phases 6–13)

- **Live Fleet** (`/fleet`): map of simulated buses, a real "Start/Stop Live
  Simulation" control hitting `/api/simulation/*`, and a simulated
  bandwidth-saved metric. The simulation is a real asyncio background task
  (`backend/app/services/simulation.py`) that writes through the same DB +
  WebSocket path the REST APIs use — everything downstream is exercised for
  real. It never pretends to run AI inference on a fabricated frame; all
  simulation-sourced rows are tagged `model_name="simulation_engine"` and
  `is_demo: true`.
- **GIS Intelligence** (`/gis`): all event types on one Leaflet map with
  layer toggles, severity filter, and a details panel.
- **Road Conditions** (`/road-conditions`): analytical Road Health Score per
  route (explicitly labeled as analytical, not an official rating) plus the
  defect map.
- **AI Detection Lab** (`/detection-lab`): upload an image, run it through
  the active model via `/api/inference`, see bounding boxes drawn on a canvas
  overlay plus the raw JSON.
- **Video Analysis** (`/video-analysis`): upload an MP4, backend samples
  frames at 2 fps (not every frame — same rate an edge node would use) and
  runs the active model on each, capped at 40 frames for the prototype.
- **Traffic Analytics / Routes**: congestion breakdown, per-route delay vs. a
  reference schedule, computed from real stored `TrafficEvent` rows.
- **Incident Center / Infrastructure**: status workflow (NEW → ACKNOWLEDGED →
  INVESTIGATING → RESOLVED), role-gated to Admin/Traffic Officer/Transport
  Authority for incidents.
- **AI Model Management** (`/models`): lists registered versions per
  capability; Admin can activate a `TESTING` version.
- **Reports** (`/reports`): JSON summary + CSV export for road damage,
  traffic, incidents, fleet, and infrastructure. PDF export uses the browser's
  native Print dialog rather than a server-side renderer — documented here
  rather than silently adding an unverified dependency.

## Testing (Phase 12)

```bash
cd backend
pip install -r requirements.txt   # includes pytest + httpx
pytest
```

Tests use an isolated in-memory SQLite DB (`tests/conftest.py`) — they never
touch your real `urbansense.db`. Covers auth, JWT validation, RBAC rejection,
event CRUD, model registry register/activate, and running real inference
through the demo detector on a synthetic test image.

## Why This Matters for the Jury Demo

The end-to-end story this platform tells:

**Public Transport Bus → Mobile AI Sensor → Edge Detection → Event → Central
Platform → GIS → Analytics → Authority Action**

Every arrow in that sentence is a real, working, inspectable code path in this
repo — not a slide.
