from pathlib import Path
from app.core.config import get_settings
from app.schemas.scene import BBox
from app.spatial.base import SpatialFeature, ViewportSpatialResponse
from app.spatial.csv_reports import filter_reports_by_bbox, load_reports
from app.spatial.postgis_optional import postgis_status


def parse_bbox(value: str) -> BBox:
    parts = [float(part.strip()) for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox must be minLon,minLat,maxLon,maxLat")
    return BBox(west=parts[0], south=parts[1], east=parts[2], north=parts[3])


def reports_csv_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "reports.csv"


def query_reports(bbox: BBox):
    return filter_reports_by_bbox(load_reports(reports_csv_path()), bbox)


def mock_lakes() -> list[SpatialFeature]:
    return [SpatialFeature(id="lake-okeechobee", kind="lake", label="Lake Okeechobee", latitude=26.94, longitude=-80.80)]


def mock_harbors() -> list[SpatialFeature]:
    return [
        SpatialFeature(id="harbor-port-everglades", kind="harbor", label="Port Everglades", latitude=26.091, longitude=-80.116),
        SpatialFeature(id="harbor-miami", kind="harbor", label="PortMiami", latitude=25.778, longitude=-80.170),
    ]


def build_viewport_spatial(bbox: BBox, tier: str = "regional") -> ViewportSpatialResponse:
    settings = get_settings()
    return ViewportSpatialResponse(
        ok=True,
        bbox=bbox,
        tier=tier,
        reports=query_reports(bbox),
        lakes=mock_lakes(),
        harbors=mock_harbors(),
        coast_mask={"id": f"coast-mask-{tier}", "status": "mock", "bbox": bbox.model_dump()},
        postgis=postgis_status(settings.postgis_enabled, settings.postgis_dsn),
    )
