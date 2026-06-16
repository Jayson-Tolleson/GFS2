from datetime import datetime, timezone
from app.fields.base import OceanFieldFrame
from app.schemas.scene import BBox

OCEAN_CHANNELS = ["sst_c", "current_u", "current_v", "bait_score"]


def build_mock_ocean_frame(bbox: BBox, grid_shape: tuple[int, int] = (4, 4)) -> OceanFieldFrame:
    rows, cols = grid_shape
    channels = {}
    for index, name in enumerate(OCEAN_CHANNELS):
        channels[name] = [[round(20 + index + (row * 0.2) + (col * 0.1), 3) for col in range(cols)] for row in range(rows)]
    channels["bait_score"] = [[round(min(1, (row + col + 1) / (rows + cols)), 3) for col in range(cols)] for row in range(rows)]
    return OceanFieldFrame(
        bbox=bbox,
        valid_time=datetime.now(timezone.utc).isoformat(),
        grid_shape=grid_shape,
        depth_levels=["surface", "20m"],
        channels=channels,
    )
