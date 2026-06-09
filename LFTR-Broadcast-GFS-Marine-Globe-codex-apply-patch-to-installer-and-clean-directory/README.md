# LFTR Broadcast / GFS Marine Globe

This installer contains the LFTR Quart app for `/`, `/broadcast`, `/watch`, and `/gfs`.
The `/gfs` page is the Google Maps Photorealistic 3D marine globe. `/broadcast` and `/watch` are retained as first-class routes/assets.

## What stays in this package

- `static/indexgfs.html` and `static/js/gfs/` for the `/gfs` marine/weather globe.
- `static/broadcast.html`, `static/js/broadcast.js`, `static/watch.html`, and `static/js/watch.js` for broadcast/watch.
- `server/` for the Quart app, broadcast routes, GFS routes, and provider/cache code.
- `static/data/fishloclist.csv` for local fishing locations.
- `deploy/`, `broadcast.sh`, and `install.sh` for installation.
- `scripts/` only for runtime/build/repair helpers; diagnostic/check scripts were intentionally removed.


## Source-only PR policy

This repository intentionally tracks the expanded installer source tree, not the binary zip bundle. GitHub PR review cannot show binary archive diffs cleanly, so `*.zip`, `*.glb`, `*.gltf`, and `*.bin` are ignored at the repo root. If a local zip is needed for handoff, rebuild it outside the PR with:

```bash
zip -qr LFTR-Broadcast-GFS-Marine-Globe-current-field-bridge-patch.zip LFTR-Broadcast-GFS-Marine-Globe-codex-apply-patch-to-installer-and-clean-directory
```

No `.glb` model is required by the current app package; the Google Photorealistic 3D globe is loaded through the Maps 3D API and the app-native HTML/JS/CSS assets in `static/`.

## /gfs core contract

`/gfs` is cache-first and tile-bounded:

```text
viewport bbox
→ /gfs/api/scene-frame or /gfs/api/scene-cache
→ split visible bbox into provider tiles
→ read existing cache first
→ fetch only missing/expired tile provider URLs
→ validate finite/useful data
→ promote improved ready tiles only
→ renderer draws selected pill layers
```

The shared contract is exposed by `/gfs/api/core-contract` and embedded in scene-frame/debug responses.
It declares:

- `/gfs` scope only; broadcast/watch are separate and retained.
- 24x24 default viewport tile grid.
- Three LOD levels: `global`, `regional`, and `local`.
- Provider families: NCSS GFS, RTOFS, HYCOM, inland geometry, lake environment, USGS flow, and shoreline.
- Update policy: viewport change or 2-minute full cache TTL.
- Lightning policy: current-frame GLM-style flashes expire after 5 minutes.
- Pill-off policy: hide/clear renderer visuals without starting provider network calls.

## Layers

- **Locations** load once from `static/data/fishloclist.csv`.
- **Clouds** render NCSS/GFS cloud-fraction contours as extruded shell polygons. The renderer targets up to 500 shells and keeps only 20-50 soft ellipse particles for jitter/wobble/advection. Party mode keeps cloud glow outlines.
- **Rain** renders precipitation from cache/provider payloads without clearing clouds.
- **Lightning** renders short-lived event particles/markers and expires them independently.
- **Jetstream** uses u/v wind near the requested layer to render a small set of mph balloons.
- **Bait** and **shark-intel** use ocean/lake data, HYCOM/current fields, and marching-square style contours where available.
- **Inland water** renders raw lake/shore vertices and attaches temperature/bait detail only past global overview zoom.
- **Boater** keeps the existing boater awareness layer.

## Install and run

```bash
bash broadcast.sh
# or
bash install.sh
# or
bash deploy/install.sh
```

The service runner is:

```bash
scripts/run_broadcast_service.sh
```

Useful service commands:

```bash
sudo systemctl daemon-reload
sudo systemctl restart broadcast.service
sudo systemctl status broadcast.service --no-pager
journalctl -u broadcast.service -n 200 --no-pager
```

## Runtime helper scripts kept

The remaining `scripts/` files are build/repair/runtime helpers, not diagnostics:

- NHD/inland cache builders: `build_nhdplus_hr_tiles.py`, `fetch_nhd_arcgis_bbox.py`, `install_nhdplus_hr_view_cache.sh`.
- Runtime and service helpers: `run_broadcast_service.sh`, `run_hypercorn_single.py`, `repair_broadcast_service.sh`.
- Cache/permission repair helpers: `clear_gfs_runtime_cache.sh`, `fix_runtime_cache_permissions.sh`, `fix_runtime_permissions_and_cache.sh`, `fix_runner_workdir.sh`, `fix_hycom_provider_import.sh`.

## Minimal validation

```bash
python3 -m py_compile server/gfs/tile_contract.py server/gfs/pipeline.py server/gfs/routes.py server/gfs_service.py server/gfs_service_parts/lightning_cache_media.py
node --check static/js/gfs/cloud-zones.js
node --check static/js/gfs/lightning-zones.js
bash -n broadcast.sh install.sh deploy/install.sh scripts/*.sh
```

## Key environment knobs

```bash
GFS_CORE_CACHE_REFRESH_SECONDS=120
GFS_SCENE_CACHE_REFRESH_MS=120000
GFS_GLM_CACHE_TTL_SECONDS=300
GFS_LIGHTNING_CACHE_REFRESH_SECONDS=300
GFS_VIEWPORT_TILE_GRID=24
GFS_MAX_CLOUD_PARTICLES_DESKTOP=50
GFS_MAX_CLOUD_PARTICLES_MOBILE=35
GFS_CLOUD_MAX_REGIONS=500
INLAND_WATER_CACHE_RETENTION_DAYS=60
```
