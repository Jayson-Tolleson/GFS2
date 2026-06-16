from datetime import datetime, timezone
from app.services.viewport import default_viewport
from app.fields.tiles import default_field_bbox
from app.providers.gfs_ncss import get_gfs_provider
from app.providers.rtofs_ncep import get_rtofs_provider


LAYER_CONTRACTS = [
    {"id": "clouds", "label": "Clouds", "kind": "field", "enabled": True},
    {"id": "rain", "label": "Rain", "kind": "field", "enabled": True},
    {"id": "ocean", "label": "Ocean", "kind": "field", "enabled": True},
    {"id": "bait", "label": "Bait", "kind": "field", "enabled": True},
    {"id": "boats", "label": "Boats", "kind": "entity", "enabled": True},
    {"id": "inland-water", "label": "Inland Water", "kind": "field", "enabled": True},
    {"id": "lightning", "label": "Lightning", "kind": "report", "enabled": False},
    {"id": "reports", "label": "Reports", "kind": "report", "enabled": False},
]


def build_mock_scene_snapshot() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    _, gfs_status = get_gfs_provider().fetch_atmosphere(default_field_bbox())
    _, rtofs_status = get_rtofs_provider().fetch_ocean(default_field_bbox())
    atmosphere_source = {
        "source": gfs_status.details.get("source", "mock:gfs_ncss"),
        "mode": gfs_status.mode,
        "live_ok": gfs_status.live_ok,
        "cache_hit": gfs_status.cache_hit,
        "degraded": gfs_status.degraded,
        "valid_time": gfs_status.valid_time,
        "error": gfs_status.error,
    }
    ocean_source = {
        "source": rtofs_status.details.get("source", "mock:rtofs_ncep"),
        "mode": rtofs_status.mode,
        "live_ok": rtofs_status.live_ok,
        "cache_hit": rtofs_status.cache_hit,
        "degraded": rtofs_status.degraded,
        "valid_time": rtofs_status.valid_time,
        "depth_levels": rtofs_status.details.get("depth_levels", []),
        "error": rtofs_status.error,
    }
    return {
        "ok": True,
        "scene_id": f"mock-scene-{now}",
        "generated_at": now,
        "bbox": {"west": -87.8, "south": 18.0, "east": -73.0, "north": 32.5},
        "viewport": default_viewport(),
        "layers": LAYER_CONTRACTS,
        "spatial": {
            "projection": "WGS84",
            "postgis": {"status": "placeholder", "todo": "wire place-aware spatial queries"},
            "objects": [
                {"id": "mock-port-everglades", "type": "harbor", "lat": 26.091, "lon": -80.116},
                {"id": "mock-gulf-stream", "type": "current-axis", "lat": 26.4, "lon": -79.6},
            ],
        },
        "fields": {
            "clouds": {"status": "provider", "patch_count": 1, "atmosphere_provider": atmosphere_source},
            "rain": {"status": "mock", "patch_count": 1},
            "ocean": {"status": "provider", "patch_count": 1, "ocean_provider": ocean_source},
            "atmosphere_provider": atmosphere_source,
            "ocean_provider": ocean_source,
        },
    }
