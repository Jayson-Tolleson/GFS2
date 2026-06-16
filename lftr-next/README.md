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


## RTOFS Ocean Provider

RTOFS is the ocean field-truth provider. Like GFS, it is an adapter that feeds compact backend fields rather than rendered objects. The ocean renderer samples those fields client-side for current streamlets, SST hints, bait glow, and future boat orientation.

The RTOFS provider is safe by default: `LFTR_RTOFS_PROVIDER_MODE=hybrid` and `LFTR_RTOFS_ENABLED=false` return degraded mock ocean truth with explicit metadata. Live RTOFS failures fall back to last-good cache from `LFTR_RTOFS_CACHE_DIR`; if no cache exists, the provider returns mock ocean fields and never crashes scene or stream endpoints.

Ocean truth channels include `sst_c`, `current_u`, `current_v`, and derived `bait_score`, plus optional/diagnostic `salinity`, `depth_m`, `current_speed`, and `current_direction`. Bait score is a deterministic scalar field derived from SST suitability, current-speed suitability, and optional depth suitability. Chlorophyll is reserved as a future booster and does not block rendering.

The provider interface is depth-ready for future 3D truth via `sample(lon, lat, depth_m, time)`. This pass begins with surface data (`depth 0` / `surface`) while preserving depth-level metadata and aliases for SST, current vectors, salinity, and depth.

Debug scripts:

- `scripts/check_rtofs_provider.py` validates `/gfs/api/providers/rtofs`.
- `scripts/check_ocean_truth.py` validates the encoded ocean field-truth patch from `/gfs/api/field-truth`.

## Morphing Renderer Lifecycle

The first renderer architecture intentionally avoids delete/redraw cycles:

1. **Snapshot:** the browser loads `/gfs/api/scene-frame` once to establish stable scene contracts.
2. **Stream:** the browser opens `/gfs/api/stream` and receives reconnect-friendly event IDs for heartbeat, atmosphere patches, ocean patches, and report patches.
3. **Field store:** incoming field patches update target state only; they do not directly redraw layers.
4. **Target state:** cloud, rain, ocean, bait, and report layers sample the latest compact field patches through capped budgets.
5. **Animation loop:** `requestAnimationFrame` ticks all animated layers.
6. **Morphing scene graph:** stable pooled DOM placeholders morph opacity, scale, footprint, altitude, and position toward the newest target values, fading unused objects instead of deleting them immediately.

Budgets are tiered as `global`, `regional`, and `local` so the renderer never creates unbounded particles or markers. Cloud placeholders sample `cloud_density` with wind advection TODO hooks from `wind_u`/`wind_v`; rain placeholders sample `rain_rate`; ocean placeholders sample `sst_c`, `current_u`/`current_v`, and `bait_score`.


## PostGIS Stable Spatial Truth

PostGIS is optional and owns stable place/world geometry only: coast and land-water masks, harbors, lakes/waterbodies, islands, spatial tiles, label anchors, simplified tier geometries, viewport intersections, and CSV report points. It must not store high-frequency GFS/RTOFS field frames.

Responsibilities remain split:

- **PostGIS = stable place truth** with spatial indexes and viewport queries.
- **GFS/RTOFS = moving field truth** for atmosphere, ocean, bait score, current, and SST fields.
- **Google `<gmp-map-3d>` = base world renderer** for terrain/buildings.
- **TypeScript renderer = morphing display layer** with object pools, field sampling, and budgets.

Safe defaults keep the app runnable without a database: `LFTR_SPATIAL_MODE=mock`, `LFTR_POSTGIS_ENABLED=false`, and no DSN required. In `hybrid` mode, viewport spatial queries use PostGIS when available and fall back to CSV/mock data without exposing the DSN.

PostGIS utilities:

- `scripts/install_postgis.sh` prints conservative Ubuntu/Debian install notes and runs migrations only when `LFTR_POSTGIS_DSN` is configured.
- `scripts/migrate_postgis.py` runs idempotent schema creation without destroying data.
- `scripts/load_reports_to_postgis.py` loads `data/reports.csv` into `spatial_reports`.
- `scripts/check_postgis.py` reports sanitized PostGIS status.
- `scripts/check_viewport_spatial.py` validates `/gfs/api/viewport-spatial`.

Admin/debug endpoints:

- `GET /gfs/api/spatial/status` returns sanitized spatial/PostGIS status.
- `POST /gfs/api/spatial/migrate` runs idempotent migrations when DB access is configured.
- `POST /gfs/api/spatial/load-reports` loads CSV reports into PostGIS.
- `GET /gfs/api/spatial/reports?bbox=minLon,minLat,maxLon,maxLat` queries report points.
- `GET /gfs/api/spatial/waterbodies?bbox=minLon,minLat,maxLon,maxLat&tier=regional` queries simplified waterbodies.

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

Returns reports, waterbodies/lakes, harbors, coast mask metadata, spatial mode, sanitized PostGIS status, geometry tier, stable IDs, and diagnostics for viewport-aware spatial truth.

### `GET /gfs/api/stream`

Streams mock SSE events:

- `scene.heartbeat`
- `atmosphere.field.patch`
- `ocean.field.patch`

### `WS /ws/gfs`

Accepts a WebSocket connection and echoes messages after an initial heartbeat placeholder.

## Checks

With the backend running:

```bash
scripts/check_health.sh
scripts/check_scene_snapshot.sh
scripts/check_gfs_provider.py
scripts/check_rtofs_provider.py
scripts/check_ocean_truth.py
scripts/check_postgis.py
scripts/check_viewport_spatial.py
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
