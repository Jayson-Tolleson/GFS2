from typing import Literal
from pydantic import BaseModel
from app.schemas.scene import BBox


class ReportPoint(BaseModel):
    id: str
    kind: Literal["report"] = "report"
    title: str
    latitude: float
    longitude: float
    observed_at: str
    summary: str
    source: str = "csv"


class SpatialFeature(BaseModel):
    id: str
    kind: str
    label: str
    latitude: float | None = None
    longitude: float | None = None
    metadata: dict = {}


class ViewportSpatialResponse(BaseModel):
    ok: bool
    bbox: BBox
    tier: str
    reports: list[ReportPoint]
    lakes: list[SpatialFeature]
    harbors: list[SpatialFeature]
    coast_mask: dict
    postgis: dict
