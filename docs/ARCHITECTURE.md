# UrbanSense AI — System Architecture

**SIH 2026 · Problem Statement 26124 · Bharat Electronics Limited (BEL)**
AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet

---

## 1. Design Principle

The platform is built as a **pipeline of loosely-coupled stages**. No stage knows the
internal details of the stage before or after it — they only agree on a JSON contract.
This is what lets us swap a demo detector for a real trained model, or add a brand-new
AI capability (e.g. waterlogging), without touching the frontend or the database schema.

```
Bus Camera (FRONT/REAR/LEFT/RIGHT/CABIN)
        │  raw video frames
        ▼
Edge AI Processing (simulated edge node per bus)
        │  samples frames, attaches GPS + timestamp
        ▼
AI Model Registry  ──────────────►  looks up ACTIVE model for a given capability
        │  loads Model.predict(frame)
        ▼
Detection / Event Engine
        │  standardized Detection JSON (class, confidence, bbox, severity)
        ▼
Event API  (POST /api/events, /api/road-damage, /api/traffic, /api/incidents)
        │
        ▼
Central Backend (FastAPI)
        │  validation → persistence → broadcast
        ▼
Database (PostgreSQL + PostGIS)  ──┬──►  WebSocket Hub ──► Dashboard (real-time feed)
                                    └──►  REST Query APIs ──► GIS / Analytics / Reports
```

## 2. The Standardized Detection Contract

Every AI model, real or demo, must return this shape. The backend and frontend are
built against **this contract only** — never against a specific model's internals.

```json
{
  "model": "road_damage",
  "model_version": "1.0.0-demo",
  "is_demo": true,
  "frame_id": "bus-001-front-000234",
  "processing_time_ms": 42,
  "detections": [
    {
      "class": "pothole",
      "confidence": 0.91,
      "bbox": [x1, y1, x2, y2],
      "severity": "HIGH"
    }
  ]
}
```

`is_demo` is mandatory and non-optional. The frontend refuses to render a detection
badge as "AI Verified" unless `is_demo === false` — this is how we keep the "never
fake AI capability" rule enforced in code, not just in a design doc.

## 3. Component Responsibilities

| Layer | Responsibility | Tech |
|---|---|---|
| Edge Simulator | Per-bus process that "plays" a route, generates frames/events, calls the AI Registry, attaches GPS+time, pushes events to the backend | Python (`simulation/`) |
| AI Model Registry | Central lookup: "give me the ACTIVE model for capability X" → returns a loaded `BaseModel` instance | Python (`backend/app/ai/registry`) |
| Model Adapters | One per capability (road_damage, traffic, pedestrian, traffic_sign, waterlogging, license_plate, rash_driving). Each implements `load / predict / postprocess / get_metadata` | Python |
| Event Engine | Turns a raw detection into a persisted domain event (RoadDefect, TrafficEvent, Incident, DetectionEvent) and decides severity/dedup | FastAPI service layer |
| Backend API | REST + WebSocket, auth, RBAC, persistence | FastAPI + SQLAlchemy + Pydantic |
| Database | Relational + geospatial storage | PostgreSQL 15 + PostGIS (SQLite fallback for zero-install local dev) |
| Frontend | Command-center UI: dashboard, GIS map, fleet, detection lab, incidents, reports | React + Vite + TS + Tailwind + shadcn/ui + MapLibre + Recharts |

## 4. Why the Road-Damage Repo Becomes an "Adapter", Not the Core

Your teammate's repo (`manvendrasrathore11/ai-urban-intelligence`) is currently a
skeleton: empty `src/road_damage/{config,model,detector,main}.py`, empty
`models/road_damage/`, empty `outputs/events/`. Rather than building the platform
*around* it, we:

1. Keep it as its own git history/repo (linked via `docs/AI_MODEL_INTEGRATION.md`
   instructions — submodule or subtree, your team's choice).
2. Write a thin **adapter** in `backend/app/ai/road_damage/adapter.py` that imports
   from it and re-shapes its output into the standardized Detection contract above.
3. Until a trained model exists, the adapter runs a clearly-labeled
   **DemoRoadDamageDetector** (`is_demo: true`) so the rest of the platform (events,
   GIS, dashboard, reports) is fully working today. Swapping in the real model later
   is a one-file change — see `docs/AI_MODEL_INTEGRATION.md`.

## 5. Model Versioning / Registry

```
road_damage/
  v1.0.0-demo   → ACTIVE   (mock heuristic detector, clearly labeled)
  v1.1.0        → (future) teammate's first trained model → TESTING
  v2.0.0        → (future) improved model → INACTIVE until promoted
```

`POST /api/models/register` adds a version. `POST /api/models/{id}/activate` flips
which version the registry hands out for that capability — with zero frontend/backend
redeploy. The frontend's **AI Model Management** page just lists whatever the registry
returns.

## 6. Bandwidth Reduction (Edge Inference)

Instead of streaming raw video (~5 Mbps/camera) to the server, each edge node sends
only: detection JSON + a single evidence JPEG per event (typically a few hundred KB
at most, often just a few KB of JSON when no evidence image is required). The
dashboard shows a **Bandwidth Saved** metric computed from
`(raw_stream_bytes - actually_sent_bytes) / raw_stream_bytes`, labeled
**Simulated / Estimated** since we are not metering a real cellular modem in this
prototype.

## 7. Roles → Feature Access

| Role | Access |
|---|---|
| Admin | everything |
| Transport Authority | Fleet, GIS, Analytics, Reports |
| Traffic Officer | Traffic, Incidents |
| Maintenance Officer | Road Defects, Infrastructure |
| Analyst | Analytics, Reports |

Enforced server-side via JWT claim + FastAPI dependency (`require_role(...)`), not
just hidden in the UI.

## 8. What "Demo Mode" Actually Does

`simulation/engine.py` is a real Python process (not a UI trick) that:
- moves N buses along predefined lat/lng route polylines,
- periodically calls the same AI Registry / adapters real inference would call,
- posts the resulting events through the *real* `/api/events` REST API,
- so the entire pipeline downstream (DB → WebSocket → dashboard → GIS → analytics)
  is exercised for real. Only the "camera input" is synthetic. This is why the demo
  is honest: nothing downstream of "there is a video frame" is faked.

## 9. Local Dev Note (SQLite vs PostgreSQL/PostGIS)

Given SIH prototyping needs a laptop-only zero-install path, the backend defaults to
SQLite via `DATABASE_URL` in `.env` and stores lat/lng as plain floats. Switching
`DATABASE_URL` to a Postgres+PostGIS DSN upgrades geometry columns automatically via
the same SQLAlchemy models (see `backend/app/database/models.py` docstring) — no
application code changes needed, only a migration. This is documented, not hidden.
