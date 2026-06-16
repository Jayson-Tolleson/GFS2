import hashlib
import math
import random
from app.schemas.scene import BBox
from app.services.field_truth_engine import get_field_truth_engine
from app.spatial.viewport_query import build_viewport_spatial


def _seed_for_bbox(bbox: BBox) -> int:
    bucket = f'{round(bbox.west, 1)}:{round(bbox.south, 1)}:{round(bbox.east, 1)}:{round(bbox.north, 1)}'
    return int(hashlib.sha1(bucket.encode()).hexdigest()[:8], 16)


def _mean_current(bbox: BBox) -> tuple[float, float]:
    patch, _ = get_field_truth_engine().ocean_patch(bbox)
    channels = patch.payload.get('channels', {})
    u_grid = channels.get('current_u', [[0]])
    v_grid = channels.get('current_v', [[0]])
    u_values = [float(value) for row in u_grid for value in row]
    v_values = [float(value) for row in v_grid for value in row]
    return (sum(u_values) / len(u_values), sum(v_values) / len(v_values)) if u_values and v_values else (0.0, 0.0)


def generate_viewport_boats(bbox: BBox, count: int = 12) -> dict:
    rng = random.Random(_seed_for_bbox(bbox))
    spatial = build_viewport_spatial(bbox, tier='regional')
    u, v = _mean_current(bbox)
    heading = (math.degrees(math.atan2(v, u)) + 360) % 360 if (u or v) else 0
    waterbodies = spatial.get('waterbodies', [])
    boats = []
    for index in range(count):
        if waterbodies and index < min(len(waterbodies), count // 2):
            anchor = waterbodies[index % len(waterbodies)].get('label_point', {})
            lat = float(anchor.get('lat', (bbox.south + bbox.north) / 2)) + rng.uniform(-0.01, 0.01)
            lon = float(anchor.get('lon', (bbox.west + bbox.east) / 2)) + rng.uniform(-0.01, 0.01)
            source = 'spatial_ocean_truth'
        else:
            lat = rng.uniform(bbox.south, bbox.north)
            lon = rng.uniform(bbox.west, bbox.east)
            source = 'mock'
        boats.append({'id': f'boat_{_seed_for_bbox(bbox):x}_{index:02d}', 'lat': round(lat, 6), 'lon': round(lon, 6), 'heading_deg': round((heading + rng.uniform(-20, 20)) % 360, 2), 'current_u': round(u, 3), 'current_v': round(v, 3), 'safety': 'unknown', 'safety_metadata': {'water_safe': bool(waterbodies), 'placeholder': True}, 'model': 'fallback', 'model_hook': 'future_glb'})
    return {'ok': True, 'source': 'spatial_ocean_truth' if waterbodies else 'mock', 'boats': boats, 'count': len(boats)}
