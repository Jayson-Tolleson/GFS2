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


def _postgis_response(bbox: BBox, tier: str):
    from app.spatial.postgis_repository import PostGISSpatialRepository
    repo = PostGISSpatialRepository()
    if not repo.available():
        return None
    try:
        reports = repo.query_reports(bbox)
        waterbodies = repo.query_waterbodies(bbox, tier)
        harbors = repo.query_harbors(bbox)
        coast_mask = repo.query_coast_mask(bbox, tier) or {"id": f"coast-mask-{tier}", "status": "postgis-empty"}
        status = repo.status()
        return {
            "ok": True,
            "bbox": bbox.model_dump(),
            "tier": tier,
            "geometry_tier": tier,
            "spatial_mode": "postgis",
            "reports": reports,
            "lakes": waterbodies,
            "waterbodies": waterbodies,
            "harbors": harbors,
            "coast_mask": coast_mask,
            "postgis": {k: v for k, v in status.items() if k != "dsn"},
            "diagnostics": {"source": "postgis", "fallback": False},
        }
    except Exception as exc:
        if get_settings().spatial_mode == "postgis":
            raise
        return {"error": str(exc)}


def build_viewport_spatial(bbox: BBox, tier: str = "regional"):
    settings = get_settings()
    if settings.spatial_mode in {"postgis", "hybrid"}:
        postgis_payload = _postgis_response(bbox, tier)
        if postgis_payload and "error" not in postgis_payload:
            return postgis_payload
    status = postgis_status(settings.postgis_enabled, settings.postgis_dsn)
    return {
        "ok": True,
        "bbox": bbox.model_dump(),
        "tier": tier,
        "geometry_tier": tier,
        "spatial_mode": "mock" if settings.spatial_mode != "postgis" else "mock-fallback",
        "reports": [report.model_dump() for report in query_reports(bbox)],
        "lakes": [lake.model_dump() for lake in mock_lakes()],
        "waterbodies": [lake.model_dump() for lake in mock_lakes()],
        "harbors": [harbor.model_dump() for harbor in mock_harbors()],
        "coast_mask": {"id": f"coast-mask-{tier}", "status": "mock", "bbox": bbox.model_dump()},
        "postgis": status,
        "diagnostics": {"source": "mock_csv", "fallback": True},
    }
