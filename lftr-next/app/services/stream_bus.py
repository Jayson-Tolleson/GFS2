import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncIterator
from app.core.config import get_settings
from app.fields.tiles import default_field_bbox
from app.services.field_truth_engine import get_field_truth_engine

MOCK_EVENTS = ["scene.heartbeat", "atmosphere.field.patch", "ocean.field.patch"]


def sse_message(event: str, event_id: int, payload: dict) -> str:
    return f"event: {event}\nid: {event_id}\ndata: {json.dumps(payload)}\n\n"


async def mock_sse_events() -> AsyncIterator[str]:
    settings = get_settings()
    delay = 1 / max(settings.mock_stream_fps, 0.1)
    bbox = default_field_bbox()
    counter = 0
    engine = get_field_truth_engine()
    while True:
        event = MOCK_EVENTS[counter % len(MOCK_EVENTS)]
        if event == "atmosphere.field.patch":
            patch, _ = engine.atmosphere_patch(bbox)
            payload = patch.model_dump(mode="json")
        elif event == "ocean.field.patch":
            patch, _ = engine.ocean_patch(bbox)
            payload = patch.model_dump(mode="json")
        else:
            payload = {
                "ok": True,
                "sequence": counter,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "provider_mode": settings.provider_mode,
                "mock_stream_fps": settings.mock_stream_fps,
                "future_target_fps": settings.target_stream_fps,
                "message": "heartbeat: field-truth stream alive; renderer morphs patches client-side",
            }
        yield sse_message(event, counter, payload)
        counter += 1
        await asyncio.sleep(delay)
