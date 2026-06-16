from datetime import datetime, timezone
from app.fields.base import AtmosphereFieldFrame
from app.schemas.scene import BBox

ATMOSPHERE_CHANNELS = ["cloud_density", "rain_rate", "wind_u", "wind_v", "humidity"]


def build_mock_atmosphere_frame(bbox: BBox, grid_shape: tuple[int, int] = (4, 4)) -> AtmosphereFieldFrame:
    rows, cols = grid_shape
    channels = {}
    for index, name in enumerate(ATMOSPHERE_CHANNELS):
        channels[name] = [[round((row + col + index) / 10, 3) for col in range(cols)] for row in range(rows)]
    return AtmosphereFieldFrame(
        bbox=bbox,
        valid_time=datetime.now(timezone.utc).isoformat(),
        grid_shape=grid_shape,
        levels=["surface", "850mb"],
        channels=channels,
    )
