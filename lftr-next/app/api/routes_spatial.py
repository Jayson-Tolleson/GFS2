from fastapi import APIRouter, HTTPException, Query
from app.spatial.viewport_query import build_viewport_spatial, parse_bbox, query_reports

router = APIRouter(prefix="/gfs/api", tags=["spatial"])


def bbox_from_query(bbox: str):
    try:
        return parse_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/reports")
def reports(bbox: str = Query(..., description="minLon,minLat,maxLon,maxLat")) -> dict:
    parsed = bbox_from_query(bbox)
    return {"ok": True, "bbox": parsed.model_dump(), "reports": [report.model_dump() for report in query_reports(parsed)]}


@router.get("/viewport-spatial")
def viewport_spatial(
    bbox: str = Query(..., description="minLon,minLat,maxLon,maxLat"),
    tier: str = Query("regional"),
):
    return build_viewport_spatial(bbox_from_query(bbox), tier=tier)
