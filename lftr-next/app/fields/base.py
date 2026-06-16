from typing import Any, Literal
from pydantic import BaseModel
from app.schemas.scene import BBox


class AtmosphereFieldFrame(BaseModel):
    bbox: BBox
    valid_time: str
    grid_shape: tuple[int, int]
    levels: list[str]
    channels: dict[Literal["cloud_density", "rain_rate", "wind_u", "wind_v", "humidity"], list[list[float]]]


class OceanFieldFrame(BaseModel):
    bbox: BBox
    valid_time: str
    grid_shape: tuple[int, int]
    depth_levels: list[str]
    channels: dict[Literal["sst_c", "current_u", "current_v", "bait_score"], list[list[float]]]


class FieldPatch(BaseModel):
    patch_id: str
    field_type: Literal["atmosphere", "ocean"]
    tile_id: str
    bbox: BBox
    lod: int
    channels: list[str]
    encoding: Literal["json-grid"] = "json-grid"
    payload: dict[str, Any]
