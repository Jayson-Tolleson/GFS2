import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from app.services.stream_bus import mock_sse_events

router = APIRouter(tags=["stream"])


@router.get("/gfs/api/stream")
def stream() -> StreamingResponse:
    return StreamingResponse(mock_sse_events(), media_type="text/event-stream")


@router.websocket("/ws/gfs")
async def websocket_gfs(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        await websocket.send_json({"event": "scene.heartbeat", "ok": True, "transport": "websocket"})
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(json.dumps({"event": "echo", "data": message}))
    except WebSocketDisconnect:
        return
