from app.schemas.scene import BBox


def postgis_status(enabled: bool, dsn: str | None) -> dict:
    return {"enabled": enabled, "configured": bool(dsn), "status": "placeholder" if enabled else "disabled"}


async def query_postgis_viewport(_: BBox) -> dict:
    # TODO: connect to PostGIS and query stable place truth by viewport bbox.
    # This intentionally does not import asyncpg/psycopg so PostGIS is optional for the mock app.
    return {"reports": [], "lakes": [], "harbors": [], "coast_mask": {}}
