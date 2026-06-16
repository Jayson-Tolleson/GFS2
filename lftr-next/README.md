# LFTR Next

LFTR Next is a clean, runnable architecture checkpoint for the next-generation LFTR Marine Intelligence Globe. Google renders the base world, optional PostGIS contracts own stable place truth, GFS/RTOFS provider adapters define moving field-truth inputs, and TypeScript morphs visuals from streamed field patches. The GFS/RTOFS live paths are probe/stub adapters with cache/mock fallback until real bounded NetCDF/NCSS/NOMADS parsing is implemented.


## LFTR Next 1–6 Checkpoint Status

Complete in this checkpoint:

- Clean FastAPI app spine with health, scene snapshot, SSE stream, WebSocket, provider status, and spatial routes.
- TypeScript/Vite renderer shell with Google `<gmp-map-3d>` placeholder, field store, object pools, animation loop, and morphing layer placeholders.
- GFS atmosphere provider adapter contract with live probe/stub, last-good cache path, and mock fallback.
- RTOFS ocean provider adapter contract with live probe/stub, last-good cache path, depth-ready interface, and mock fallback.
- Optional PostGIS schema/migration/viewport-spatial contract for stable place truth.

Adapter/stub, not finished production parsing:

- Live GFS NCSS NetCDF parsing is TODO. Current live path only probes reachability and returns mock-shaped field frames with explicit `live_stub`/`probe` metadata.
- Live RTOFS NOMADS NetCDF parsing is TODO. Current live path only probes availability and returns mock-shaped field frames with explicit `live_stub`/`probe` metadata.
- Chlorophyll/ocean-color provider is documented as a disabled future booster for bait score.

Next pass #7 should add USGS/NHD lake ingest into PostGIS spatial truth. Do not add boats, lightning, broadcast/watch migration, or production NOAA/RTOFS parsers in this checkpoint.

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



## Provider Catalog

The provider catalog is available in code at `app/providers/catalog.py`, in docs at `docs/providers.md`, and at runtime via `GET /gfs/api/providers/catalog`. Runtime config values are authoritative; documented URLs are templates/examples for future parser work.

### GFS NCSS Atmosphere

`gfs_ncss_atmosphere` is the moving atmosphere field-truth adapter for clouds, rain, wind, humidity, temperature, and pressure. It documents NCSS query parameters (`var`, `north`, `south`, `east`, `west`, `time=present`, `accept=netcdf4`, `addLatLon=true`), expected GFS variables, normalized LFTR channels, units, and parser TODOs. Current live behavior is a probe/stub with mock fallback, not real parsed NetCDF field truth.

### RTOFS/NOMADS Ocean

`rtofs_ncep_ocean` is the moving ocean field-truth adapter for SST, current vectors, salinity/depth metadata, and derived bait score. It documents NOMADS source templates, product files, aliases, normalized ocean channels, depth levels, and the future `sample(lon, lat, depth_m, time)` interface. Current live behavior is a probe/stub with mock fallback, not real parsed RTOFS NetCDF field truth.

### Chlorophyll / Ocean Color Future Booster

`chlorophyll_ocean_color` is disabled by default. It documents NOAA CoastWatch ERDDAP and NASA OceanColor source families and possible chlorophyll aliases. Chlorophyll can boost or shape `bait_score` later, but it must never block ocean rendering; if missing, bait score still derives from SST/current/depth.

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

Use `scripts/check_gfs_provider.py` and `scripts/check_provider_catalog.py` to validate mock/hybrid provider behavior and provider catalog honesty.


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



## Visual Layer Contracts (#8)

Pass #8 adds clean visual layer contracts and first lightweight adapters over existing truth systems. Clouds/rain sample atmosphere fields; ocean/current sample ocean fields; bait is a bounded scalar-field glow from `bait_score`; boats are stable viewport entities generated from viewport/spatial/ocean-current truth; lightning is a short-lived TTL event layer; inland water consumes stable USGS/PostGIS waterbody IDs and labels; reports remain CSV/PostGIS spatial points.

The renderer flow remains `snapshot → stream → field store → target state → animation loop → morphing object pools`. This pass does not add broadcast/watch, WebRTC, STT, AI chat, full NOAA/RTOFS parsers, or giant legacy frontend code.

Layer endpoints:

- `GET /gfs/api/layers/status` returns layer contracts, budgets, provider/spatial status, and renderer expectations.
- `GET /gfs/api/layers/boats?bbox=minLon,minLat,maxLon,maxLat` returns deterministic stable viewport boats.
- `GET /gfs/api/layers/lightning?bbox=minLon,minLat,maxLon,maxLat` returns TTL mock/GLM-style flashes.
- `GET /gfs/api/layers/bait?bbox=minLon,minLat,maxLon,maxLat` summarizes field-derived bait score metadata.

## USGS Hydrography / Inland Water Pass #7

Pass #7 adds stable inland-water geometry only. USGS 3DHP/current hydrography should be preferred when configured, while NHDPlus HR and NHD are legacy/reference source families. Supported source adapters are `3dhp`, `nhdplus_hr`, `nhd`, `arcgis_rest`, `geojson`, `shapefile_zip`, and `mock`.

The ingest normalizes source features into LFTR waterbody objects with stable IDs, source metadata, kind, area, geometry, label point, bbox, properties, and ingest batch ID. PostGIS is optional but recommended for durable stable spatial truth; mock and GeoJSON modes run without network or PostGIS.

This pass does **not** add live lake temperature, inland bait scoring, boats, lightning, or a new renderer. Waterbody geometry persists independently of GFS/RTOFS weather and ocean fields.

USGS endpoints and scripts:

- `GET /gfs/api/spatial/usgs/status` reports sanitized config and cache/PostGIS availability.
- `POST /gfs/api/spatial/usgs/ingest?bbox=minLon,minLat,maxLon,maxLat` runs configured ingest for a bbox.
- `GET /gfs/api/spatial/waterbodies?bbox=minLon,minLat,maxLon,maxLat&tier=regional` returns PostGIS or mock/cache waterbodies.
- `scripts/ingest_usgs_waterbodies.py`, `scripts/check_usgs_ingest.py`, `scripts/check_waterbody_viewport.py`, and `scripts/check_postgis_waterbodies.py` support local checks.

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
scripts/check_provider_catalog.py
scripts/check_pre7_checkpoint.sh
scripts/check_usgs_ingest.py
scripts/check_waterbody_viewport.py
scripts/check_postgis_waterbodies.py
scripts/check_layers.py
scripts/check_bait_boats_lightning.py
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

- Implement real bounded GFS NCSS NetCDF parsing behind the existing adapter.
- Implement real bounded RTOFS NOMADS NetCDF parsing behind the existing adapter.
- Pass #7: USGS/3DHP/NHD/NHDPlus stable inland-water geometry ingest is now scaffolded; future work should add production source configs and richer validation.
- Keep chlorophyll as a future optional bait-score booster until a dataset is selected.
- Replace placeholder layer modules with efficient globe-native rendering.
