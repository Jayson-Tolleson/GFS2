from fastapi import APIRouter, HTTPException, Query
from app.providers.gfs_ncss import get_gfs_provider
from app.services.field_truth_engine import get_field_truth_engine
from app.spatial.viewport_query import parse_bbox

router = APIRouter(prefix="/gfs/api", tags=["providers"])


def bbox_from_query(bbox: str):
    try:
        return parse_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/providers/status")
def provider_status() -> dict:
    gfs = get_gfs_provider().status()
    return {"ok": True, "provider_mode": gfs.mode, "providers": {"gfs": gfs.model_dump(mode="json")}}


@router.get("/providers/gfs")
def provider_gfs(bbox: str = Query(..., description="minLon,minLat,maxLon,maxLat")) -> dict:
    frame, status = get_gfs_provider().fetch_atmosphere(bbox_from_query(bbox))
    return {"ok": True, "status": status.model_dump(mode="json"), "frame": frame.model_dump(mode="json")}


@router.get("/field-truth")
def field_truth(bbox: str = Query(..., description="minLon,minLat,maxLon,maxLat")) -> dict:
    patch, status = get_field_truth_engine().atmosphere_patch(bbox_from_query(bbox))
    return {"ok": True, "status": status.model_dump(mode="json"), "patch": patch.model_dump(mode="json")}
