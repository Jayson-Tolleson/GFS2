from datetime import datetime, timezone
from app.services.viewport import default_viewport


LAYER_CONTRACTS = [
    {"id": "clouds", "label": "Clouds", "kind": "field", "enabled": True},
    {"id": "rain", "label": "Rain", "kind": "field", "enabled": True},
    {"id": "ocean", "label": "Ocean", "kind": "field", "enabled": True},
    {"id": "bait", "label": "Bait", "kind": "entity", "enabled": True},
    {"id": "boats", "label": "Boats", "kind": "entity", "enabled": True},
    {"id": "inland-water", "label": "Inland Water", "kind": "field", "enabled": True},
    {"id": "lightning", "label": "Lightning", "kind": "report", "enabled": False},
    {"id": "reports", "label": "Reports", "kind": "report", "enabled": False},
]


def build_mock_scene_snapshot() -> dict:
    now = datetime.now(timezone.utc).isoformat()
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
            "clouds": {"status": "mock", "patch_count": 1},
            "rain": {"status": "mock", "patch_count": 1},
            "ocean": {"status": "mock", "patch_count": 1},
        },
    }
