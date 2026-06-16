import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncIterator
from app.core.config import get_settings
from app.fields.tiles import default_field_bbox
from app.providers.csv_reports import reports_for_bbox
from app.providers.mock_atmosphere import next_atmosphere_patch
from app.providers.mock_ocean import next_ocean_patch

MOCK_EVENTS = ["scene.heartbeat", "atmosphere.field.patch", "ocean.field.patch", "reports.patch"]


def sse_message(event: str, event_id: int, payload: dict) -> str:
    return f"event: {event}\nid: {event_id}\ndata: {json.dumps(payload)}\n\n"


async def mock_sse_events() -> AsyncIterator[str]:
    settings = get_settings()
    delay = 1 / max(settings.mock_stream_fps, 0.1)
    bbox = default_field_bbox()
    counter = 0
    while True:
        event = MOCK_EVENTS[counter % len(MOCK_EVENTS)]
        if event == "atmosphere.field.patch":
            payload = next_atmosphere_patch(bbox).model_dump(mode="json")
        elif event == "ocean.field.patch":
            payload = next_ocean_patch(bbox).model_dump(mode="json")
        elif event == "reports.patch":
            payload = {"reports": [report.model_dump() for report in reports_for_bbox(bbox)]}
        else:
            payload = {
                "ok": True,
                "sequence": counter,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "mock_stream_fps": settings.mock_stream_fps,
                "future_target_fps": settings.target_stream_fps,
                "message": "mock field-truth stream; NOAA/RTOFS/PostGIS ingestion is TODO",
            }
        yield sse_message(event, counter, payload)
        counter += 1
        await asyncio.sleep(delay)
