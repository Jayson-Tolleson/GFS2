from app.schemas.scene import BBox


def tile_id_for_bbox(bbox: BBox, lod: int = 0) -> str:
    return f"lod{lod}:{bbox.west:.2f},{bbox.south:.2f},{bbox.east:.2f},{bbox.north:.2f}"


def default_field_bbox() -> BBox:
    return BBox(west=-87.8, south=18.0, east=-73.0, north=32.5)
