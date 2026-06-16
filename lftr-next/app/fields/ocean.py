import math
from datetime import datetime, timezone
from app.fields.base import OceanFieldFrame
from app.schemas.scene import BBox

OCEAN_CHANNELS = ["sst_c", "current_u", "current_v", "bait_score", "salinity", "depth_m", "current_speed", "current_direction"]


def build_mock_ocean_frame(bbox: BBox, grid_shape: tuple[int, int] = (4, 4), depth_levels: list[str] | None = None) -> OceanFieldFrame:
    rows, cols = grid_shape
    channels: dict[str, list[list[float]]] = {}
    channels["sst_c"] = [[round(23 + (row * 0.35) + (col * 0.2), 3) for col in range(cols)] for row in range(rows)]
    channels["current_u"] = [[round(-0.4 + (col / max(cols - 1, 1)) * 0.8, 3) for col in range(cols)] for _ in range(rows)]
    channels["current_v"] = [[round(0.15 + (row / max(rows - 1, 1)) * 0.35, 3) for _ in range(cols)] for row in range(rows)]
    channels["salinity"] = [[round(35.0 + row * 0.03 - col * 0.02, 3) for col in range(cols)] for row in range(rows)]
    channels["depth_m"] = [[0.0 for _ in range(cols)] for _ in range(rows)]
    channels["bait_score"] = derive_bait_score(channels)
    frame = OceanFieldFrame(
        bbox=bbox,
        valid_time=datetime.now(timezone.utc).isoformat(),
        grid_shape=grid_shape,
        depth_levels=depth_levels or ["surface", "20m"],
        channels=channels,
        metadata={"source": "mock_ocean", "degraded": False},
    )
    enrich_ocean_diagnostics(frame)
    return frame


def derive_bait_score(channels: dict[str, list[list[float]]]) -> list[list[float]]:
    sst = channels["sst_c"]
    u = channels["current_u"]
    v = channels["current_v"]
    depth = channels.get("depth_m")
    rows, cols = len(sst), len(sst[0])
    score: list[list[float]] = []
    for row in range(rows):
        out_row: list[float] = []
        for col in range(cols):
            temp = sst[row][col]
            speed = math.hypot(u[row][col], v[row][col])
            temp_fit = max(0.0, 1.0 - abs(temp - 25.0) / 8.0)
            speed_fit = max(0.0, 1.0 - abs(speed - 0.45) / 0.9)
            depth_fit = 1.0
            if depth:
                depth_fit = max(0.0, 1.0 - abs(depth[row][col] - 20.0) / 120.0)
            # Future chlorophyll hook: multiply/boost score when a chlorophyll field is available.
            out_row.append(round(max(0.0, min(1.0, (temp_fit * 0.45) + (speed_fit * 0.4) + (depth_fit * 0.15))), 3))
        score.append(out_row)
    return score


def enrich_ocean_diagnostics(frame: OceanFieldFrame) -> None:
    u = frame.channels["current_u"]
    v = frame.channels["current_v"]
    rows, cols = len(u), len(u[0])
    frame.channels["current_speed"] = [[round(math.hypot(u[row][col], v[row][col]), 3) for col in range(cols)] for row in range(rows)]
    frame.channels["current_direction"] = [[round(math.degrees(math.atan2(v[row][col], u[row][col])), 3) for col in range(cols)] for row in range(rows)]
