from fastapi import APIRouter, HTTPException, Query
from app.db.migrations import run_migrations
from app.spatial.postgis_repository import PostGISSpatialRepository
from app.spatial.viewport_query import parse_bbox

router = APIRouter(prefix="/gfs/api/spatial", tags=["spatial-admin"])


def bbox_from_query(bbox: str):
    try:
        return parse_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/status")
def spatial_status() -> dict:
    repo = PostGISSpatialRepository()
    status = repo.status()
    return {"ok": True, "postgis": status, "dsn_exposed": False}


@router.post("/migrate")
def migrate_spatial() -> dict:
    try:
        return run_migrations()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/load-reports")
def load_reports() -> dict:
    try:
        return PostGISSpatialRepository().load_reports_csv()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/reports")
def spatial_reports(bbox: str = Query(..., description="minLon,minLat,maxLon,maxLat")) -> dict:
    parsed = bbox_from_query(bbox)
    repo = PostGISSpatialRepository()
    if not repo.available():
        raise HTTPException(status_code=503, detail="PostGIS unavailable or disabled")
    return {"ok": True, "reports": repo.query_reports(parsed)}


@router.get("/waterbodies")
def spatial_waterbodies(
    bbox: str = Query(..., description="minLon,minLat,maxLon,maxLat"),
    tier: str = Query("regional"),
) -> dict:
    parsed = bbox_from_query(bbox)
    repo = PostGISSpatialRepository()
    if not repo.available():
        raise HTTPException(status_code=503, detail="PostGIS unavailable or disabled")
    return {"ok": True, "tier": tier, "waterbodies": repo.query_waterbodies(parsed, tier)}
