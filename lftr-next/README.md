# LFTR Next

LFTR Next is a clean, runnable spine for the next-generation LFTR Marine Intelligence Globe. Google renders the world, future PostGIS services will understand place, Python computes live fields, and TypeScript morphs visuals. This first pass intentionally contains only mock contracts and TODO boundaries—no NOAA, RTOFS, or PostGIS integration yet.

## Architecture

- **Backend:** Python 3, FastAPI, Uvicorn ASGI.
- **Frontend:** TypeScript, Vite, Google `<gmp-map-3d>` placeholder.
- **Streaming:** Server-Sent Events at `/gfs/api/stream` and WebSocket placeholder at `/ws/gfs`.
- **Deployment templates:** systemd and Nginx placeholders in `deploy/`.

## Install

```bash
cd lftr-next
scripts/install.sh
```

The installer creates `.venv`, installs backend dependencies, installs frontend packages when `npm` exists, builds the frontend, and prints the next commands.

## Run

Backend:

```bash
cd lftr-next
. .venv/bin/activate
python -m app.main
```

Frontend development server:

```bash
cd lftr-next/frontend
npm run dev
```

Open the Vite URL, usually <http://127.0.0.1:5173>. The page boots a Google 3D map placeholder, layer pills, a mock scene fetch, and an SSE debug pane.


## Field Truth Engine

LFTR Next is organized around four truth/rendering responsibilities:

- **PostGIS = stable place truth:** future durable geometry, harbors, coast masks, lakes, named areas, and report joins. PostGIS is optional in this pass and disabled by default.
- **Field Engine = moving atmosphere/ocean truth:** Python builds compact scalar fields for clouds, rain, wind, humidity, sea-surface temperature, currents, and bait score.
- **Google map = base world renderer:** `<gmp-map-3d>` remains the world/camera substrate.
- **TypeScript renderer = morphing visual layer:** browser code samples compact field patches and morphs visual layers instead of receiving thousands of rendered objects.

The stream currently uses JSON field patches for readability. Binary Float32Array/quantized encodings are explicit TODOs after the contract stabilizes. Mock stream rate is configured by `LFTR_MOCK_STREAM_FPS` and defaults to 1 fps; `LFTR_TARGET_STREAM_FPS` records the future 5-10 fps target.



## GFS Atmosphere Provider

GFS is now modeled as a **provider adapter**, not a renderer. The adapter targets NCSS-style GFS access and maps available GFS variables such as total cloud cover, precipitation rate, humidity, temperature, pressure, and u/v wind into LFTR atmosphere field truth channels. The browser still receives compact field patches; it never receives thousands of server-made cloud objects.

Provider mode is controlled by `LFTR_PROVIDER_MODE=mock|live|hybrid`. Defaults are safe for offline development: `hybrid` mode with `LFTR_GFS_ENABLED=false` returns mock/degraded atmosphere frames. If live GFS fails, the provider attempts a last-good cache from `LFTR_GFS_CACHE_DIR`; if no cache exists, it returns a degraded mock frame with explicit provider metadata instead of crashing scene or stream endpoints.

Debug endpoints:

- `GET /gfs/api/providers/status` reports provider mode and GFS adapter status.
- `GET /gfs/api/providers/gfs?bbox=minLon,minLat,maxLon,maxLat` returns the atmosphere frame and provider metadata.
- `GET /gfs/api/field-truth?bbox=minLon,minLat,maxLon,maxLat` returns the encoded atmosphere field patch used by the stream.

Use `scripts/check_gfs_provider.py` against a running backend to validate mock/hybrid provider behavior.

## Morphing Renderer Lifecycle

The first renderer architecture intentionally avoids delete/redraw cycles:

1. **Snapshot:** the browser loads `/gfs/api/scene-frame` once to establish stable scene contracts.
2. **Stream:** the browser opens `/gfs/api/stream` and receives reconnect-friendly event IDs for heartbeat, atmosphere patches, ocean patches, and report patches.
3. **Field store:** incoming field patches update target state only; they do not directly redraw layers.
4. **Target state:** cloud, rain, ocean, bait, and report layers sample the latest compact field patches through capped budgets.
5. **Animation loop:** `requestAnimationFrame` ticks all animated layers.
6. **Morphing scene graph:** stable pooled DOM placeholders morph opacity, scale, footprint, altitude, and position toward the newest target values, fading unused objects instead of deleting them immediately.

Budgets are tiered as `global`, `regional`, and `local` so the renderer never creates unbounded particles or markers. Cloud placeholders sample `cloud_density` with wind advection TODO hooks from `wind_u`/`wind_v`; rain placeholders sample `rain_rate`; ocean placeholders sample `sst_c`, `current_u`/`current_v`, and `bait_score`.

## API Contracts

### `GET /health`

Returns:

```json
{"ok": true}
```

### `GET /gfs/api/scene-frame`

Returns a mock scene snapshot with these top-level keys:

- `ok`
- `scene_id`
- `generated_at`
- `bbox`
- `viewport`
- `layers`
- `spatial`
- `fields`

### `GET /gfs/api/reports?bbox=minLon,minLat,maxLon,maxLat`

Returns CSV-backed report points inside the requested bbox. If `data/reports.csv` is missing, the backend creates a small example CSV.

### `GET /gfs/api/viewport-spatial?bbox=minLon,minLat,maxLon,maxLat&tier=regional`

Returns reports, mock lakes, mock harbors, mock coast mask metadata, PostGIS status, and stable IDs for viewport-aware spatial truth.

### `GET /gfs/api/stream`

Streams mock SSE events:

- `scene.heartbeat`
- `atmosphere.field.patch`

### `WS /ws/gfs`

Accepts a WebSocket connection and echoes messages after an initial heartbeat placeholder.

## Checks

With the backend running:

```bash
scripts/check_health.sh
scripts/check_scene_snapshot.sh
scripts/check_gfs_provider.py
curl -N http://127.0.0.1:8787/gfs/api/stream
```

Frontend compile/build:

```bash
cd frontend
npm run build
```

## Deployment Templates

- `deploy/systemd/lftr-next.service` assumes installation under `/opt/lftr-next` and a `lftr` service user.
- `deploy/nginx/lftr-next.conf` serves the built frontend and proxies `/health`, `/gfs/api/`, and `/ws/gfs` to Uvicorn.

## TODO Boundaries

- Replace mock field patches with live Python field computation.
- Replace mock spatial truth with PostGIS-backed spatial services when `POSTGIS_ENABLED=true`.
- Add NOAA/RTOFS/GFS ingestion after contracts stabilize.
- Replace placeholder layer modules with efficient globe-native rendering.
