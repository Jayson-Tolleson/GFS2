from fastapi import APIRouter, HTTPException, Query
from app.layers.compiler import layer_status
from app.services.bait_field import bait_field_summary
from app.services.boat_generator import generate_viewport_boats
from app.services.lightning_service import lightning_flashes
from app.spatial.viewport_query import parse_bbox

router = APIRouter(prefix='/gfs/api/layers', tags=['layers'])


def bbox_from_query(bbox: str):
    try:
        return parse_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get('/status')
def status() -> dict:
    return layer_status()


@router.get('/boats')
def boats(bbox: str = Query(..., description='minLon,minLat,maxLon,maxLat')) -> dict:
    return generate_viewport_boats(bbox_from_query(bbox))


@router.get('/lightning')
def lightning(bbox: str = Query(..., description='minLon,minLat,maxLon,maxLat')) -> dict:
    return lightning_flashes(bbox_from_query(bbox))


@router.get('/bait')
def bait(bbox: str = Query(..., description='minLon,minLat,maxLon,maxLat'), threshold: float = Query(0.55)) -> dict:
    return bait_field_summary(bbox_from_query(bbox), threshold=threshold)
