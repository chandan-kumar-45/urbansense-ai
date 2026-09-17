# AI Model Integration Guide

This explains how UrbanSense AI's model plug-in architecture works, using the
road-damage capability (and the teammate's repo) as the worked example. The same
pattern applies to every other capability (traffic, pedestrian, traffic_sign,
waterlogging, license_plate, rash_driving).

## 1. How the teammate model is integrated

`github.com/manvendrasrathore11/ai-urban-intelligence` is pulled in as a **git
submodule** at `teammate-road-damage/` (see `teammate-road-damage/README.md` for
the exact commands). The platform never imports it directly from the API/frontend
layer — it only talks to it through the adapter at
`backend/app/ai/road_damage/adapter.py` and `inference.py`.

As of this writing, that repo is confirmed to be an empty skeleton (placeholder
`config.py` / `model.py` / `detector.py` / `main.py`, no weights, no YOLO). So the
adapter currently serves `DemoRoadDamageDetector` — a classical computer-vision
heuristic (adaptive thresholding + contour analysis), **not** a trained neural
network — and reports `is_demo: true` / `framework: "opencv-heuristic"` on every
response so the UI never claims it's a validated AI model.

## 2. Where model files are placed

```
models/
  road_damage/
    v1.0.0-demo/     # no files needed — heuristic, not weights
    v1.1.0/          # teammate's first trained model would go here, e.g. best.pt
    v2.0.0/          # future improved model
```

`models/` is git-ignored for actual weight files (too large for git) — only the
folder structure and a `.gitkeep` are committed. Real deployments would pull
weights from object storage (S3/GCS) at container startup; documented as a future
improvement, not implemented in this prototype.

## 3. How to update the teammate's repo

```bash
cd teammate-road-damage
git pull origin main
cd ..
git add teammate-road-damage && git commit -m "Update teammate-road-damage submodule"
```

## 4. How to add a brand-new AI model (a new capability)

1. Create `backend/app/ai/<capability>/{config.py, preprocessing.py, postprocessing.py, inference.py, adapter.py}`
   mirroring the road_damage package.
2. In `inference.py`, implement a class extending `BaseDetectionModel`
   (`backend/app/ai/registry/base.py`) with `load / predict / postprocess /
   get_metadata`. If no trained model exists yet, ship an honestly-labeled demo
   detector, exactly like `DemoRoadDamageDetector`.
3. In `adapter.py`, call `register_adapter_factory("<capability>", your_factory_fn)`.
4. Import that adapter module once at startup (see `app/main.py`'s
   `import app.ai.<capability>.adapter` lines) so the factory registers itself.
5. `POST /api/models/register` a `ModelVersion` row for it, then
   `POST /api/models/{id}/activate`.
6. The generic `POST /api/inference` endpoint and the (Phase 7) AI Detection Lab
   UI immediately work with it — no other code changes needed.

## 5. How to change model versions / promote a new one

```
POST /api/models/register
{
  "model_name": "road_damage",
  "version": "1.1.0",
  "model_type": "yolov8",
  "framework": "pytorch",
  "supported_classes": ["pothole","cracked_road","damaged_asphalt","road_depression","debris"],
  "is_demo": false
}
→ created with status = TESTING

POST /api/models/{id}/activate
→ status = ACTIVE (previous ACTIVE version for the same model_name is set to INACTIVE)
```

The registry's in-memory cache is invalidated on activation
(`ModelRegistry.invalidate(capability)`), so the very next `/api/inference` call
uses the newly-active version — no backend restart required.

## 6. How to register a model (step-by-step for road_damage v1.1.0 once trained)

1. Add your teammate's trained weights under `models/road_damage/v1.1.0/`.
2. Edit `TeammateRoadDamageModel` in
   `backend/app/ai/road_damage/inference.py`: implement `load()` to actually load
   those weights, and `predict()` to run real inference and return `Detection`
   objects. Remove the `NotImplementedError`s.
3. Update `build_road_damage_adapter()` in `adapter.py` if you need to branch on
   `model_version_row.model_type` (e.g. `"yolov8"` vs `"onnx"`) to pick the right
   loader.
4. `POST /api/models/register` with `is_demo: false` and the real `model_type`.
5. `POST /api/models/{id}/activate`.
6. Test via `POST /api/inference` with a road image before relying on it for the
   live demo — see "How to test inference" below.
7. **You don't need to touch the camera/fleet pipeline at all.** Once the new
   version is `ACTIVE`, `backend/app/services/capture.py` (used by both the
   fleet simulation and the manual `POST /api/buses/{bus_id}/cameras/{camera_id}/capture`
   endpoint) automatically calls `registry.get_active_model(db, "road_damage")`
   — it will start running your real model the moment it's activated, tagging
   every resulting `RoadDefect` with `is_demo: false` and the real
   `model_version` and `camera_id` automatically.

## 6a. How the 4-camera capture pipeline works today

Every bus has 4 cameras (`FRONT`/`REAR`/`LEFT`/`RIGHT`, seeded automatically —
see `app/main.py`'s `seed_demo_data()`). Two things drive detections:

- **Fleet simulation** (`POST /api/simulation/start`): each tick, each active
  bus has a ~35% chance one of its 4 cameras is chosen at random and run
  through `app/services/capture.py::capture_and_detect()`.
- **Manual trigger**: `POST /api/buses/{bus_id}/cameras/{camera_id}/capture`
  runs the same function once, immediately — this is what the "Capture Now"
  button on the Live Fleet page (click a bus row to expand its 4 cameras) calls.

Both paths call the exact same function, which:
1. Calls `capture_frame(camera)` — currently a synthetic frame generator
   (stands in for a real camera/RTSP read; swap this one function for a real
   frame grab and nothing downstream changes).
2. Calls `registry.get_active_model(db, "road_damage")` — whichever model is
   currently `ACTIVE`, demo heuristic or a real trained model.
3. Runs `model.predict(frame)` → `model.postprocess(...)`.
4. For each detection, writes a `RoadDefect` row with `bus_id`, `camera_id`,
   the bus's current GPS, and `is_demo`/`model_version` taken directly from
   the model that produced it — never hardcoded.
5. Broadcasts the new defect over `ws://.../ws/events` so the dashboard, GIS
   map, and Live Fleet page all update instantly.

**To wire in a real camera feed instead of the synthetic generator:**
Replace the body of `capture_frame()` in `backend/app/services/capture.py`
with a real read — e.g. `cv2.VideoCapture(camera.rtsp_url).read()` (you'd add
an `rtsp_url` column to the `Camera` model) or a call into an edge device's
local inference API. Everything from step 2 onward is unchanged.

## 7. How to test inference

```bash
curl -X POST http://localhost:8000/api/inference \
  -F "capability=road_damage" \
  -F "file=@sample_road.jpg"
```

Returns the standardized detection JSON (see `docs/ARCHITECTURE.md` §2), including
`is_demo` and `model_version` so you can confirm exactly which detector produced
the result. The AI Detection Lab page (Phase 7) is a UI wrapper around this same
endpoint.

## 8. Future plug-in formats

The `BaseDetectionModel` interface doesn't care whether `predict()` internally
runs a classical heuristic, a `ultralytics.YOLO` model, an ONNX Runtime session, or
a TensorRT engine — as long as it returns a `list[Detection]`. This is intentional:
YOLO, YOLO-seg, RT-DETR, custom PyTorch, ONNX, and TensorRT backends can all be
added later as new `inference.py` implementations without changing the registry,
API, or frontend.
